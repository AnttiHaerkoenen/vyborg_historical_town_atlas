import rasterio


def clip_histogram(file, min=9999, max=9999):
    with rasterio.open(file) as raster:
        pass


if __name__ == '__main__':
    clip_histogram()
