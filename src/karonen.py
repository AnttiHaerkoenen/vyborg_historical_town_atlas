import os
import logging
from datetime import datetime
import time

import squarify
import geopandas as gpd
import pandas as pd
import numpy as np
from bokeh.plotting import figure, show, output_file
from bokeh.layouts import gridplot
from bokeh.palettes import Category10_10 as palette
from bokeh.models import (
    HoverTool,
    GeoJSONDataSource,
    Title,
    BasicTicker
)
from bokeh.client import pull_session
from bokeh.embed import server_session
from flask import Flask, render_template

from src.util import *


def get_mosaic(data_: pd.DataFrame, *, data_col: str, x=0, y=0, width, height) -> dict:
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
    data_['colors'] = palette[:len(data_)]

    fig = figure(
        plot_width=600,
        plot_height=600,
    )
    mosaic_data = get_mosaic(data_, data_col='iii', x=0, y=0, height=100, width=100)
    fig.patches(**mosaic_data)
    mosaic_data = get_mosaic(data_, data_col='ii', x=120, y=120, height=100, width=100)
    fig.patches(**mosaic_data)
    mosaic_data = get_mosaic(data_, data_col='iv', x=120, y=0, height=100, width=100)
    fig.patches(**mosaic_data)
    mosaic_data = get_mosaic(data_, data_col='i', x=0, y=120, height=100, width=100)
    fig.patches(**mosaic_data)
    print(data_)

    output_file(r'../figures/karonen.html')

    show(fig)
