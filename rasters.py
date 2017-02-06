import rasterio
import numpy as np


def clip_histogram(input_file, output_file, min_val=-32767, max_val=32768):
    try:
        with rasterio.open(input_file) as fin:
            b = fin.read(1)
            image = fin.read()
            h, w = fin.shape
            m1 = image < min_val
            m2 = image > max_val
            image[m1] = min_val
            image[m2] = max_val
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
            dtype=b.dtype
        ) as fout:
            fout.write(image)
    except IOError as ioe:
        raise ioe


def main():
    print("******************************"
          "*** Raster clipping script ***"
          "******************************")

    input_file = input("Input original raster file: ")
    output_file = input("Input new raster file: ")
    max_val = input("Input maximum cell value: ")
    min_val = input("Input minimum cell value: ")

    if int(max_val) not in np.arange(-32767, 32768):
        max_val = 32768

    if int(min_val) not in np.arange(-32767, 32768):
        min_val = -32767

    try:
        clip_histogram(input_file, output_file, min_val, max_val)
        print("Raster manipulation succeeded.")
    except IOError as ioe:
        print(ioe)


if __name__ == '__main__':
    main()
