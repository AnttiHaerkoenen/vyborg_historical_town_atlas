import os
import logging
import json
from typing import Sequence

import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, Point


def polygon_to_point(
        input_fp: str,
        output_fp: str=None
) -> None:
    if not output_fp:
        fp, ending = input_fp.split('.', maxsplit=1)
        output_fp = f'{fp}_to_point.{ending}'
    with open(input_fp.replace('.shp', '.prj')) as crs_fin:
        crs_ = crs_fin.readline().strip()
    data_ = gpd.read_file(input_fp)
    data_['geometry'] = data_['geometry'].apply(lambda poly: poly.centroid)
    data_.to_file(output_fp, crs_wkt=crs_, encoding='utf-8')
    logging.info(f"polygon_to_point: Data written to file {output_fp}.")


def combine_data(
        shp_fp: str,
        stats_fp: str,
        output_fp: str=None,
        stats_on: str=None,
        **kwargs
) -> None:
    if not output_fp:
        output_fp = '{0}_{1}.shp'.format(shp_fp.split('.')[0], stats_fp.split('.')[0])
    data_ = gpd.read_file(shp_fp)
    with open(shp_fp.replace('.shp', '.prj')) as crs_fin:
        crs_ = crs_fin.readline().strip()

    stats_format = stats_fp.split('.', maxsplit=1)[1]
    if stats_format == 'csv':
        data_stats = pd.read_csv(stats_fp)
    elif stats_format in ('xls', 'xlsx'):
        data_stats = pd.read_excel(stats_fp)
    else:
        logging.error(f'combine_data: {stats_format} is not supported data format')
        return

    if stats_on:
        data_stats = data_stats.set_index(stats_on)

    data_ = data_.join(data_stats, **kwargs)
    data_.to_file(output_fp, crs_wkt=crs_, encoding='utf-8')
    logging.info(f"combine_data: Data written to file {output_fp}.")


def shp_to_geojson(
        input_fp: str,
        geojson_fp: str=None,
        to_epsg: int=4326,
        columns: Sequence[str]=None
) -> None:
    if not geojson_fp:
        geojson_fp = '{0}.geojson'.format(input_fp.split('.')[0])

    with open(input_fp.replace('.shp', '.prj')) as crs_fin:
        crs_ = crs_fin.readline().strip()
    data_ = gpd.read_file(input_fp)
    crs_ = data_.crs
    data_ = data_.to_crs(epsg=to_epsg)
    logging.info(f'Coordinates transformed from EPSG {crs_} to {to_epsg}.')

    data_.columns = [remove_umlauts(c) for c in data_.columns]
    data_ = data_.applymap(remove_umlauts)

    if not columns:
        columns = data_.columns.drop('geometry')
    geojson = {
        'type': 'FeatureCollection',
        'features': [],
    }
    for _, row in data_.iterrows():
        feature = {
            'type': 'Feature',
            'properties': {},
        }
        point = row['geometry']
        feature['geometry'] = {
            'type': 'Point',
            'coordinates': [point.x, point.y]
        }
        for col in columns:
            feature['properties'][col] = row[col]
        geojson['features'].append(feature)

    with open(geojson_fp, 'w') as fout:
        json.dump(geojson, fout, indent=2)
    logging.info(f"shp_to_geojson: Data written to file {geojson_fp}.")


def remove_umlauts(text):
    if isinstance(text, str):
        text = text.replace('ä', 'a').replace('ö', 'o')
    return text


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    os.chdir(r'..\data')

    polygon_to_point('districts_1928.shp')
    combine_data(
        'districts_1928_to_point.shp',
        'population_1870_1890.xlsx',
        stats_on='Kaupunginosa',
        on='NAME',
        how='inner'
    )
    shp_to_geojson('districts_1928_to_point_population_1870_1890.shp')
