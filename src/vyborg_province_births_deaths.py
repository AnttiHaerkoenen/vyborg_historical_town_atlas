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


births_deaths = pd.read_csv(get_csv('births_deaths.csv'), index_col=0)
source = ColumnDataSource(births_deaths)
f = figure(
    title="Viipurin läänin syntyneisyys, kuolleisuus ja avioituneisuus 1815-1917",
    plot_width=1000,
    plot_height=600
)
f.line(x='vuosi', y='syntyneisyys', source=source, color='green')
f.line(x='vuosi', y='kuolleisuus', source=source, color='red')
f.line(x='vuosi', y='avioituneisuus', source=source, color='blue')
f.legend.location = "top_right"
f.title.align = 'center'
f.title.text_font_size = '20pt'
f.xaxis.major_label_text_font_size = '16pt'
f.yaxis.major_label_text_font_size = '16pt'

hover = HoverTool(
    tooltips=[
        ("vuosi", "@vuosi"),
        ("syntyneisyys", "@syntyneisyys")
    ],
    mode='vline'
)

f.add_tools(hover)

show(f)
