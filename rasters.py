import rasterio


def clip_histogram(input_file, output_file, min=9999, max=9999):
    with rasterio.open(input_file) as fin:
        b = fin.read(1)
        image = fin.read()
        h, w = fin.shape

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
    clip_histogram(input_file='WorldDEM_Vyborg.tif', output_file='output.tif')
