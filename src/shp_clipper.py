#!/usr/bin/env python

import os

import fire
import geopandas as gpd


def clip_shp(
        input_file,
        clip_file,
        output_file=None,
):
    if input_file == clip_file:
        return
    if not output_file:
        if not os.path.isdir(r"./clipped"):
            os.mkdir(r"clipped")
        input_file_basename = os.path.basename(input_file).split('.')[0]
        output_file = f"clipped/{input_file_basename}.shp"

    target: gpd.GeoDataFrame = gpd.read_file(input_file)
    clip: gpd.GeoDataFrame = gpd.read_file(clip_file)

    if target.crs != clip.crs:
        clip = clip.to_crs(target.crs)

    clip_poly = clip.geometry.unary_union
    target = target[target.geometry.intersects(clip_poly)]
    target['geometry'] = target['geometry'].intersection(clip_poly)

    if target.is_empty:
        print(f"{input_file}: No features in clip area")
    else:
        target.to_file(output_file)
        print(f"{input_file}: Clipping successful")

        
if __name__ == '__main__':
    fire.Fire(clip_shp)
