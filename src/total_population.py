import io

import requests
import pandas as pd
from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure

DATA_DIR = 'https://raw.githubusercontent.com/AnttiHaerkoenen/vyborg_historical_town_atlas/master/data'


def get_csv(file, data_dir=DATA_DIR):
    url = '{0}/{1}'.format(data_dir, file)
    s = requests.get(url).content
    csv = io.StringIO(s.decode('utf-8'))
    return csv


population = pd.read_csv(get_csv('population_1799_2011.csv'), index_col=0)
source = ColumnDataSource(population)

f = figure(
    title="Population of Vyborg",
    plot_width=1000,
    plot_height=600
)
f.line(x='year', y='population', source=source)
f.title.align = 'center'
f.title.text_font_size = '20pt'
f.xaxis.major_label_text_font_size = '16pt'
f.yaxis.major_label_text_font_size = '16pt'

hover = HoverTool(
    tooltips=[
        ("vuosi", "@year"),
        ("väkiluku", "@population")
    ],
    mode='vline'
)

f.add_tools(hover)

show(f)
