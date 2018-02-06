import os
import logging

import geopandas as gpd
import pandas as pd
import numpy as np
from bokeh.plotting import figure, show
from bokeh.palettes import RdYlGn8 as palette
from bokeh.models import (
    HoverTool,
    GeoJSONDataSource,
    LinearColorMapper,
    Title
)

from src.util import combine_data, remove_umlauts


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    os.chdir('..\data')
    data_ = combine_data(
        'districts.shp',
        'population_1870_1890.xlsx',
        sheet='1890',
        shp_on='NAME',
        stats_on='Kaupunginosa',
        how='left'
    )
    data_.columns = pd.Index([remove_umlauts(col.lower()) for col in data_.columns])

    kielet = ['suomi', 'ruotsi', 'venaja', 'saksa', 'ranska', 'englanti', 'viro',
                'unkari', 'jiddish', 'tataari', 'romani', 'ilmoittamatta']
    for col in kielet:
        data_[f'{col}_pct'] = data_[col] / data_['yhteensa'] * 100

    data_['x'] = data_['geometry'].apply(lambda geom: tuple(geom.exterior.coords.xy[0]))
    data_['y'] = data_['geometry'].apply(lambda geom: tuple(geom.exterior.coords.xy[1]))
    type_change = {k: np.float64 for k in (kielet + [f'{k}_pct' for k in kielet])}
    data_ = data_.fillna(0)
    print(data_['venaja_pct'].describe())
    districts_src = GeoJSONDataSource(geojson=data_.to_json())
    color_mapper = LinearColorMapper(palette=palette)
    fig = figure(
        title='Viipurin väestö',
        x_axis_location=None,
        y_axis_location=None,
        y_range=(60.68, 60.738),
        x_range=(28.688, 28.80),
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
            'field': 'venaja_pct',
            'transform': color_mapper,
        },
        fill_alpha=0.9,
        line_color='black',
        line_width=0.8,
        legend='label'
    )
    hover = HoverTool()
    hover.tooltips = [
        ('Kaupunginosa', '@name'),
        ('Väkiluku', '@yhteensa'),
        ('Ortodoksien osuus', '@venaja_pct{0.0 a}'),
        ('Juutalaisten osuus', '@jiddish_pct{0.0 a}'),
        ('koordinaatit', '($y, $x)'),
    ]
    fig.add_tools(hover)
    show(fig)
