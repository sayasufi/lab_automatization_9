import datetime
import logging
import os


class ConsoleColors:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET = '\033[0m'


def setup_logging():
    """Создаем функцию инициализирующую логгер"""
    log_file = (f"cache/"
                f"{datetime.date.today().strftime('%d.%m.%Y')}/"
                f"log_{datetime.datetime.now().strftime('%H_%M_%S')}.log")

    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    with open(log_file, "w"):
        pass

    class InfoFilter(logging.Filter):
        def filter(self, record):
            return record.levelno == logging.INFO

    class WarningFilter(logging.Filter):
        def filter(self, record):
            return record.levelno == logging.WARNING

    # Создаем логгер
    logger = logging.getLogger()
    logger.setLevel(logging.NOTSET)

    # Создаем форматтер для логов
    formatter = logging.Formatter("%(levelname)s\t%(asctime)s\t%(message)s")
    # Создаем обработчик для записи в файл
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Обработчик для WARNING
    debug_handler = logging.StreamHandler()
    debug_handler.setLevel(logging.WARNING)
    debug_formatter = logging.Formatter(ConsoleColors.BLUE + "%(levelname)s - %(message)s")
    debug_handler.setFormatter(debug_formatter)
    debug_handler.addFilter(WarningFilter())
    logger.addHandler(debug_handler)

    # Обработчик для INFO
    info_handler = logging.StreamHandler()
    info_handler.setLevel(logging.INFO)
    info_formatter = logging.Formatter(ConsoleColors.GREEN + "%(levelname)s - %(message)s")
    info_handler.setFormatter(info_formatter)
    info_handler.addFilter(InfoFilter())
    logger.addHandler(info_handler)

    # Обработчик для WARNING
    warning_handler = logging.StreamHandler()
    warning_handler.setLevel(logging.ERROR)
    warning_formatter = logging.Formatter(ConsoleColors.RED + "%(levelname)s - %(message)s")
    warning_handler.setFormatter(warning_formatter)
    logger.addHandler(warning_handler)

    return logger
