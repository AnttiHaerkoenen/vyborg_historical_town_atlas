import os
from collections import namedtuple

# import squarify
import geopandas as gpd
import pandas as pd
import numpy as np
from bokeh.plotting import figure, show, output_file
from bokeh.layouts import gridplot
from bokeh.palettes import Category10_10
from bokeh.io import export_png, export_svgs
from bokeh.models import (
    HoverTool,
    LabelSet,
    GeoJSONDataSource,
    ColumnDataSource,
    VBar)

from src.util import *

Coordinates = namedtuple('Coordinates', 'x y')


def get_mosaic(data_: pd.DataFrame, *, data_col: str, x=0.0, y=0.0, width, height) -> dict:
    """
    :param data_: DataFrame with data and color columns
    :param data_col: Name of the column with plotted data
    :param x: x coordinate for bottom right corner
    :param y: y coordinate for bottom right corner
    :param width: Width of plot
    :param height: Height of plot
    :return: Dictionary in the form:
        {
        'xs': list of lists of x coordinates in clockwise order,
        'ys': list of lists of y coordinated in clockwise order,
        'color': list(data['colors']),
        }
    """
    data = data_.sort_values(by=data_col, ascending=False)
    data = data.loc[data[data_col] > 0]
    rectangles = squarify.normalize_sizes(list(data[data_col]), width, height)
    rectangles = squarify.squarify(rectangles, x, y, width, height)
    xs = [[
        r['x'],
        r['x'] + r['dx'],
        r['x'] + r['dx'],
        r['x'],
    ] for r in rectangles]

    ys = [[
        r['y'] + r['dy'],
        r['y'] + r['dy'],
        r['y'],
        r['y'],
    ] for r in rectangles]

    return {
        'xs': xs,
        'ys': ys,
        'color': list(data['colors']),
    }


def get_bar(
        data: pd.DataFrame,
        *,
        data_col: str,
        x=0.0,
        y=0.0,
        width,
        height,
) -> dict:
    data = data.loc[data[data_col] > 0]
    heights = data[data_col] / data[data_col].sum() * height
    bars = len(heights)

    return {
        'x': [x + width * i for i in range(bars)],
        'top': [y + h for h in heights],
        'bottom': [y] * bars,
        'values': list(data[data_col]),
        'color': list(data['colors']),
    }


def get_stacked_bar(data: pd.DataFrame, *, data_col: str, x=0.0, y=0.0, width, height) -> dict:
    data = data.loc[data[data_col] > 0][::-1]
    lens = data[data_col] / data[data_col].sum() * height
    xs, ys = [], []
    last_y = y
    for len_ in lens:
        x_ = [
            x,
            x + width,
            x + width,
            x,
        ]
        xs.append(x_)
        y_ = [
            last_y + len_,
            last_y + len_,
            last_y,
            last_y,
        ]
        last_y += len_
        ys.append(y_)

    return {
        'xs': xs,
        'ys': ys,
        'color': list(data['colors']),
    }


def draw_population_map(
        *,
        population_file,
        water_file,
        islands_file,
        districts_file,
        locations,
        width,
        height=None,
        label_font_size,
        add_legend=False,
        legend_font_size,
        legend_padding,
        legend_spacing,
        kind,
        **kwargs
):
    kinds = 'mosaic', 'stacked bar', 'bar'
    if kind not in kinds:
        raise ValueError(f'Incorrect type parameter (Must be one of {kinds})')
    data_ = pd.read_csv(population_file, index_col=0)
    totals = data_.sum(axis=0)
    palette = Category10_10[:len(data_)]
    data_['colors'] = palette
    groups = [g for g in data_.index]

    water = gpd.read_file(water_file)
    water = get_xy(multipolygons_to_polygons(water))
    water_src = GeoJSONDataSource(geojson=water.to_json())

    islands = gpd.read_file(islands_file)
    islands = get_xy(multipolygons_to_polygons(islands))
    islands_src = GeoJSONDataSource(geojson=islands.to_json())

    districts = gpd.read_file(districts_file)
    districts = get_xy(districts)
    districts_src = GeoJSONDataSource(geojson=districts.to_json())

    fig = figure(**kwargs)

    fig.grid.grid_line_color = None

    fig.patches(
        xs='x',
        ys='y',
        source=water_src,
        fill_color='#59d0ff',
        fill_alpha=0.8,
        line_color=None,
        line_width=0,
    )
    fig.patches(
        xs='x',
        ys='y',
        source=islands_src,
        fill_color='white',
        line_color=None,
        line_width=0,
    )
    fig.patches(
        xs='x',
        ys='y',
        source=districts_src,
        fill_color=None,
        line_color='black',
        line_width=0,
    )

    if kind.lower() == 'mosaic':
        for col, loc in locations.items():
            width = width * np.sqrt(totals[col] / totals.max())
            mosaic_data = get_mosaic(
                data_,
                data_col=col,
                x=loc.x,
                y=loc.y,
                height=width * np.cos(loc.y * 0.01745),
                width=width,
            )
            fig.patches(**mosaic_data)

    if kind.lower() == 'stacked bar':
        for col, loc in locations.items():
            loc_height = height * totals[col] / totals.max()
            stack_data = get_stacked_bar(
                data_,
                data_col=col,
                x=loc.x,
                y=loc.y,
                height=loc_height,
                width=width,
            )
            fig.patches(**stack_data)

    if kind.lower() == 'bar':
        for col, loc in locations.items():
            loc_height = height * totals[col] / totals.max()
            source = ColumnDataSource(get_bar(
                data_,
                data_col=col,
                x=loc.x,
                y=loc.y,
                height=loc_height,
                width=width,
            ))
            glyph = VBar(
                x='x',
                width=width,
                top='top',
                bottom='bottom',
                fill_color='color',
            )
            fig.add_glyph(source, glyph)
            labels = LabelSet(
                x='x',
                y='top',
                text='values',
                text_align='center',
                text_font_size=label_font_size,
                source=source,
            )
            fig.add_layout(labels)

    if add_legend:
        for group, color in zip(groups, palette):
            fig.circle(x=[], y=[], size=12, fill_color=color, legend=group)

        fig.legend.location = 'bottom_left'
        fig.legend.background_fill_alpha = 1
        fig.legend.border_line_color = 'black'
        fig.legend.label_text_font_size = legend_font_size
        fig.legend.spacing = legend_spacing
        fig.legend.padding = legend_padding

        fig.title.text_font_size = '30px'

    return fig


def main():
    os.chdir(r'../data')
    width = 0.00025
    height = 0.0025
    label_font_size = "11pt"
    add_legend = False
    legend_font_size = "24pt"
    legend_spacing = 20
    legend_padding = 20
    kwargs = dict(
        water_file='water_1698.shp',
        islands_file='islands_1698.shp',
        plot_height=2400,
        plot_width=2400,
        x_axis_location=None,
        y_axis_location=None,
        # output_backend='svg',
    )

    fig1 = draw_population_map(
        population_file='population_1570.csv',
        districts_file='districts_1637.shp',
        y_range=(60.705, 60.717),
        x_range=(28.722, 28.743),
        title='1570',
        width=width,
        height=height,
        kind='bar',
        label_font_size=label_font_size,
        add_legend=add_legend,
        legend_font_size=legend_font_size,
        legend_padding=legend_padding,
        legend_spacing=legend_spacing,
        locations={
            'i': Coordinates(28.73, 60.7125),
            'ii': Coordinates(28.732, 60.7105),
            'iii': Coordinates(28.7315, 60.7137),
            'iv': Coordinates(28.734, 60.713),
            'Valli': Coordinates(28.737, 60.7105),
        },
        **kwargs
    )
    fig2 = draw_population_map(
        population_file='population_1630.csv',
        districts_file='districts_1703.shp',
        y_range=(60.705, 60.718),
        x_range=(28.72, 28.743),
        title='1630',
        width=width,
        height=height,
        label_font_size=label_font_size,
        add_legend=add_legend,
        legend_font_size=legend_font_size,
        legend_padding=legend_padding,
        legend_spacing=legend_spacing,
        kind='bar',
        locations={
            'Linnoitus': Coordinates(28.732, 60.712),
            'Siikaniemi': Coordinates(28.724, 60.712),
            'Valli': Coordinates(28.737, 60.710),
            'Pantsarlahti': Coordinates(28.738, 60.7057),
        },
        **kwargs
    )
    fig3 = draw_population_map(
        population_file='population_1700.csv',
        districts_file='districts_1703.shp',
        y_range=(60.705, 60.718),
        x_range=(28.72, 28.743),
        title='1700',
        width=width,
        height=height,
        label_font_size=label_font_size,
        add_legend=add_legend,
        legend_font_size=legend_font_size,
        legend_padding=legend_padding,
        legend_spacing=legend_spacing,
        kind='bar',
        locations={
            'Linnoitus': Coordinates(28.732, 60.712),
            'Siikaniemi': Coordinates(28.724, 60.712),
            'Valli': Coordinates(28.737, 60.710),
            'Pantsarlahti': Coordinates(28.738, 60.7059),
        },
        **kwargs
    )

    os.chdir(r'../figures')
    # export_svgs(fig1, filename="1570.svg")
    # export_svgs(fig2, filename="1630.svg")
    # export_svgs(fig3, filename="1700.svg")
    export_png(fig1, filename="1570.png")
    export_png(fig2, filename="1630.png")
    export_png(fig3, filename="1700.png")
    output_file(r'karonen.html')
    show(gridplot([fig1, fig2, fig3], ncols=1))


if __name__ == '__main__':
    main()
