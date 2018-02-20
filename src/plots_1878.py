import os
import logging
from datetime import datetime

import geopandas as gpd
import pandas as pd
import numpy as np
from bokeh.plotting import figure, show, save
from bokeh.palettes import Category10_9 as palette
from bokeh.transform import factor_cmap
from bokeh.models import (
    HoverTool,
    GeoJSONDataSource,
    CategoricalColorMapper,
    Title,
    ColorBar,
    BasicTicker
)
import folium

from src.util import multipolygons_to_polygons, get_xy

district_name_mapper = {
    '1': 'Linnoitus',
    '2': 'P. Annan kruunu (Siikaniemi)',
    '3': 'Salakkalahti',
    '4': 'Repola',
    '5': 'Pantsarlahti',
    '6': 'Kaleva',
    '7': 'Papula',
    '8': 'Saunalahti',
    '10': 'Neitsytniemi'
}


def plot_plots_folium(fp_plots, title):
    plots = gpd.read_file(fp_plots)
    plots = get_xy(plots)
    plots['district_name'] = plots.DISTRICT.map(district_name_mapper)

    map_ = folium.Map(
        location=[60.71, 28.73],
        zoom_start=14,
        tiles='Stamen Terrain',
    )
    folium.GeoJson(
        plots.to_json()
    ).add_to(map_)
    folium.LayerControl().add_to(map_)

    return map_


def plot_plots_bokeh(fp_plots, title=None, **kwargs):
    water = gpd.read_file('water.shp')
    water = get_xy(multipolygons_to_polygons(water))
    water_src = GeoJSONDataSource(geojson=water.to_json())

    islands = gpd.read_file('islands.shp')
    islands = get_xy(multipolygons_to_polygons(islands))
    islands_src = GeoJSONDataSource(geojson=islands.to_json())

    plots = gpd.read_file(fp_plots)
    plots = get_xy(plots)
    plots['district_name'] = plots.DISTRICT.map(district_name_mapper)
    plots_src = GeoJSONDataSource(geojson=plots.to_json())

    factors = list(district_name_mapper.values())
    color_mapper = factor_cmap(
        'district_name',
        palette=palette,
        factors=factors,
    )

    fig = figure(
        title=title,
        x_axis_location=None,
        y_axis_location=None,
        y_range=(60.70, 60.73),
        x_range=(28.70, 28.77),
        **kwargs
    )
    if title:
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
    )
    hover = HoverTool(renderers=[plots_patch])
    hover.tooltips = [
        ('kaupunginosa', '@district_name'),
        ('numero', '@NUMBER'),
        ('koordinaatit', '($y, $x)'),
    ]
    fig.add_tools(hover)

    for factor, color in zip(factors, palette):
        fig.circle(x=[], y=[], fill_color=color, legend=factor)
    fig.legend.location = 'bottom_left'

    return fig


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    os.chdir(r'..\data')
    fig = plot_plots_bokeh(
        'plots_1878.shp',
        plot_height=650,
        plot_width=800,
    )
    os.chdir(r'..\figures')
    show(fig)
    save(fig, filename='plots_1878.html', title='Cadastral plots of Vyborg 1878')
