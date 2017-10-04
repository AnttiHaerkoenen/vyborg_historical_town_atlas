import io

import requests
import pandas as pd
from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

DATA_DIR = 'https://raw.githubusercontent.com/AnttiHaerkoenen/vyborg_historical_town_atlas/master/data'


def get_csv(file, data_dir=DATA_DIR):
    url = '{0}/{1}'.format(data_dir, file)
    s = requests.get(url).content
    csv = io.StringIO(s.decode('utf-8'))
    return csv


lang_groups = pd.read_csv(get_csv('lang_groups_1812_1939.csv'))
totals = lang_groups[lang_groups.columns[1:]].sum(axis=1)
lang_group_pct = pd.DataFrame({'year': lang_groups['year']})
lang_group_pct[lang_groups.columns[1:]] = lang_groups[lang_groups.columns[1:]].div(totals, axis=0) * 100

lang_groups.columns = "vuosi, suomi, venäjä, ruotsi, saksa, muut".split(', ')
lang_group_pct.columns = lang_groups.columns

lang_groups_source = ColumnDataSource(lang_groups)
lang_group_pct_source = ColumnDataSource(lang_group_pct)

colors = "blue, red, yellow, black, green".split(' ,')
f1 = figure(title="Viipurin kieliryhmät 1812-1939")
f1.vbar_stack(
    stackers="suomi, venäjä, ruotsi, saksa, muut".split(', '),
    x='vuosi',
    width=0.9,
    color=colors,
    source=lang_groups_source
)

show(f1)
