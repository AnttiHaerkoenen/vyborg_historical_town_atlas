import os

import pandas as pd
from bokeh.io import show, output_file
from bokeh.palettes import Colorblind5
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure


if __name__ == '__main__':
    os.chdir(r'../data')
    lang_groups = pd.read_csv('lang_groups_1812_1939.csv', index_col=0).fillna(0)
    lang_groups = lang_groups[lang_groups.columns[::-1]]
    totals = lang_groups.sum(axis=1)
    lang_group_pct = lang_groups.div(totals, axis=0) * 100

    group_names = "finnish, russian, swedish, german, other".split(', ')[::-1]
    lang_groups.columns = group_names
    lang_group_pct.columns = lang_groups.columns

    lang_groups_source = ColumnDataSource(lang_groups)
    lang_groups_pct_source = ColumnDataSource(lang_group_pct)

    f = figure(
        y_range=(0, 100),
        plot_width=700,
        plot_height=500
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
    f.legend.border_line_color = 'black'
    f.legend.background_fill_alpha = 1
    f.title.align = 'center'
    f.title.text_font_size = '20pt'
    f.xaxis.major_label_text_font_size = '16pt'
    f.yaxis.major_label_text_font_size = '16pt'

    hover = HoverTool(tooltips=[
        ("year", "@year"),
        ("Finnish", "@finnish{0.0 a}"),
        ("Russian", "@russian{0.0 a}"),
        ("Swedish", "@swedish{0.0 a}"),
        ("German", "@german{0.0 a}"),
        ("Other", "@other{0.0 a}")
    ])

    f.add_tools(hover)
    output_file(r'../figures/language_groups_percentages.html')
    show(f)
