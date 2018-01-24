import os
import logging

import geopandas as gpd
from shapely.geometry import Polygon, Point


def shp_to_geojson(input_fp: str, geojson_fp: str=None, to_epsg: int=4326) -> None:
    if not geojson_fp:
        geojson_fp = '{0}.geojson'.format(input_fp.split('.')[0])
    data_ = gpd.read_file(input_fp)
    data_ = data_.to_crs(epsg=to_epsg)
    data_.to_file(geojson_fp)
    logging.info(f"Data written to file {geojson_fp}.")


def polygon_to_point(input_fp: str, output_fp: str=None) -> None:
    if not output_fp:
        output_fp = '{0}_to_point.shp'.format(input_fp.split('.')[0])
    data_ = gpd.read_file(input_fp)
    data_.to_file(output_fp)
    logging.info(f"Data written to file {output_fp}.")


if __name__ == '__main__':
    pass
