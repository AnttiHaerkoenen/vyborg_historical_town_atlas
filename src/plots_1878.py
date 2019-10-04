import os
import logging

import geopandas as gpd
from bokeh.plotting import figure, show, output_file, save
from bokeh.palettes import Category10_9 as palette
from bokeh.transform import factor_cmap
from bokeh.models import HoverTool, GeoJSONDataSource

from src.util import multipolygons_to_polygons, get_xy

district_name_mapper_fi = {
    '1': "Linnoitus",
    '2': "P. Annan kruunu (Siikaniemi)",
    '3': "Salakkalahti",
    '4': "Repola",
    '5': "Pantsarlahti",
    '6': "Kaleva",
    '7': "Papula",
    '8': "Saunalahti",
    '10': "Neitsytniemi",
}

district_name_mapper_en = {
    '1': "Old town",
    '2': "St. Anna's crown",
    '3': "Salakkalahti",
    '4': "Repola",
    '5': "Pantsarlahti",
    '6': "Kaleva",
    '7': "Papula",
    '8': "Saunalahti",
    '10': "Neitsytniemi",
}

district_name_mapper = district_name_mapper_en


def mk_plots_folium(fp_plots, title=None):
    import folium

    plots = gpd.read_file(fp_plots)
    plots = get_xy(plots)
    plots['district_name'] = plots.DISTRICT.map(district_name_mapper)

    map_ = folium.Map(
        location=[60.71, 28.73],
        zoom_start=14,
        tiles='Stamen Terrain',
    )
    folium.GeoJson(
        plots.to_json()
    ).add_to(map_)
    folium.LayerControl().add_to(map_)

    return map_


def plot_plots_bokeh(fp_plots, title=None, **kwargs):
    water = gpd.read_file('water_clip.shp')
    water = get_xy(multipolygons_to_polygons(water))
    water_src = GeoJSONDataSource(geojson=water.to_json())

    islands = gpd.read_file('islands.shp')
    islands = get_xy(multipolygons_to_polygons(islands))
    islands_src = GeoJSONDataSource(geojson=islands.to_json())

    plots = gpd.read_file(fp_plots)
    plots = get_xy(plots)
    plots['district_name'] = plots.DISTRICT.map(district_name_mapper)
    plots_src = GeoJSONDataSource(geojson=plots.to_json())

    factors = list(district_name_mapper.values())
    color_mapper = factor_cmap(
        'district_name',
        palette=palette,
        factors=factors,
    )

    fig = figure(
        title=title,
        x_axis_location=None,
        y_axis_location=None,
        y_range=(60.70, 60.73),
        x_range=(28.70, 28.77),
        **kwargs
    )
    if title:
        fig.title.text_font_size = "20px"
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
        line_width=0
    )
    plots_patch = fig.patches(
        xs='x',
        ys='y',
        source=plots_src,
        fill_color=color_mapper,
        fill_alpha=0.8,
        line_color='black',
        line_width=0.8,
    )
    hover = HoverTool(renderers=[plots_patch])
    hover.tooltips = [
        ('kaupunginosa', '@district_name'),
        ('numero', '@NUMBER'),
        ('koordinaatit', '($y, $x)'),
    ]
    fig.add_tools(hover)

    for factor, color in zip(factors, palette):
        fig.circle(x=[], y=[], fill_color=color, legend=factor)
    fig.legend.location = 'bottom_left'
    fig.legend.background_fill_alpha = 1
    fig.legend.border_line_color = 'black'

    return fig


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    os.chdir(r'../data')
    # fol = mk_plots_folium('plots_1878.shp')
    # os.chdir(r'../figures')
    # fol.save('folium.html')
    fig = plot_plots_bokeh(
        'plots_1878.shp',
        plot_height=400,
        plot_width=500,
    )
    output_file(r'../figures/plots_1878.html')
    save(fig)
    # show(fig)
