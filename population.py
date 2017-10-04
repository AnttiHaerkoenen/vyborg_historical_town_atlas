import io

import requests
import pandas as pd
import numpy as np
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

social_strata = pd.read_csv(get_csv('language_groups_by_social_strata.csv'), index_col=0)
social_strata['total'] = social_strata.sum(axis=1)
total = social_strata.sum(axis=0)
social_strata = social_strata.append(total, ignore_index=True)
social_strata.index = "Finnish Swedish German Russian Other total".split(' ')
strata_totals, lang_totals = np.broadcast_arrays(social_strata.values[-1], social_strata.values[:,-1].reshape(6,1))
strata_pct = np.round(social_strata / strata_totals * 100, decimals=1)
lang_pct = np.round(social_strata / lang_totals * 100, decimals=1)

employment = pd.read_csv(get_csv('employment.csv'), index_col=0)

plt.style.use("ggplot")
lang_groups.plot(
    x="vuosi",
    title="Viipurin kieliryhmät 1812-1939",
    figsize=(8, 6)
)
plt.show()

lang_groups.plot(
    x="vuosi",
    kind="bar",
    stacked=True,
    title="Viipurin kieliryhmät 1812-1939",
    figsize=(8, 6)
)
plt.tight_layout()
plt.show()

lang_group_proportions.plot(
    x="vuosi",
    kind='area',
    stacked=True,
    title="Viipurilaisten kieliryhmät 1812-1939\nVäestöosuudet",
    figsize=(8, 6),
    ylim=(0, 100)
).set_ylabel('%')
plt.tight_layout()
plt.show()

population.plot(
    kind='area',
    x="vuosi",
    color='blue',
    title="Viipurin väkiluku 1799-2011"
)
plt.show()

pop_districts.plot(
    kind='area',
    figsize=(11, 12),
    stacked=True,
    title="Viipurin kaupunginosien väkiluku 1870-1920"
)
plt.legend(loc='upper left').get_frame().set_facecolor("white")
labels = 'Valli, Salakkalahti, Repola, P. Anna, Viipurin esik., ' \
         'Saunalahti, Hiekka, Anina, Papula, Pantsarlahti, Muut'.split(', ')
ann_x = [1920 for _ in labels]
ann_y = [2100, 5100, 8300, 11300, 12300, 13000, 13400, 15700, 19400, 22800, 24825]
for ann, x, y in zip(labels, ann_x, ann_y):
    plt.annotate(ann, (x, y))
plt.show()

pop_suburbs.plot(
    kind='area',
    figsize=(11, 12),
    stacked=True,
    title="Viipurin esikaupunkien väkiluku 1870-1920"
)
plt.legend(loc='upper left').get_frame().set_facecolor("white")
labels = 'Sorvali, Hiekka, Papula, Saunalahti, Likolampi, Tiiliruukki, Kelkkala, ' \
         'Kolikkoinmäki, Karjala, Kangasranta, Saaret'.split(', ')
ann_x = [1920 for _ in labels]
ann_y = [1700, 4200, 5500, 6600, 7500, 10000, 14000, 18500, 22500, 24300, 27000]
for ann, x, y in zip(labels, ann_x, ann_y):
    plt.annotate(ann, (x, y))
plt.show()

births_deaths.plot(
    figsize=(10, 8),
    title="Viipurin läänin avioituneisuus, syntyneisyys ja kuolleisuus 1812-1917"
)
plt.tight_layout()
plt.show()
