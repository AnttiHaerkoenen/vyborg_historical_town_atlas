import os
import logging

import geopandas as gpd
import pandas as pd

from src.util import combine_data


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    os.chdir('..\data')
    data_ = combine_data(
        'districts_1928.shp',
        'population_1870_1890.xlsx',
        sheet='1870',
        shp_on='NAME',
        stats_on='Kaupunginosa',
        how='inner'
    )
    print(data_)
