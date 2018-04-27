import os

import pandas as pd
from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure


if __name__ == '__main__':
    os.chdir('../data')
    population = pd.read_csv('population_karonen.csv', index_col=0)
    population.interpolate(method='linear', inplace=True)
    population['Yhteensa'] += population['korjaus']
    population['ka'] = population['Yhteensa'].rolling(5).mean()
    source = ColumnDataSource(population)

    fig = figure(
        plot_width=700,
        plot_height=400,
        x_range=(1635, 1710),
    )
    line1 = fig.line(x='vuosi', y='ka', source=source, color='blue', legend='väestö henkikirjojen mukaan')
    fig.title.align = 'center'
    fig.title.text_font_size = '20pt'
    fig.xaxis.major_label_text_font_size = '16pt'
    fig.yaxis.major_label_text_font_size = '16pt'

    hover = HoverTool(renderers=[line1])
    hover.tooltips = [
            ("vuosi", "@vuosi"),
            ("väkiluku, henkikirja", "@Yhteensa{0.}"),
    ]
    hover.mode = 'vline'

    fig.add_tools(hover)
    fig.legend.location = 'top_right'

    output_file(r'../figures/population_ruuth.html')
    show(fig)
