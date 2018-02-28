import os


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


if __name__ == '__main__':
    os.chdir(r'../data')
    data_ = pd.read_csv('population_1570.csv', index_col=0)
    palette = Category10_10[:len(data_)]
    data_['colors'] = palette
    groups = [g for g in data_.index]
    water = gpd.read_file('water_clip.shp')

    water = get_xy(multipolygons_to_polygons(water))
    water_src = GeoJSONDataSource(geojson=water.to_json())

    islands = gpd.read_file('islands.shp')
    islands = get_xy(multipolygons_to_polygons(islands))
    islands_src = GeoJSONDataSource(geojson=islands.to_json())

    fig = figure(
        plot_height=750,
        plot_width=700,
        x_axis_location=None,
        y_axis_location=None,
        y_range=(60.7, 60.72),
        x_range=(28.72, 28.745),
    )

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

    mosaic_data = get_mosaic(data_, data_col='i', x=28.729, y=60.712, height=0.0011, width=0.002)
    fig.patches(**mosaic_data)

    for group, color in zip(groups, palette):
        fig.circle(x=[], y=[], fill_color=color, legend=group)
    fig.legend.location = 'bottom_left'
    fig.legend.background_fill_alpha = 1
    fig.legend.border_line_color = 'black'

    output_file(r'../figures/karonen.html')

    show(fig)
