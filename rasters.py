import rasterio


def clip_histogram(file, min=9999, max=9999):
    with rasterio.open(file) as file:
        print(file.width, file.height)
        print(file.crs)
        print(file.transform)
        print(file.count)
        print(file.indexes)


if __name__ == '__main__':
    clip_histogram()
