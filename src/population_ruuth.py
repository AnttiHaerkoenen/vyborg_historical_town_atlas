import os

import pandas as pd
from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure


if __name__ == '__main__':
    os.chdir('../data')
    population = pd.read_csv('population_ruuth.csv', index_col=0)
    population.interpolate(method='linear', inplace=True)
    source = ColumnDataSource(population)

    fig = figure(
        plot_width=600,
        plot_height=600,
        x_range=(1718, 1900),
    )
    line1 = fig.line(
        x='year',
        y='population_secular',
        source=source,
        color='blue',
        legend='väestö henkikirjojen mukaan',
    )
    line2 = fig.line(
        x='year',
        y='population_church',
        source=source,
        color='green',
        legend='väestö, srk',
    )
    fig.xaxis.major_label_text_font_size = '16pt'
    fig.yaxis.major_label_text_font_size = '16pt'
    fig.xaxis.axis_label = 'Vuosi | Year'
    fig.yaxis.axis_label = 'Asukkaat | Inhabitants '

    hover = HoverTool(renderers=[line1])
    hover.tooltips = [
            ("vuosi", "@year"),
            ("väkiluku, henkikirja", "@population_secular{0.}"),
            ("väkiluku, srk", "@population_church{0.}"),
    ]
    hover.mode = 'vline'

    fig.add_tools(hover)
    fig.legend.location = 'top_left'

    output_file(r'../figures/population_ruuth.html')
    show(fig)
