import json
import logging
import time

from source.interfaces import Oscilloscope


class AKIP4122(Oscilloscope):
    def __init__(self, ip: str = "192.168.1.72", port: int = 3000):
        super().__init__(ip, port)
        self.set_factory_settings()

        self.json_string = {}

    def get_all(self):
        self.sock.send(":MEASUrement:CH1?\n".encode())
        unicode_string = self.sock.recv(1024).decode("latin1")
        unicode_string = unicode_string[unicode_string.index("{"):]
        self.json_string = json.loads(unicode_string, strict=False)["CH1"]
        return self.json_string

    def get_mean(self):
        self.sock.send(":MEASUrement:CH1:AVERage?\n".encode())
        data = self.sock.recv(1024).decode()[4:-3]
        return self.convert_voltage(data)

    def get_pkp(self):
        self.sock.send(":MEASUrement:CH1:PKPK?\n".encode())
        data = self.sock.recv(1024).decode()[6:-3]
        return self.convert_voltage(data)

    def set_default_settings(self):
        """Сброс AKIP к заводским настройкам и очистка регистров"""
        # Восстановить значение прибора по умолчанию.
        self.sock.send("*RST\n".encode())
        # Очистить все регистры событий в наборе регистров и очистите очередь ошибок.
        self.sock.send("*CLS\n".encode())
        time.sleep(2)
        logging.info("Сброс AKIP к заводским настройкам успешно произведен")
