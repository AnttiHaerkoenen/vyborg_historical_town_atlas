import os

import pandas as pd
from bokeh.io import show, output_file
from bokeh.palettes import Colorblind5
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure


if __name__ == '__main__':
    os.chdir(r'../data')
    palette = Colorblind5

    lang_groups = pd.read_csv('lang_groups_1812_1939.csv', index_col=0).fillna(0)
    lang_groups = lang_groups[lang_groups.columns[::-1]]
    totals = lang_groups.sum(axis=1)
    lang_group_pct = lang_groups.div(totals, axis=0) * 100

    group_names = "finnish, russian, swedish, german, other".split(', ')[::-1]
    group_names_legend = "suomi, venäjä, ruotsi, saksa, muut".split(', ')
    lang_groups.columns = group_names
    lang_group_pct.columns = lang_groups.columns

    lang_groups_source = ColumnDataSource(lang_groups)
    lang_groups_pct_source = ColumnDataSource(lang_group_pct)

    fig = figure(
        y_range=(0, 101),
        plot_width=900,
        plot_height=700
    )
    fig.vbar_stack(
        stackers=group_names,
        x='year',
        width=8,
        color=palette,
        source=lang_groups_pct_source,
    )

    hover = HoverTool(tooltips=[
        ("vuosi", "@year"),
        ("suomi", "@finnish{0.0 a}"),
        ("venäjä", "@russian{0.0 a}"),
        ("ruotsi", "@swedish{0.0 a}"),
        ("saksa", "@german{0.0 a}"),
        ("muut", "@other{0.0 a}")
    ])

    for group, color in zip(group_names_legend, reversed(palette)):
        fig.circle(x=[], y=[], fill_color=color, legend=group)

    fig.legend.location = "top_right"
    fig.legend.border_line_color = 'black'
    fig.legend.background_fill_alpha = 1
    fig.title.align = 'center'
    fig.title.text_font_size = '20pt'
    fig.xaxis.major_label_text_font_size = '16pt'
    fig.yaxis.major_label_text_font_size = '16pt'

    fig.add_tools(hover)
    output_file(r'../figures/language_groups_percentages.html')
    show(fig)
