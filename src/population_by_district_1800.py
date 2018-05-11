import os
import logging
from datetime import datetime
import time

import geopandas as gpd
import pandas as pd
import numpy as np
from bokeh.plotting import figure, show, output_file
from bokeh.layouts import gridplot
from bokeh.palettes import magma
from bokeh.models import (
    HoverTool,
    GeoJSONDataSource,
    LinearColorMapper,
    Title,
    ColorBar,
    BasicTicker,
)

from src.util import *


def plot_population_by_district(
        year,
        group,
        low: float=0,
        high: float=100,
        step: float=5,
        copyright_=False,
        title=None,
        y_range=None,
        x_range=None,
) -> figure:
    palette = magma(np.ceil((high - low) / step))
    palette = list(reversed(palette))
    year = str(year)

    water = gpd.read_file('water_clip.shp')
    water = get_xy(multipolygons_to_polygons(water))
    water_src = GeoJSONDataSource(geojson=water.to_json())

    islands = gpd.read_file('islands.shp')
    islands = get_xy(multipolygons_to_polygons(islands))
    islands_src = GeoJSONDataSource(geojson=islands.to_json())

    districts = combine_data(
        'districts.shp',
        'population_1870_1890.xlsx',
        sheet=year,
        shp_on='NAME',
        stats_on='Kaupunginosa',
        how='left'
    )
    districts.columns = pd.Index([remove_umlauts(col.lower()) for col in districts.columns])

    kielet = ['suomi', 'ruotsi', 'venaja', 'saksa', 'ranska', 'englanti', 'viro',
                'unkari', 'jiddish', 'tataari', 'romani', 'ilmoittamatta']
    for col in kielet:
        districts[f'{col}_pct'] = districts[col] / districts['yhteensa'] * 100

    districts = districts[districts['yhteensa'] > 0]
    districts = get_xy(districts)
    districts = districts.fillna(0)

    districts_src = GeoJSONDataSource(geojson=districts.to_json())
    color_mapper = LinearColorMapper(
        palette=palette,
        low=low,
        high=high
    )

    fig = figure(
        title=title,
        x_axis_location=None,
        y_axis_location=None,
        y_range=(60.69, 60.738),
        x_range=(28.688, 28.78),
    )
    fig.title.text_font_size = "20px"
    fig.grid.grid_line_color = None
    pvm = datetime.date(datetime.now())
    if copyright_:
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
    district_patch = fig.patches(
        xs='x',
        ys='y',
        source=districts_src,
        fill_color={
            'field': group,
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

    hover = HoverTool(renderers=[district_patch])
    hover.tooltips = [
        ('Kaupunginosa', '@name'),
        ('Väkiluku', '@yhteensa'),
        ('suomi', '@suomi_pct{0.0 a}'),
        ('ruotsi', '@ruotsi_pct{0.0 a}'),
        ('venäjä', '@venaja_pct{0.0 a}'),
        ('saksa', '@saksa_pct{0.0 a}'),
        ('jiddish', '@jiddish_pct{0.0 a}'),
        ('koordinaatit', '($y, $x)'),
    ]
    fig.add_tools(hover)
    return fig


if __name__ == '__main__':
    os.chdir('..\data')
    logging.basicConfig(level=logging.INFO)
    set_gdal()
    group = 'suomi_pct'
    min_ = 40
    max_ = 90
    step = 5
    y_range = 60.69, 60.738
    x_range = 28.688, 28.78
    # clip_shapefile_to_rectangle(target_fp='water.shp', output_fp='water_clip.shp', y_range=y_range, x_range=x_range)

    fig1 = plot_population_by_district(
        1870,
        group,
        low=min_,
        high=max_,
        step=step,
        title='1870',
        y_range=y_range,
        x_range=x_range,
    )
    fig2 = plot_population_by_district(
        1880,
        group,
        low=min_,
        high=max_,
        step=step,
        title='1880',
        y_range=x_range,
        x_range=y_range,
    )
    fig3 = plot_population_by_district(
        1890,
        group,
        low=min_,
        high=max_,
        step=step,
        title='1890',
        y_range=x_range,
        x_range=y_range,
    )

    output_file(r'../figures/population_by_district.html')
    show(gridplot([fig1, fig2, fig3], ncols=1))
