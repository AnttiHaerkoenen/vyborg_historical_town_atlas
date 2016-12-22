import io

import requests
import pandas as pd
import matplotlib.pyplot as plt


DATA_DIR = 'https://raw.githubusercontent.com/AnttiHaerkoenen/vyborg_historical_town_atlas/master/data'


def get_csv(file, data_dir=DATA_DIR):
    url = '{0}/{1}'.format(data_dir, file)
    s = requests.get(url).content
    csv = io.StringIO(s.decode('utf-8'))
    return csv


lang_groups = pd.read_csv(get_csv('lang_groups_1812_1939.csv'))
lang_groups.columns = ["vuosi", "suomi", "venäjä", "ruotsi", "saksa", "muut"]
population = pd.read_csv(get_csv('population_1799_2011.csv'))
population.columns = ["vuosi", "väkiluku"]

plt.style.use("ggplot")
lang_groups.plot(x="vuosi", title="Viipurilaisten äidinkieli 1812-1939")
plt.show()

lang_groups.plot.bar(x="vuosi", stacked=True, title="Viipurilaisten äidinkieli 1812-1939")
plt.show()

x = 1799, 2011
population.plot(
    x="vuosi",
    c='blue',
    title="Viipurin väkiluku 1799-2011"
).fill_between(
    x=population['vuosi'],
    y1=population['väkiluku'],
    facecolor='blue'
)
plt.show()
