import io

import requests
import pandas as pd
from bokeh.io import show, output_file
from bokeh.palettes import Colorblind5
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure

DATA_DIR = 'https://raw.githubusercontent.com/AnttiHaerkoenen/vyborg_historical_town_atlas/master/data'


def get_csv(file, data_dir=DATA_DIR):
    url = '{0}/{1}'.format(data_dir, file)
    s = requests.get(url).content
    csv = io.StringIO(s.decode('utf-8'))
    return csv


lang_groups = pd.read_csv(get_csv('lang_groups_1812_1939.csv'), index_col=0).fillna(0)
lang_groups = lang_groups[lang_groups.columns[::-1]]
totals = lang_groups.sum(axis=1)
lang_group_pct = lang_groups.div(totals, axis=0) * 100

group_names = "suomi, venaja, ruotsi, saksa, muut".split(', ')[::-1]
lang_groups.columns = group_names
lang_group_pct.columns = lang_groups.columns

lang_groups_source = ColumnDataSource(lang_groups)
lang_groups_pct_source = ColumnDataSource(lang_group_pct)

f = figure(
    y_range=(0, 100),
    title="Kieliryhmien osuus Viipurin väestöstä 1812-1939 (%)",
    plot_width=1000,
    plot_height=1000
)
f.vbar_stack(
    stackers=group_names,
    x='year',
    width=8,
    color=Colorblind5,
    source=lang_groups_pct_source,
    legend=[c.upper() for c in group_names]
)
f.legend.location = "top_right"
f.title.align = 'center'
f.title.text_font_size = '20pt'
f.xaxis.major_label_text_font_size = '16pt'
f.yaxis.major_label_text_font_size = '16pt'

hover = HoverTool(tooltips=[
    ("vuosi", "@year"),
    ("suomi", "@suomi{0.0 a}"),
    ("venäjä", "@venaja{0.0 a}"),
    ("ruotsi", "@ruotsi{0.0 a}"),
    ("saksa", "@saksa{0.0 a}"),
    ("muut", "@muut{0.0 a}")
])

f.add_tools(hover)

show(f)
