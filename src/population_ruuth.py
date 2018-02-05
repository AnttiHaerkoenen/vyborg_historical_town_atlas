import os

import pandas as pd
import numpy as np
from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure


if __name__ == '__main__':
    os.chdir('../data')
    population = pd.read_csv('population_ruuth.csv', index_col=0)
    population.interpolate(method='linear', inplace=True)
    print(population['population_church'])
    source = ColumnDataSource(population)

    fig = figure(
        title="Viipurin väkiluku 1718-1900",
        plot_width=1000,
        plot_height=600
    )
    fig.line(x='year', y='population_secular', source=source, color='blue', legend='väestö henkikirjojen mukaan')
    fig.line(x='year', y='population_church', source=source, color='green', legend='väestö, srk')
    fig.title.align = 'center'
    fig.title.text_font_size = '20pt'
    fig.xaxis.major_label_text_font_size = '16pt'
    fig.yaxis.major_label_text_font_size = '16pt'

    hover = HoverTool(
        tooltips=[
            ("vuosi", "@year"),
            ("väkiluku, henkikirja", "@population_secular{0.}"),
            ("väkiluku, srk", "@population_church{0.}"),
        ],
        mode='vline'
    )

    fig.add_tools(hover)
    fig.legend.location = 'top_left'

    show(fig)
