import logging
import time

import numpy as np

from source.handlers import PowerLimiter, ConvertData, Calculation
from source.interfaces import Generator, Oscilloscope


class SearchOptimalLevel:
    """Класс определения оптимального уровня в Дб"""

    def __init__(self,
                 freq_start: int,
                 freq_stop: int,
                 freq_step: int | float,
                 center_freq: int,
                 db_step: int,
                 osc: Oscilloscope,
                 gen: Generator,
                 exp_name):
        self.calculation = None
        self.freq_start = freq_start
        self.freq_stop = freq_stop
        self.freq_step = freq_step
        self.center_freq = center_freq
        self.center_voltage = None
        self.center_db = None
        self.center_pkp = None
        self.db_step = db_step
        self.osc = osc
        self.gen = gen

        # Массив частот
        self.array_freq = np.arange(self.freq_start, self.freq_stop, self.freq_step)
        # Кол-во элементов массива
        self.num_elements = self.array_freq.shape[0]
        # Создаем пустой массив для напряжений и PKP
        self.voltage_list = np.empty(self.num_elements)
        self.pkp_list = np.empty(self.num_elements)
        self.db_list = np.empty(self.num_elements)
        self.l_list = np.empty(self.num_elements)

        self.window = PowerLimiter(center_freq, freq_start, freq_stop)
        self.convert = ConvertData(exp_name)
        logging.info("Настройка класса для определения оптимального уровня успешно выполнена")

    def start(self):
        logging.info("Старт эксперемента...")
        self.gen.out_on()
        self.calculation = Calculation(self.osc, self.gen, self.db_step, self.window)
        self.center_voltage, self.center_pkp, self.center_db = self.calculation.search_optimal_level(self.center_freq,
                                                                                                     flag=True)

        for i in range(self.num_elements):
            start_time = time.time()
            freq = np.round(self.array_freq[i], 2)
            if int(freq) == int(self.center_freq):
                l = self.calculation.calculate_l(self.center_voltage, self.center_db)
                self.convert.flush_to_csv(Частота=self.center_freq,
                                          Уровень=self.center_db,
                                          Напряжение=self.center_voltage,
                                          Разброс=self.center_pkp,
                                          Чувствительность=l)
                self.convert.update_plot(self.center_freq, l)
            else:
                self.gen.set_level(self.window.get_min_limit(freq))
                self.gen.set_freq(freq)
                voltage, pkp, db = self.calculation.search_optimal_level(freq, flag=False)
                l = self.calculation.calculate_l(voltage, db)
                self.voltage_list[i], self.pkp_list[i], self.db_list[i], self.l_list[i] = voltage, pkp, db, l

                self.convert.flush_to_csv(Частота=freq,
                                          Уровень=db,
                                          Напряжение=voltage,
                                          Разброс=pkp,
                                          Чувствительность=l)

                self.convert.update_plot(freq, l)

            end_time = (time.time() - start_time) * (self.num_elements - i)
            hours = int(end_time // 3600)
            minutes = int((end_time % 3600) // 60)
            seconds = int(end_time % 60)

            logging.info(f"Измерение {i} из {self.num_elements}\n"
                         f"Уровень = {db}Дб, Частота = {freq}Мгц, Напряжение = {voltage}В\n"
                         f"Примерное оставшееся время = {hours}ч {minutes}м {seconds}с\n")

        self.gen.disconnect()
        self.osc.disconnect()

        self.convert.convert_to_png()
        self.convert.csv_to_excel()


class Linear:
    """Класс измерения линейного изменения частот на одном уровне Дб"""

    def __init__(self,
                 freq_start: int,
                 freq_stop: int,
                 freq_step: int | float,
                 center_freq: int,
                 db: int,
                 count_measurements: int,
                 osc: Oscilloscope,
                 gen: Generator,
                 exp_name):

        self.convert = None
        self.calculation = None
        self.center_voltage = None
        self.center_pkp = None
        self.center_db = None
        self.freq_start = freq_start
        self.freq_stop = freq_stop
        self.freq_step = freq_step
        self.center_freq = center_freq
        self.db = db
        self.osc = osc
        self.gen = gen
        self.count_measurements = count_measurements
        self.exp_name = exp_name

        # Массив частот
        self.array_freq = np.arange(self.freq_start, self.freq_stop, self.freq_step)
        # Кол-во элементов массива
        self.num_elements = self.array_freq.shape[0]
        # Создаем пустой массив для напряжений и PKP
        self.voltage_list = np.empty(self.num_elements)
        self.pkp_list = np.empty(self.num_elements)
        self.db_list = np.empty(self.num_elements)
        self.l_list = np.empty(self.num_elements)

        self.window = PowerLimiter(center_freq, freq_start, freq_stop)
        logging.info("Настройка класса для измерения линейного изменения частот на одном уровне успешно выполнена")

    def start(self):
        logging.info("Старт эксперемента...")
        self.gen.out_on()
        self.calculation = Calculation(self.osc, self.gen, 10, self.window)
        self.center_voltage, self.center_pkp, self.center_db = self.calculation.search_optimal_level(self.center_freq,
                                                                                                     flag=True)

        for j in range(1, self.count_measurements + 1):
            # Создаем пустой массив для напряжений и PKP
            self.voltage_list = np.empty(self.num_elements)
            self.pkp_list = np.empty(self.num_elements)
            self.db_list = np.empty(self.num_elements)
            self.l_list = np.empty(self.num_elements)
            self.convert = ConvertData(self.exp_name)

            for i in range(self.num_elements):
                start_time = time.time()
                if i == self.center_freq:
                    l = self.calculation.calculate_l(self.center_voltage, self.center_db)
                    self.convert.flush_to_csv(Частота=self.center_freq,
                                              Уровень=self.center_db,
                                              Напряжение=self.center_voltage,
                                              Разброс=self.center_pkp,
                                              Чувствительность=l)
                    self.convert.update_plot(self.center_freq, l)
                else:
                    self.gen.set_freq(self.array_freq[i])
                    time.sleep(0.3)
                    data = self.osc.get_all()

                    self.voltage_list[i] = self.osc.convert_voltage(data["AVERage"])
                    self.pkp_list[i] = self.osc.convert_voltage(data["PKPK"])
                    self.db_list[i] = self.db
                    self.l_list[i] = self.calculation.calculate_l(self.voltage_list[i], self.db)
                    self.convert.flush_to_csv(Частота=i,
                                              Уровень=self.db,
                                              Напряжение=self.voltage_list[i],
                                              Разброс=self.pkp_list[i],
                                              Чувствительность=self.l_list[i])
                    self.convert.update_plot(i, self.l_list[i])

                end_time = (time.time() - start_time) * (
                        (self.num_elements - i) + (self.count_measurements - j) * self.num_elements)
                hours = int(end_time // 3600)
                minutes = int((end_time % 3600) // 60)
                seconds = int(end_time % 60)

                logging.info(f"Измерение {j} из {self.count_measurements}\n"
                             f"{int(i / self.num_elements * 100)}%\n"
                             f"Уровень = {self.db}Дб, Частота = {self.array_freq[i]}Мгц, Напряжение = {self.voltage_list[i]}В"
                             f"Примерное оставшееся время = {hours}ч {minutes}м {seconds}с\n")

            self.convert.convert_to_png()
            self.convert.csv_to_excel()
