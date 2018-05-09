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

from src.util import *


if __name__ == '__main__':
    os.chdir('..\data')
    logging.basicConfig(level=logging.INFO)

    geo_data = gpd.read_file('districts_1929.shp')
    pop_data = pd.read_csv('pop_1900s.csv')

    output_file(r'../figures/population_by_district.html')
