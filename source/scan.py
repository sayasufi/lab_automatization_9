import socket

import pyvisa


def scan_instr(instr_name: str):
    rm = pyvisa.ResourceManager()
    for i in range(100, 255):
        ip = f"192.168.1.{i}"
        try:
            socket.inet_aton(ip)
            try:
                instrument = rm.open_resource(f"TCPIP::{ip}::INSTR")
                idn_response = instrument.query("*IDN?")
                if instr_name in idn_response:
                    rm.close()
                    return ip
            except pyvisa.errors.VisaIOError:
                pass
        except socket.error:
            pass

    rm.close()
