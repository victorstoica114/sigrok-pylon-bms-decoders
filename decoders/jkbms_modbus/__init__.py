'''
JKBMS RS485 Modbus protocol decoder.

Stack above the UART decoder. Use 115200 8N1 for JK app profile
001 - JK BMS RS485 Modbus V1.0, or 9600 8N1 for profile 013.
'''

from .pd import Decoder
