import geopandas as gpd
import pandas as pd
import numpy as np
from bokeh.plotting import figure, show, output_file
from bokeh.layouts import gridplot
from bokeh.palettes import magma
from bokeh.models import (
    HoverTool,
    GeoJSONDataSource,
    LinearColorMapper,
    Title,
    ColorBar,
    BasicTicker,
)

from src.util import *


def plot_population_by_district(
        year,
        low: float=0,
        high: float=10000,
        step: float=500,
        copyright_=False,
        title=None,
) -> figure:
    palette = magma(np.ceil((high - low) / step))
    palette = list(reversed(palette))
    year = str(year)

    water = gpd.read_file('water_clip.shp')
    water = get_xy(multipolygons_to_polygons(water))
    water_src = GeoJSONDataSource(geojson=water.to_json())

    islands = gpd.read_file('islands.shp')
    islands = get_xy(multipolygons_to_polygons(islands))
    islands_src = GeoJSONDataSource(geojson=islands.to_json())

    districts = combine_data(
        'districts_1929.shp',
        'population_1900s.csv',
        how='left',
    )
    districts = get_xy(districts)
    districts = districts.fillna(0)
    districts_src = GeoJSONDataSource(geojson=districts.to_json())
    color_mapper = LinearColorMapper(
        palette=palette,
        low=low,
        high=high,
    )

    fig = figure(
        title=title,
        x_axis_location=None,
        y_axis_location=None,
        y_range=(60.69, 60.738),
        x_range=(28.688, 28.78),
    )
    fig.grid.grid_line_color = None
    pvm = datetime.date(datetime.now())
    if copyright_:
        fig.add_layout(Title(text=f"© Antti Härkönen {pvm}", align="left"), "below")

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
    district_patch = fig.patches(
        xs='x',
        ys='y',
        source=districts_src,
        fill_color={
            'field': year,
            'transform': color_mapper,
        },
        fill_alpha=0.8,
        line_color='black',
        line_width=0.8,
    )

    color_bar = ColorBar(
        color_mapper=color_mapper,
        ticker=BasicTicker(),
        label_standoff=12,
        border_line_color=None,
        location=(0, 0)
    )
    fig.add_layout(
        color_bar,
        'right'
    )

    hover = HoverTool(renderers=[district_patch])
    hover.tooltips = [
        ('Kaupunginosa', '@name'),
        ('Väkiluku', '@yhteensa'),
        ('koordinaatit', '($y, $x)'),
    ]
    fig.add_tools(hover)
    return fig


if __name__ == '__main__':
    os.chdir('..\data')
    logging.basicConfig(level=logging.INFO)
    fig1 = plot_population_by_district(1910)
    fig2 = plot_population_by_district(1920)
    fig3 = plot_population_by_district(1930)
    output_file(r'../figures/population_by_district.html')
    show(gridplot([fig1, fig2, fig3], ncols=1))
