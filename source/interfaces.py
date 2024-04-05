import logging
import re
import socket

import pyvisa


def check_ip_address(ip):
    """Проверка валидности ip-адреса"""
    ip_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    try:
        if re.match(ip_pattern, ip):
            return True
        else:
            return False
    except TypeError:
        return False


def scan_instr(instr_name: str):
    """Поиск ip оборудования"""
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


class BaseInterface(object):
    def __init__(self, ip: str, port: int | None = None, type_instr: str | None = None):

        if type_instr == "gen":
            self.string = "генератор"
        elif type_instr == "osc":
            self.string = "осциллограф"
        else:
            logging.error("Неизвестный тип прибора")

        if not check_ip_address(ip):
            logging.error(f"IP адрес - {ip} задан неверно")
            raise TypeError(f"IP адрес - {ip} задан неверно")

        if port is None:
            address = "TCPIP0::" + ip + "::INSTR"
            try:
                rm = pyvisa.ResourceManager()
                self.resource = rm.open_resource(address)
                idn_response = self.resource.query("*IDN?")
                if idn_response:
                    logging.info(f"Подключение к {self.string}у успешно завершено\n{idn_response}")
                else:
                    logging.error(f"Ошибка при подключении к {self.string}у (IDN?)")
            except pyvisa.errors.VisaIOError:
                logging.error(f"Ошибка при подключении к {self.string}у")
            self.sock = None

        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.sock.connect((ip, port))
                self.sock.send("*IDN?\n".encode())
                data = self.sock.recv(1024).decode()
                if data:
                    logging.info(f"Подключение к {self.string}у успешно завершено\n{data}")
                else:
                    logging.error(f"Ошибка при подключении к {self.string}у (*IDN?)")
            except Exception:
                logging.error(f"Ошибка при подключении к {self.string}у")
            self.resource = None

    def set_factory_settings(self):
        """Сброс к заводским настройкам"""
        pass

    def disconnect(self):
        """Закрыть соединение с прибором"""
        if self.resource:
            self.resource.close()
            logging.info(f"Соединение с {self.string}ом закрыто")
        elif self.sock:
            self.sock.close()
            logging.info(f"Соединение с {self.string}ом закрыто")
        else:
            logging.error("Соединение не может быть закрыто")

    def convert_voltage(self, data):
        """Перевод строки напряжения в float значение [В]"""
        if "mV" in data:
            return round(float(data[:-2]) / 1000, 4)
        elif "V" in data:
            return float(data[:-1])
        else:
            logging.error(f"Неопределенная размерность напряжения: {data}")


class Oscilloscope(BaseInterface):
    def __init__(self, ip: str, port: int | None = None):
        super().__init__(ip, port, "osc")

    def get_all(self):
        """Получить все измеренные значения"""
        pass

    def get_mean(self):
        """Получить среднее напряжение"""
        pass

    def get_pkp(self):
        """Получить peak-to-peak значение"""
        pass

    def get_min(self):
        """Получить минимальное значение"""
        pass

    def get_max(self):
        """Получить максимальное значение"""
        pass


class Generator(BaseInterface):
    def __init__(self, ip: str, port: int | None = None):
        super().__init__(ip, port, "gen")

    def set_level(self, level: int):
        """Установить амплитуду радиочастотного сигнала."""
        pass

    def set_freq(self, freq: int | float):
        """Установить частоту радиочастотного сигнала"""
        pass

    def out_on(self):
        """Включить радиочастотный выход."""
        pass

    def out_off(self):
        """Выключить радиочастотный выход."""
        pass
