import os
import logging

import geopandas as gpd
import pandas as pd
from bokeh.plotting import figure, show
from bokeh.palettes import RdYlGn8 as palette
from bokeh.models import (
    HoverTool,
    GeoJSONDataSource,
    LinearColorMapper,
    Title
)

from src.util import combine_data


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    os.chdir('..\data')
    data_ = combine_data(
        'districts_1928.shp',
        'population_1870_1890.xlsx',
        sheet='1890',
        shp_on='NAME',
        stats_on='Kaupunginosa',
        how='left'
    )
    data_.columns = [col.lower() for col in data_.columns]
    data_['total'] = data_.loc[:, ['suomi', 'ruotsi', 'venäjä', 'saksa',
                                   'puola', 'ranska', 'englanti', 'viro',
                                   'unkari', 'latvia', 'jiddish', 'tataari',
                                   'romani', 'lätti', 'ilmoittamatta']].sum(axis=1)
    for col in ['suomi', 'ruotsi', 'venäjä', 'saksa',
                'puola', 'ranska', 'englanti', 'viro',
                'unkari', 'latvia', 'jiddish', 'tataari',
                'romani', 'lätti', 'ilmoittamatta', 'luterilaisia',
                'reformoituja', 'ortodokseja', 'katolilaisia', 'muita kristittyjä',
                'juutalaisia', 'muslimeja']:
        data_[f'{col}_pct'] = data_[col] / data_['total'] * 100
    data_ = data_.fillna('0')
    data_['x'] = data_['geometry'].apply(lambda geom: tuple(geom.exterior.coords.xy[0]))
    data_['y'] = data_['geometry'].apply(lambda geom: tuple(geom.exterior.coords.xy[1]))
    districts_src = GeoJSONDataSource(geojson=data_.to_json())
    color_mapper = LinearColorMapper(palette=palette)
    fig = figure(
        title='Viipurin väestö',
        x_axis_location=None,
        y_axis_location=None
    )
    print(data_.columns)
    print(data_.describe())
    print(data_.head())
    fig.title.text_font_size = "20px"
    fig.grid.grid_line_color = None
    fig.add_layout(Title(text="© Antti Härkönen", align="left"), "below")
    fig.patches(
        xs='x',
        ys='y',
        source=districts_src,
        fill_color={
            'field': 'ortodokseja_pct',
            'transform': color_mapper,
        },
        fill_alpha=0.9,
        line_color='black',
        line_width=0.8
    )
    hover = HoverTool()
    hover.tooltips = [
        ('Kaupunginosa', '@name'),
        ('Väkiluku', '@total'),
        ('Ortodoksien osuus', '@ortodokseja_pct{0.0 a}'),
        ('Juutalaisten osuus', '@juutalaisia_pct{0.0 a}'),
    ]
    fig.add_tools(hover)
    show(fig)
