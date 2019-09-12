#!/usr/bin/env python

import binascii
import socket
import string
import time
import sys
import mysql.connector
import sqlite3

from datetime import datetime

from reader.base import ReaderCommand
from reader.command import G2_TAG_INVENTORY
from reader.transport import TcpTransport
from reader.uhfreader18 import G2InventoryResponseFrame
from reader.uhfreader288m import G2InventoryCommand, G2InventoryResponseFrame as G2InventoryResponseFrame288
from sheets import GoogleSheetAppender

TCP_PORT = 27011


mydb = mysql.connector.connect(
  host="192.168.1.230",
  user="rfidusr",
  passwd="rfidpsw",
  database='rfid',
)

mycursor = mydb.cursor()

def insert_into_Maria(tag, time):
    sql = "INSERT INTO tags (tag, time) VALUES (%s, %s)"
    val = (tag, time)
    mycursor.execute(sql, val)

    mydb.commit()

    #print(mycursor.rowcount, "record inserted.")


sqlitedb = sqlite3.connect('rfid.db')
sqlitecursor = sqlitedb.cursor()

def insert_into_sqlite(tag, time):
    sql = "INSERT INTO tags (tag, time) VALUES (?, ?)"
    val = (tag, time)
    sqlitecursor.execute(sql, val)

    sqlitedb.commit()

    #print(mycursor.rowcount, "record inserted.")

valid_chars = string.digits + string.ascii_letters

def is_marathon_tag(tag):
    tag_data = tag.epc
    return True
    #return len(tag_data) == 4 and all([ chr(tag_byte) in valid_chars for tag_byte in tag_data.lstrip('\0') ])

def read_tags(reader_addr, appender):

    get_inventory_288 = G2InventoryCommand(q_value=1)
    get_inventory_uhfreader18 = ReaderCommand(G2_TAG_INVENTORY)
    transport = TcpTransport(reader_addr=reader_addr, reader_port=TCP_PORT, auto_connect=True)
    running = True
    while running:
        start = time.time()
        try:
            now = datetime.now().time()
            transport.write(get_inventory_288.serialize())
            #transport.write(get_inventory_uhfreader18.serialize())
            #resp = G2InventoryResponseFrame(transport.read_frame())
            resp = G2InventoryResponseFrame288(transport.read_frame())
            for tag in resp.get_tag():
                if (is_marathon_tag(tag)):
                    #boat_num = str(tag.epc.lstrip('\0'))
                    boat_num = binascii.hexlify(tag.epc)
                    boat_time = str(now)[:12]
                    print '{0} {1}'.format(boat_num, boat_time)
                    try:
                        insert_into_Maria(boat_num, boat_time)
                    except:
                        print("An exception occurred while talking to Maria")
                    try:
                        insert_into_sqlite(boat_num, boat_time)
                    except:
                        print("An exception occurred while talking to SQLite")

                    if appender is not None:
                        appender.add_row([ boat_num, boat_time, '', '' ])
                else:
                    print "Non-marathon tag 0x%s" % (binascii.hexlify(tag.epc))
            #print "received %s tags" % (resp.num_tags)
        except KeyboardInterrupt:
            running = False
            mycursor.close()
            mydb.close()
            sqlitedb.close()
            print "KeyboardInterrupt"
        except socket.error as err:
            print 'Unable to connect to reader'
            continue
        end = time.time()
        #s.close()
        #print "elapsed time %.2f" % (end - start)
        try:
            time.sleep(0.05)
        except KeyboardInterrupt:
            running = False
            transport.close()
            mycursor.close()
            mydb.close()
            sqlitedb.close()
            print "KeyboardInterrupt"

if __name__ == "__main__":

    if len(sys.argv) >= 2:

        appender_thread = None
        if len(sys.argv) >= 3:
            appender_thread = GoogleSheetAppender(sys.argv[2])
            appender_thread.start()

        read_tags(sys.argv[1], appender_thread)

        if appender_thread is not None:
            appender_thread.running = False
            appender_thread.join()
    else:
        print 'Usage: {0} <reader-ip> [<spreadsheet-id>]'.format(sys.argv[0])
