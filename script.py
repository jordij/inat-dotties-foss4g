# -*- coding: utf-8 -*-
from folium.plugins import HeatMap
import folium
import pandas
import requests
import yaml

# API docs in https://www.inaturalist.org/pages/api+reference
API_BASEURL = 'https://inaturalist.nz/observations.json'

# Load predefined args: bounding box, taxon ID and other API params
params = yaml.load(open('params.yaml'), yaml.SafeLoader)
map_params = params['map']
api_params = params['api']


def get_data(api_params={}):
    print("⏳ Fetch iNaturalist data from API... page %d" % api_params['page'])
    r = requests.get(API_BASEURL, params=api_params, headers={
        'Content-Type': 'application/json'})
    if r.status_code != 200:
        raise Exception(
            'Yikes - iNaturalist API error: {}'.format(
                r.status_code)
        )

    df = pandas.read_json(r.content)

    if len(df.index) == api_params['per_page']:  # more pages to fetch
        api_params['page'] += 1
        df = df.append(get_data(api_params))
    return df


df = get_data(api_params)
basemap = folium.Map(
        location=[map_params['center_lat'], map_params['center_long']],
        zoom_start=map_params['zoom'],
        control_scale=True,
        zoom_control=True,
        )
tiles = folium.raster_layers.TileLayer(
        tiles=map_params['basemap_url'],
        attr=map_params['basemap_attr'],
        name=map_params['basemap_name'],
        show=True)
tiles.add_to(basemap)

obs_coords = list(zip(df['latitude'], df['longitude']))
heatmap = HeatMap(obs_coords, min_opacity=0.2, radius=25)

fg_hm = folium.FeatureGroup(name='NNZD heatmap', show=False)
basemap.add_child(fg_hm)
heatmap.add_to(fg_hm)

fg = folium.FeatureGroup(name='NNZD single observations', show=True)
basemap.add_child(fg)

for coord in obs_coords:
    folium.Marker(coord).add_to(fg)

folium.LayerControl().add_to(basemap)

basemap.save(params['output_map'])
