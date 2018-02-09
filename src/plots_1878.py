import os
import logging
from datetime import datetime

import geopandas as gpd
import pandas as pd
import numpy as np
from bokeh.plotting import figure, show
from bokeh.palettes import Spectral9
from bokeh.transform import factor_cmap
from bokeh.models import (
    HoverTool,
    GeoJSONDataSource,
    CategoricalColorMapper,
    Title,
    ColorBar,
    BasicTicker
)

from src.util import multipolygons_to_polygons, get_xy


def plot_plots(fp_plots, title):
    water = gpd.read_file('water.shp')
    water = get_xy(multipolygons_to_polygons(water))
    water_src = GeoJSONDataSource(geojson=water.to_json())

    islands = gpd.read_file('islands.shp')
    islands = get_xy(multipolygons_to_polygons(islands))
    islands_src = GeoJSONDataSource(geojson=islands.to_json())

    plots = gpd.read_file(fp_plots)
    plots = get_xy(plots)
    plots_src = GeoJSONDataSource(geojson=plots.to_json())

    factors = sorted(list(set(plots['DISTRICT'])))
    color_mapper = factor_cmap(
        'DISTRICT',
        palette=Spectral9,
        factors=factors,
    )

    fig = figure(
        title=title,
        x_axis_location=None,
        y_axis_location=None,
        y_range=(60.70, 60.74),
        x_range=(28.69, 28.77),
    )
    fig.title.text_font_size = "20px"
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
    plots_patch = fig.patches(
        xs='x',
        ys='y',
        source=plots_src,
        fill_color=color_mapper,
        fill_alpha=0.8,
        line_color='black',
        line_width=0.8,
        legend=factors
    )
    hover = HoverTool(renderer=plots_patch)
    hover.tooltips = [
        ('kaupunginosa', '@DISTRICT'),
        ('numero', '@NUMBER'),
        ('koordinaatit', '($y, $x)'),
    ]
    fig.add_tools(hover)

    return fig


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    os.chdir('..\data')
    fig = plot_plots('plots_1878.shp', 'Tontit 1878')
    show(fig)
