import os
import logging
import json
from typing import Sequence
from datetime import datetime

import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, Point
from bokeh.plotting import figure
from bokeh.models import Title


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


def combine_data_to_file(
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


def combine_data(
        shp_fp: str,
        stats_fp: str,
        shp_on: str=None,
        stats_on: str=None,
        sheet: str or int=None,
        **kwargs
) -> gpd.GeoDataFrame or None:
    """
    Combines spatial and non-spatial data from files using pandas.DataFrame and geopandas.GeoDataFrame.
    :param shp_fp: Filepath to spatial data (shapefile)
    :param stats_fp: Filepath to non-spatial data (csv, xls, xlsx)
    :param shp_on: Which column of spatial data to use in join
    :param stats_on: Which column of non-spatial data to use in join
    :param sheet: which excel sheet to use
    :param kwargs: Additional arguments for pandas.DataFrame.join
    :return: geopandas.GeoDataFrame with joined data
    """
    data_ = gpd.read_file(shp_fp)
    with open(shp_fp.replace('.shp', '.prj')) as crs_fin:
        crs_ = crs_fin.readline().strip()

    stats_format = stats_fp.split('.', maxsplit=1)[1]
    if stats_format == 'csv':
        data_stats = pd.read_csv(stats_fp)
    elif stats_format in ('xls', 'xlsx'):
        data_stats = pd.read_excel(stats_fp, sheet_name=sheet)
    else:
        logging.error(f'combine_data: {stats_format} is not supported data format')
        return None

    if shp_on:
        try:
            data_ = data_.set_index(shp_on)
        except KeyError:
            logging.error(f"{shp_on} is wrong key. Check spelling")
            return None
    if stats_on:
        try:
            data_stats = data_stats.set_index(stats_on)
        except KeyError:
            logging.error(f"{stats_on} is wrong key. Check spelling")
            return None

    data_ = data_.join(data_stats, **kwargs)
    return data_.reset_index()


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

    data_.columns = pd.Index([remove_umlauts(c) for c in data_.columns])
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


def multipolygons_to_polygons(
        geodataframe: gpd.GeoDataFrame,
        geometry_column='geometry',
        min_area=0
) -> gpd.GeoDataFrame:
    """
    Turns rows with MultiPolygons into groups of rows with single Polygon each.
    :param geodataframe:
    :param geometry_column: Column containing Polygons and Multipolygons.
    :param min_area: Size of Polygons to be removed
    :return: enlargened geodataframe with each Polygon in its own row
    """
    new_geodataframe = gpd.GeoDataFrame(columns=geodataframe.columns)
    for _, row in geodataframe.iterrows():
        geom = row[geometry_column]
        if geom.type == 'Polygon':
            new_geodataframe = new_geodataframe.append(row)
        elif geom.type == 'MultiPolygon':
            for poly in geom:
                new_row = row.copy()
                new_row[geometry_column] = poly
                if poly.area >= min_area:
                    new_geodataframe = new_geodataframe.append(new_row)
    return gpd.GeoDataFrame(new_geodataframe.reset_index())


def get_xy(geodf: gpd.GeoDataFrame, geometry_col: str='geometry') -> gpd.GeoDataFrame:
    geodf['x'] = geodf[geometry_col].apply(lambda geom: tuple(geom.exterior.coords.xy[0]))
    geodf['y'] = geodf[geometry_col].apply(lambda geom: tuple(geom.exterior.coords.xy[1]))
    return geodf


def clip_shapefile_to_rectangle(
        *,
        target_fp: str,
        output_fp: str,
        x_range: Sequence,
        y_range: Sequence
) -> None:
    target = gpd.read_file(target_fp)
    crs_ = target.crs
    display_area = gpd.GeoDataFrame()
    display_area['geometry'] = None
    display_area.loc[0, 'geometry'] = Polygon([
        (x_range[0], y_range[1]),
        (x_range[1], y_range[1]),
        (x_range[1], y_range[0]),
        (x_range[0], y_range[0]),
    ])
    target = gpd.overlay(target, display_area, how='intersection')
    target.crs = crs_
    print(target)
    target.to_file(output_fp)


def set_gdal():
    if 'GDAL_DATA' not in os.environ:
        os.environ['GDAL_DATA'] = r'C:\Users\antth\AppData\Local\Continuum\anaconda3\Library\share\gdal'


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    os.chdir('..\data')

    polygon_to_point('districts_1928.shp')
    combine_data_to_file(
        'districts_1928_to_point.shp',
        'population_1870_1890.xlsx',
        stats_on='Kaupunginosa',
        shp_on='NAME',
        how='inner'
    )
    shp_to_geojson('districts_1928_to_point_population_1870_1890.shp')
