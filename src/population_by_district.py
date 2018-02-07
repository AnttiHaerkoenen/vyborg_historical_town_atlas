import os
import logging
from datetime import datetime

import geopandas as gpd
import pandas as pd
import numpy as np
from bokeh.plotting import figure, show
from bokeh.palettes import magma
from bokeh.models import (
    HoverTool,
    GeoJSONDataSource,
    LinearColorMapper,
    Title,
    ColorBar,
    BasicTicker
)

from src.util import combine_data, remove_umlauts, multipolygons_to_polygons, get_xy


def plot_population_by_district(year, low=0, high=100) -> figure:
    palette = magma(np.ceil((high - low) / 5))
    palette = list(reversed(palette))
    year = str(year)

    os.chdir('..\data')

    water = gpd.read_file('water.shp')
    water = get_xy(multipolygons_to_polygons(water))
    water_src = GeoJSONDataSource(geojson=water.to_json())

    islands = gpd.read_file('islands.shp')
    islands = get_xy(multipolygons_to_polygons(islands))
    islands_src = GeoJSONDataSource(geojson=islands.to_json())

    data_ = combine_data(
        'districts.shp',
        'population_1870_1890.xlsx',
        sheet=year,
        shp_on='NAME',
        stats_on='Kaupunginosa',
        how='left'
    )
    data_.columns = pd.Index([remove_umlauts(col.lower()) for col in data_.columns])

    kielet = ['suomi', 'ruotsi', 'venaja', 'saksa', 'ranska', 'englanti', 'viro',
                'unkari', 'jiddish', 'tataari', 'romani', 'ilmoittamatta']
    for col in kielet:
        data_[f'{col}_pct'] = data_[col] / data_['yhteensa'] * 100

    data_ = data_[data_['yhteensa'] > 0]
    data_ = get_xy(data_)
    data_ = data_.fillna(0)

    districts_src = GeoJSONDataSource(geojson=data_.to_json())
    color_mapper = LinearColorMapper(
        palette=palette,
        low=low,
        high=high
    )
    fig = figure(
        title=f'Ortodoksien osuus Viipurin väestöstä {year}',
        x_axis_location=None,
        y_axis_location=None,
        y_range=(60.69, 60.738),
        x_range=(28.688, 28.78),
    )
    fig.title.text_font_size = "20px"
    fig.grid.grid_line_color = None
    pvm = datetime.date(datetime.now())
    fig.add_layout(Title(text=f"© Antti Härkönen {pvm}", align="left"), "below")

    fig.patches(
        xs='x',
        ys='y',
        source=water_src,
        fill_color='#59d0ff',
        fill_alpha=0.8,
        line_color=None,
        line_width=0,
    )
    fig.patches(
        xs='x',
        ys='y',
        source=islands_src,
        fill_color='white',
        line_color=None,
        line_width=0
    )
    fig.patches(
        xs='x',
        ys='y',
        source=districts_src,
        fill_color={
            'field': 'venaja_pct',
            'transform': color_mapper,
        },
        fill_alpha=0.8,
        line_color='black',
        line_width=0.8,
    )

    color_bar = ColorBar(
        color_mapper=color_mapper,
        ticker=BasicTicker(),
        label_standoff=12,
        border_line_color=None,
        location=(0, 0)
    )
    fig.add_layout(
        color_bar,
        'right'
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


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    plot_population_by_district(1890, 0, 55)
