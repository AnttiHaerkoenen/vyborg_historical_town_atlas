import os
from collections import namedtuple

import squarify
import geopandas as gpd
import pandas as pd
import numpy as np
from bokeh.plotting import figure, show, output_file
from bokeh.layouts import gridplot
from bokeh.palettes import Category10_10
from bokeh.models import (
    HoverTool,
    GeoJSONDataSource,
    Title,
    BasicTicker
)

from src.util import *

Coordinates = namedtuple('Coordinates', 'x y')


def get_mosaic(data_: pd.DataFrame, *, data_col: str, x=0.0, y=0.0, width, height) -> dict:
    data = data_.sort_values(by=data_col, ascending=False)
    data = data.loc[data[data_col] > 0]
    rectangles = squarify.normalize_sizes(list(data[data_col]), width, height)
    rectangles = squarify.squarify(rectangles, x, y, width, height)
    xs = [[
        r['x'],
        r['x'] + r['dx'],
        r['x'] + r['dx'],
        r['x'],
    ] for r in rectangles]

    ys = [[
        r['y'] + r['dy'],
        r['y'] + r['dy'],
        r['y'],
        r['y'],
    ] for r in rectangles]

    colors = [c for c in data['colors']]

    return {
        'xs': xs,
        'ys': ys,
        'color': colors,
    }


def draw_population_map(
        *,
        population_file,
        water_file,
        islands_file,
        districts_file,
        locations,
        size,
        **kwargs
):
    data_ = pd.read_csv(population_file, index_col=0)
    totals = data_.sum(axis=0)
    palette = Category10_10[:len(data_)]
    data_['colors'] = palette
    groups = [g for g in data_.index]

    water = gpd.read_file(water_file)
    water = get_xy(multipolygons_to_polygons(water))
    water_src = GeoJSONDataSource(geojson=water.to_json())

    islands = gpd.read_file(islands_file)
    islands = get_xy(multipolygons_to_polygons(islands))
    islands_src = GeoJSONDataSource(geojson=islands.to_json())

    districts = gpd.read_file(districts_file)
    districts = get_xy(districts)
    districts_src = GeoJSONDataSource(geojson=districts.to_json())

    fig = figure(**kwargs)

    fig.grid.grid_line_color = None

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
        fill_color=None,
        line_color='black',
        line_width=0
    )

    for col, loc in locations.items():
        width = size * np.sqrt(totals[col] / totals.max())
        mosaic_data = get_mosaic(
            data_,
            data_col=col,
            x=loc.x,
            y=loc.y,
            height=width * np.cos(loc.y * 0.01745),
            width=width,
        )
        fig.patches(**mosaic_data)

    for group, color in zip(groups, palette):
        fig.circle(x=[], y=[], fill_color=color, legend=group)
    fig.legend.location = 'bottom_left'
    fig.legend.background_fill_alpha = 1
    fig.legend.border_line_color = 'black'
    return fig


if __name__ == '__main__':
    os.chdir(r'../data')
    fig1 = draw_population_map(
        population_file='population_1570.csv',
        water_file='water_1698.shp',
        islands_file='islands_1698.shp',
        districts_file='districts_1637.shp',
        plot_height=900,
        plot_width=1000,
        x_axis_location=None,
        y_axis_location=None,
        y_range=(60.705, 60.717),
        x_range=(28.722, 28.743),
        size=0.0018,
        locations={
            'i': Coordinates(28.73, 60.7125),
            'ii': Coordinates(28.732, 60.7105),
            'iii': Coordinates(28.7315, 60.7137),
            'iv': Coordinates(28.734, 60.713),
            'Valli': Coordinates(28.738, 60.7105),
        },
    )
    fig2 = draw_population_map(
        population_file='population_1630.csv',
        water_file='water_1698.shp',
        islands_file='islands_1698.shp',
        districts_file='districts_1703.shp',
        plot_height=900,
        plot_width=1000,
        x_axis_location=None,
        y_axis_location=None,
        y_range=(60.705, 60.718),
        x_range=(28.72, 28.743),
        size=0.0025,
        locations={
            'Linnoitus': Coordinates(28.732, 60.7125),
            'Siikaniemi': Coordinates(28.7235, 60.7125),
            'Valli': Coordinates(28.738, 60.7105),
            'Pantsarlahti': Coordinates(28.738, 60.7057),
        },
    )

    output_file(r'../figures/karonen.html')

    show(fig2)
