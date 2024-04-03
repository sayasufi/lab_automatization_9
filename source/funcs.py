import datetime
import logging
import os
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from source.interfaces import Generator, Oscilloscope


class ConvertData:
    def __init__(self, exp_name):
        self.data = {}
        self.path_to_csv = (f"data/"
                            f"{datetime.date.today().strftime('%d.%m.%Y')}/"
                            f"{exp_name}/"
                            f"{datetime.datetime.now().strftime('%H:%M:%S')}.csv")

        self.path_to_png = (f'images/'
                            f'{datetime.date.today().strftime("%d.%m.%Y")}/'
                            f'{exp_name}/'
                            f'{datetime.datetime.now().strftime("%H:%M:%S")}.png')

        os.makedirs(os.path.dirname(self.path_to_csv), exist_ok=True)
        os.makedirs(os.path.dirname(self.path_to_png), exist_ok=True)

        self.df = pd.DataFrame(columns=['Frequency', 'Level', 'Voltage', 'Peak_to_peak', 'L'])

    def flush_to_csv(self, **data):
        self.data = data
        new_data = {'Frequency': self.data["freq"],
                    'Level': self.data["level"],
                    'Voltage': self.data["volt"],
                    'Peak_to_peak': self.data["pkp"],
                    'L': self.data["l"]}

        self.df = self.df.append(new_data, ignore_index=True)
        self.df.to_csv(self.path_to_csv)

    def convert_to_png(self):
        df = pd.read_csv(self.path_to_csv)

        plt.style.use("ggplot")
        plt.plot(df["Frequency"], df["Voltage"])
        plt.xlabel('Частота, Мгц')
        plt.ylabel('Напряжение, В')
        for spine in plt.gca().spines.values():
            spine.set_color('black')
            spine.set_linewidth(1.5)
        plt.gca().set_facecolor('white')
        plt.grid(color='gray', alpha=0.7, linestyle='--')
        plt.savefig(f"{self.path_to_png}_FV", dpi=600)

        plt.plot(df["Frequency"], df["L"])
        plt.xlabel('Частота, Мгц')
        plt.ylabel('Чувствительность, Дб')
        for spine in plt.gca().spines.values():
            spine.set_color('black')
            spine.set_linewidth(1.5)
        plt.gca().set_facecolor('white')
        plt.grid(color='gray', alpha=0.7, linestyle='--')
        plt.savefig(f"{self.path_to_png}_FL", dpi=600)

        logging.info(f"Графики сохранены в {self.path_to_png}")


class PowerLimiter:
    def __init__(self):
        self.__min_limitation = {
            (1120, 1152): -20,
            (1153, 1169): -70,
            (1170, 1250): -20
        }
        self.__max_limitation = {
            (1120, 1152): 0,
            (1153, 1155): -50,
            (1156, 1167): -60,
            (1168, 1169): -50,
            (1170, 1250): 0
        }

    def get_max_limit(self, freq):
        for freq_range, value in self.__max_limitation.items():
            if freq_range[0] <= freq <= freq_range[1]:
                return value
        logging.error("Частота не удовлетворяет ни одному диапазону значений")
        return None

    def get_min_limit(self, freq):
        for freq_range, value in self.__min_limitation.items():
            if freq_range[0] <= freq <= freq_range[1]:
                return value
        logging.error("Частота не удовлетворяет ни одному диапазону значений")
        return None


class SearchOptimalLevel:
    """Класс определения оптимального уровня в Дб"""

    def __init__(self,
                 freq_start: int,
                 freq_stop: int,
                 freq_step: int | float,
                 center_freq: int,
                 db_step: int,
                 osc: Oscilloscope,
                 gen: Generator):

        self.voltage_center = None
        self.freq_start = freq_start
        self.freq_stop = freq_stop
        self.freq_step = freq_step
        self.center_freq = center_freq
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

        self.window = PowerLimiter()
        self.convert = ConvertData("search_optimal_level")

    def search_optimal_level(self, freq_current):

        voltage_last = 1000
        pkp_last = 0

        for db_current in range(self.window.get_min_limit(freq_current),
                                self.window.get_max_limit(freq_current) + 1,
                                self.db_step):
            self.gen.set_level(db_current)
            time.sleep(0.3)
            data = self.osc.get_all()
            voltage_current = self.osc.convert_voltage(data["AVERage"])
            pkp_current = self.osc.convert_voltage(data["PKPK"])

            if abs(voltage_current - 1) >= abs(voltage_last - 1) + 0.05 or voltage_current < 0.8:
                return voltage_last, pkp_last, db_current - self.db_step

            elif db_current == self.window.get_max_limit(freq_current):
                return voltage_current, pkp_current, db_current
            else:
                voltage_last = voltage_current
                pkp_last = pkp_current

    def calculate_l(self, voltage, db):
        """Расчет чувствительности"""
        return (voltage - self.voltage_center) / 0.0245 + db

    def start(self):
        self.gen.out_on()
        self.voltage_center = self.search_optimal_level(self.center_freq)[0]

        for i in range(self.num_elements):
            start_time = time.time()
            freq = self.array_freq[i]
            self.gen.set_level(self.window.get_min_limit(freq))
            self.gen.set_freq(freq)
            voltage, pkp, db = self.search_optimal_level(freq)
            l = self.calculate_l(voltage, db)
            self.voltage_list[i], self.pkp_list[i], self.db_list[i], self.l_list[i] = voltage, pkp, db, l

            self.convert.flush_to_csv(Frequency=freq,
                                      Level=db,
                                      Voltage=voltage,
                                      Peak_to_peak=pkp,
                                      L=l)

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
