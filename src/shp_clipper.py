#!/usr/bin/env python

import os

import fire
import geopandas as gpd


def clip_shp(
        input_file,
        clip_file,
        output_file=None,
):
    if not output_file:
        input_file_basename = input_file[:input_file.rindex('.')]
        output_file = f"{input_file_basename}_clip.shp"

    target: gpd.GeoDataFrame = gpd.read_file(input_file)
    clip: gpd.GeoDataFrame = gpd.read_file(clip_file)
    target = target.to_crs(epsg=4326)
    clip = clip.to_crs(epsg=4326)

    clip_poly = clip.geometry.unary_union
    target = target[target.geometry.intersects(clip_poly)]
    target['geometry'] = target['geometry'].intersection(clip_poly)

    target.to_file(output_file)
    print("Clipping successful")


if __name__ == '__main__':
    fire.Fire(clip_shp)
