import os

import pandas as pd
from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure


if __name__ == '__main__':
    os.chdir('../data')
    population = pd.read_csv('population_1799_2011.csv', index_col=0)
    source = ColumnDataSource(population)

    fig = figure(
        plot_width=700,
        plot_height=400,
    )
    fig.line(x='year', y='population', source=source)
    fig.title.align = 'center'
    fig.title.text_font_size = '20pt'
    fig.xaxis.major_label_text_font_size = '16pt'
    fig.yaxis.major_label_text_font_size = '16pt'
    fig.xaxis.axis_label = 'Vuosi | Year'
    fig.yaxis.axis_label = 'Asukkaat | Inhabitants '

    hover = HoverTool(
        tooltips=[
            ("vuosi", "@year"),
            ("väkiluku", "@population")
        ],
        mode='vline'
    )
    fig.add_tools(hover)
    output_file(r'../figures/total_population.html')
    show(fig)
