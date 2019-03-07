#!/usr/bin/env python

import rasterio
import fire


def clip_histogram(input_file, output_file, min_val=-32767, max_val=32768):
    if max_val not in range(-32767, 32768):
        max_val = 32768

    if min_val not in range(-32767, 32768):
        min_val = -32767

    try:
        with rasterio.open(input_file, driver='GTiff') as fin:
            b = fin.read(1)
            image = fin.read()
            h, w = fin.shape
            m1 = image < min_val
            m2 = image > max_val
            image[m1] = min_val
            image[m2] = max_val
            dtype_ = b.dtype
    except IOError as ioe:
        raise ioe

    try:
        with rasterio.open(
            output_file,
            'w',
            driver='GTiff',
            width=w,
            height=h,
            count=1,
            dtype=dtype_
        ) as fout:
            fout.write(image)
    except IOError as ioe:
        raise ioe
    except TypeError as type:
        raise type

    print("Raster manipulation successful.")


if __name__ == '__main__':
    fire.Fire(clip_histogram)
