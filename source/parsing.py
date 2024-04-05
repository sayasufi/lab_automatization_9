import configparser
import logging


def config_pars(path_to_config: str = "config.ini"):
    config = configparser.ConfigParser()
    config.read(path_to_config)

    exp_name = config.get("ExperimentName", "NAME")

    variables = []
    for key in config[exp_name]:
        value_temp = config[exp_name][key].split(";")[0].strip()
        if "." in value_temp:
            variables.append(float(value_temp))
        else:
            variables.append(int(value_temp))

    return exp_name, variables


def name_exp_parse():
    scheme_dict = {
        1: "с_резисторами",
        2: "без_резисторов"
    }
    screen_dict = {
        1: "c_экраном",
        2: "без_экрана"
    }
    logging.warning("Введите номер РЭМа")
    number_rem = input()
    logging.warning("Введите cхему РЭМа\n\t1 - С резисторами\n\t2 - Без резисторов")
    scheme = scheme_dict[int(input())]
    logging.warning("Установлен ли экран на РЭМ?\n\t1 - Да\n\t2 - Нет")
    screen = screen_dict[int(input())]
    logging.warning("Введите версию прошивки")
    version = input()

    return f"РЭМ-{number_rem}_{scheme}_{screen}_{version}"
