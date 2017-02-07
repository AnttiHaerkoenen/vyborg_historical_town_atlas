#!/usr/bin/env python

import os

import rasterio


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
    print("******************************\n"
          "*** Raster clipping script ***\n"
          "******************************\n")

    while True:
        input_file = input("Input original raster file: ")
        if not input_file:
            return
        output_file = input("Input new raster file: ")
        if not output_file:
            return

        if os.path.isfile(input_file) and os.path.isfile(output_file):
            break

        print("File(s) do not exist")

    while True:
        max_val = input("Input maximum cell value: ")
        min_val = input("Input minimum cell value: ")

        try:
            max_val = int(max_val) if max_val else None
            min_val = int(min_val) if min_val else None
            break
        except ValueError:
            print("Incorrect value! Enter a number.")

    if max_val not in range(-32767, 32768):
        max_val = 32768

    if min_val not in range(-32767, 32768):
        min_val = -32767

    clip_histogram(input_file, output_file, min_val, max_val)
    print("Raster manipulation succesfull.")


if __name__ == '__main__':
    main()
