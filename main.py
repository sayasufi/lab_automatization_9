import logging

from log.logger import setup_logging
from source.Akip import Akip
from source.Rigol import Rigol
from source.funcs import SearchOptimalLevel
from source.scan import scan_instr

FREQ_START = 1120  # Начальная частота измерения в Мгц
FREQ_STOP = 1220  # Конечная частота измерения в Мгц
FREQ_STEP = 1  # Шаг измерения частоты в Мгц
LEVEL = -70  # Уровень сигнала в Дб

DB_STEP = 10
CENTER_FREQ = 1160


def main():
    """Точка входа"""

    # Путь до лог файла
    log_file = "log/cache.log"
    setup_logging(log_file)

    ip_rigol = scan_instr("Rigol")
    logging.info(f"Rigol найден на {ip_rigol}")

    # Инициализация осциллографа и генератора
    generator = Rigol(ip=ip_rigol, level=-70, freq=1160)
    oscilloscope = Akip()

    search_optimal_level = SearchOptimalLevel(FREQ_START,
                                              FREQ_STOP,
                                              FREQ_STEP,
                                              CENTER_FREQ,
                                              DB_STEP,
                                              oscilloscope,
                                              generator)
    search_optimal_level.start()


if __name__ == '__main__':
    main()
