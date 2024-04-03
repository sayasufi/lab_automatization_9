import logging
import time

from source.interfaces import Generator


class Rigol(Generator):
    def __init__(self, ip: str = "192.168.1.102", level: int = -70, freq: int = 1160):
        super().__init__(ip)

        self.set_factory_settings()
        self.level: int = level
        self.freq: int | float = freq
        self.resource.write(f":LEV {self.level}")
        self.resource.write(f":FREQ {self.freq * 1000}KHz")
        logging.info("Инициализация Rigol успешно завершена")

    def set_level(self, level: int):
        """Установить амплитуду радиочастотного сигнала."""
        self.level = level
        self.resource.write(f":LEV {self.level}")

    def set_freq(self, freq: int | float):
        """Установить частоту радиочастотного сигнала"""
        self.freq = freq
        self.resource.write(f":FREQ {int(self.freq * 1000)}KHz")

    def out_on(self):
        """Включить радиочастотный выход"""
        self.resource.write(":OUTP ON")
        logging.info("Включен радиочастотный выход Rigol")

    def out_off(self):
        """Выключить радиочастотный выход"""
        self.resource.write(":OUTP OFF")
        logging.info("Выключен радиочастотный выход Rigol")

    def disconnect(self):
        """Закрыть соединение с Rigol"""
        self.out_off()
        super().disconnect()

    def set_factory_settings(self):
        """
        После очистки данных прибор будет восстановлен к заводским настройкам.
        — Отформатировать флэш-память NAND;
        — Восстановить заводские настройки пользовательских данных, сохраненных в NVRAM и NorFlash;
        — Восстановить заводские настройки ИМЕНИ хоста, IP-адреса и пароля в LXI.
        """
        self.resource.write(":SYST:PRES:TYPE FACtory")
        time.sleep(2)
        logging.info("Сброс Rigol к заводским настройкам успешно произведен")
        self.out_off()
