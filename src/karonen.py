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
from bokeh.palettes import magma
from bokeh.models import (
    HoverTool,
    GeoJSONDataSource,
    LinearColorMapper,
    Title,
    ColorBar,
    BasicTicker
)
from bokeh.client import pull_session
from bokeh.embed import server_session
from flask import Flask, render_template

from src.util import *


def make_mosaic() -> figure:
    pass


if __name__ == '__main__':
    pass
