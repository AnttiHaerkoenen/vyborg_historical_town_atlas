import rasterio


def clip_histogram(file, min=9999, max=9999):
    with rasterio.open(file) as src:
        print(src.width, src.height)
        print(src.crs)
        print(src.transform)
        print(src.count)
        print(src.indexes)


if __name__ == '__main__':
    clip_histogram(file='WorldDEM_Vyborg.tif')
