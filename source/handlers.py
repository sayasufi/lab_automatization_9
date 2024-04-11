import datetime
import logging
import os
import time

import pandas as pd
from matplotlib import pyplot as plt


class ConvertData:
    def __init__(self, exp_name):
        self.data = {}
        self.path_to_csv = (f"data/"
                            f"{datetime.date.today().strftime('%d.%m.%Y')}/"
                            f"{exp_name}_"
                            f"({datetime.datetime.now().strftime('%Hh_%Mm_%Ss')})")

        self.path_to_png = (f'images/'
                            f'{datetime.date.today().strftime("%d.%m.%Y")}/'
                            f'{exp_name}_'
                            f'({datetime.datetime.now().strftime("%Hh_%Mm_%Ss")})')

        os.makedirs(os.path.dirname(self.path_to_csv), exist_ok=True)
        os.makedirs(os.path.dirname(self.path_to_png), exist_ok=True)

        self.df = pd.DataFrame(columns=['Частота', 'Уровень', 'Напряжение', 'Разброс', 'Чувствительность'])

        self.init_plot()

    def flush_to_csv(self, **data):
        self.data = data
        self.df = self.df.append(self.data, ignore_index=True)
        self.df.to_csv(f"{self.path_to_csv}.csv")

    def convert_to_png(self):
        df = pd.read_csv(f"{self.path_to_csv}.csv")

        plt.style.use("ggplot")
        plt.plot(df["Частота"], df["Напряжение"])
        plt.xlabel('Частота, Мгц')
        plt.ylabel('Напряжение, В')
        for spine in plt.gca().spines.values():
            spine.set_color('black')
            spine.set_linewidth(1.5)
        plt.gca().set_facecolor('white')
        plt.grid(color='gray', alpha=0.7, linestyle='--')
        plt.savefig(f"{self.path_to_png}_FV.png", dpi=600)

        plt.plot(df["Частота"], df["Чувствительность"])
        plt.xlabel('Частота, Мгц')
        plt.ylabel('Чувствительность, Дб')
        for spine in plt.gca().spines.values():
            spine.set_color('black')
            spine.set_linewidth(1.5)
        plt.gca().set_facecolor('white')
        plt.grid(color='gray', alpha=0.7, linestyle='--')
        plt.savefig(f"{self.path_to_png}_FL.png", dpi=600)

        logging.info(f"Графики сохранены в {self.path_to_png}")

    def csv_to_excel(self):
        df = pd.read_csv(f"{self.path_to_csv}.csv")
        df.to_excel(f"{self.path_to_csv}.xlsx", index=False)

    def init_plot(self):
        self.fig, self.ax = plt.subplots()
        self.x_data = []
        self.y_data = []
        self.line, = self.ax.plot([], [])
        plt.ion()
        plt.show()

        for spine in self.ax.spines.values():
            spine.set_color('black')
            spine.set_linewidth(1.5)
        self.ax.set_xlabel('Частота, Мгц')
        self.ax.set_ylabel('Чувствительность, Дб')
        self.ax.set_facecolor('white')
        self.ax.grid(color='gray', alpha=0.7, linestyle='--')

    def update_plot(self, x, y):
        self.x_data.append(x)
        self.y_data.append(y)
        self.line.set_xdata(self.x_data)
        self.line.set_ydata(self.y_data)
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


class PowerLimiter:
    def __init__(self, center_freq, min_freq, max_freq):
        self.__min_limitation = {
            (min_freq, center_freq - 8): -10,
            (center_freq - 8, center_freq + 8): -70,
            (center_freq + 8, max_freq): 0
        }
        self.__max_limitation = {
            (min_freq, center_freq - 8): 0,
            (center_freq - 8, center_freq - 6): -10,
            (center_freq - 6, center_freq + 6): -40,
            (center_freq + 6, center_freq + 8): -10,
            (center_freq + 8, max_freq): 0
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


class Calculation:
    def __init__(self, osc, gen, db_step, window):
        self.center_voltage = None
        self.osc = osc
        self.gen = gen
        self.db_step = db_step
        self.window = window

    def search_optimal_level(self, freq_current, flag=False):

        voltage_last = 1000
        volt_list = []
        result_list = []

        for db_current in range(self.window.get_min_limit(freq_current),
                                self.window.get_max_limit(freq_current) + 1,
                                self.db_step):
            self.gen.set_level(db_current)
            time.sleep(0.3)
            data = self.osc.get_all()
            voltage_current = self.osc.convert_voltage(data["AVERage"])
            pkp_current = self.osc.convert_voltage(data["PKPK"])

            if voltage_current < 0.85 or db_current == self.window.get_max_limit(freq_current):
                volt_list = [abs(x - 1) for x in volt_list]
                min_index = volt_list.index(min(volt_list))
                if flag:
                    self.center_voltage = voltage_last
                return result_list[min_index]

            else:
                volt_list.append(voltage_current)
                result_list.append((voltage_current, pkp_current, db_current))

    def calculate_l(self, voltage, db):
        """Расчет чувствительности"""
        return (voltage - self.center_voltage) / 0.0245 + db
