from matplotlib import pyplot as plt
import pandas as pd

df = pd.read_csv("../../data/03.04.2024/search_optimal_level/20_39_37.csv")
freq = df["Частота"]
voltage = df["Напряжение"]
db = df["Уровень"]
a = (voltage - voltage[40])/(0.0245) + db

plt.style.use("ggplot")
plt.plot(freq, a)
plt.xlabel('Частота, Мгц')
plt.ylabel('Чувствительность, Дб')
for spine in plt.gca().spines.values():
    spine.set_color('black')
    spine.set_linewidth(1.5)
plt.gca().set_facecolor('white')
plt.grid(color='gray', alpha=0.7, linestyle='--')
plt.show()


class Linear:
    def __init__(self,
                 freq_start: int,
                 freq_stop: int,
                 freq_step: int | float,
                 db: int,
                 osc: Oscilloscope,
                 gen: Generator,
                 count_measurements: int = 1):

        self.freq_start = freq_start
        self.freq_stop = freq_stop
        self.freq_step = freq_step
        self.db = db
        self.osc = osc
        self.gen = gen
        self.count_measurements = count_measurements

    def initialize(self):
        # Массив частот
        self.array_freq = np.arange(self.freq_start, self.freq_stop, self.freq_step)
        # Кол-во элементов массива
        self.num_elements = self.array_freq.shape[0]
        self.gen.set_level(db)

    for j in range(1, count_measurements + 1):

        # Создаем пустой массив для напряжений и PKP
        voltage_list = np.empty(num_elements)
        pkp_list = np.empty(num_elements)
        db_list = np.empty(num_elements)

        for i in range(num_elements):

            if i % five_procent == 0:
                start_time = time.time()

            gen.set_freq(array_freq[i])
            time.sleep(0.3)
            data = osc.get_all()
            if not data:
                logging.error("Пустой массив данных от АКИП")
            else:
                voltage_list[i] = osc.convert_voltage(data["AVERage"])
                pkp_list[i] = osc.convert_voltage(data["PKPK"])
                db_list[i] = db

            if i % five_procent == 0:
                end_time = (time.time() - start_time) * ((num_elements - i) + (count_measurements - j) * num_elements)
                hours = int(end_time // 3600)
                minutes = int((end_time % 3600) // 60)
                seconds = int(end_time % 60)

                logging.info(f"Измерение {j} из {count_measurements}\n"
                             f"{int(i / num_elements * 100)}%\n"
                             f"Уровень = {db}Дб, Частота = {array_freq[i]}Мгц, Напряжение = {voltage_list[i]}В"
                             f"Примерное оставшееся время = {hours}ч {minutes}м {seconds}с\n")

        convert = ConvertData("linear",
                              array_freq=array_freq,
                              db_list=db_list,
                              voltage_list=voltage_list,
                              pkp_list=pkp_list)
        convert.convert_to_csv()
        convert.convert_to_png()