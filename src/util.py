import os
import logging

import geopandas as gpd


def shp_to_geojson(input_fp, geojson_fp=None, to_epsg=4326):
    if not geojson_fp:
        geojson_fp = '{0}.geojson'.format(input_fp.split('.')[0])
    data_ = gpd.read_file(input_fp)
    data_ = data_.to_crs(epsg=to_epsg)
    data_.to_file(geojson_fp)
    logging.info(f"Data written to file {geojson_fp}.")


if __name__ == '__main__':
    pass
