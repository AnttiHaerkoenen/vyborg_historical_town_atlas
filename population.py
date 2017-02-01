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
totals = lang_groups[lang_groups.columns[1:]].sum(axis=1)
lang_group_proportions = pd.DataFrame({'year': lang_groups['year']})
lang_group_proportions[lang_groups.columns[1:]] = lang_groups[lang_groups.columns[1:]].div(totals, axis=0) * 100

lang_groups.columns = ["vuosi", "suomi", "venäjä", "ruotsi", "saksa", "muut"]
lang_group_proportions.columns = lang_groups.columns

population = pd.read_csv(get_csv('population_1799_2011.csv'))
population.columns = ["vuosi", "väkiluku"]

pop_districts = pd.read_csv(get_csv('population_districts.csv'), index_col=0)
pop_suburbs = pd.read_csv(get_csv('population_suburbs.csv'), index_col=0)

births_deaths = pd.read_csv(get_csv('births_deaths.csv'), index_col=0)
print(births_deaths)

plt.style.use("ggplot")
lang_groups.plot(x="vuosi", title="Viipurin kieliryhmät 1812-1939")
plt.show()

lang_groups.plot(
    x="vuosi",
    kind="bar",
    stacked=True,
    title="Viipurin kieliryhmät 1812-1939"
)
plt.show()

lang_group_proportions.plot(
    x="vuosi",
    kind='area',
    stacked=True,
    title="Viipurilaisten kieliryhmät 1812-1939\nVäestöosuudet"
).set_ylabel('%')
plt.show()

x = 1799, 2011
population.plot(
    x="vuosi",
    color='blue',
    title="Viipurin väkiluku 1799-2011"
).fill_between(
    x=population['vuosi'],
    y1=population['väkiluku'],
    facecolor='blue'
)
plt.show()

pop_districts.plot(
    kind='area',
    figsize=(12, 10),
    stacked=True,
    title="Viipurin kaupunginosien väkiluku 1870-1920"
)
plt.legend(loc='upper left').get_frame().set_facecolor("white")
plt.show()


pop_suburbs.plot(
    kind='area',
    figsize=(12, 10),
    stacked=True,
    title="Viipurin esikaupunkien väkiluku 1870-1920"
)
plt.legend(loc='upper left').get_frame().set_facecolor("white")
plt.show()

births_deaths.plot()
plt.show()
