Chafon RFID reader
==================

This project provides a script which can be used to connect to a Chafon RFID reader
via TCP/IP or serial and upload the times recorded to a Google Sheet.

Installation
------------

Install Google client and pyserial libs via `pip`

    pip install --upgrade google-api-python-client oauth2client pyserial

Follow the steps in the [Google Sheets API Python
Quickstart](https://developers.google.com/sheets/api/quickstart/python),
to allow times to be added to a spreadsheet (optional)

Usage
-----

To keep attempting to read tags continuously until Ctrl-C is pressed, run
`continuous-read.py` providing the IP of the reader and optionally the ID of the 
Google Sheet

    python continuous-read.py 192.168.1.190 [spreadsheet_id]

A second script `single-read.py` shows how to connect to different types of Chafon 
reader via serial or TCP/IP and obtain information about the reader as well as to 
perform a read.

License
-------

This code is based on work of [Will Abson](https://github.com/wabson)
in [Chafon RFID Repository](https://github.com/wabson/chafon-rfid).
License is not specified, but I assume an Open Source License. My
contributions are published under BSD 3-Clause License if original license allows.
