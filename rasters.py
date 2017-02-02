import rasterio
import numpy as np


def clip_histogram(input_file, output_file, min_val=-32767, max_val=32768):
    with rasterio.open(input_file) as fin:
        b = fin.read(1)
        image = fin.read()
        h, w = fin.shape
        m1 = image < min_val
        m2 = image > max_val
        image[m1] = min_val
        image[m2] = max_val

    with rasterio.open(
            output_file,
            'w',
            driver='GTiff',
            width=w,
            height=h,
            count=1,
            dtype=b.dtype
    ) as fout:
        fout.write(image)


if __name__ == '__main__':
    clip_histogram(input_file='WorldDEM_Vyborg.tif', output_file='output.tif', min_val=0)
