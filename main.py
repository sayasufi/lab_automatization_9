import warnings

import source.hardware as hardware
from source.funcs import *
from source.logger import setup_logging
from source.parsing import config_pars, name_exp_parse


def main():
    """Точка входа"""
    warnings.simplefilter(action="ignore", category=FutureWarning)
    setup_logging()
    exp_name, variables = config_pars("config.ini")
    logging.info("Файл config.ini успешно загружен")

    names_for_file = name_exp_parse()

    # Инициализация осциллографа и генератора
    generator = hardware.RigolDSG815(level=-70, freq=1160)
    oscilloscope = hardware.AKIP4122()

    exp_class = globals()[exp_name](*variables, oscilloscope, generator, names_for_file)
    exp_class.start()


if __name__ == '__main__':
    main()
