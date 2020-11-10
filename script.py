# -*- coding: utf-8 -*-
from folium.plugins import HeatMap
import folium
import pandas
import requests
import yaml

# API docs in https://www.inaturalist.org/pages/api+reference
API_BASEURL = 'https://inaturalist.nz/observations.json'

# Load bounding box, taxon ID and other API params
params = yaml.load(open('params.yaml'), yaml.SafeLoader)
map_params = params['map']
api_params = params['api']

def get_data(api_params={}):
    print("⏳ Fetch iNaturalist data from API... page %d" % api_params['page'] )
    r = requests.get(API_BASEURL, params=api_params, headers={'Content-Type': 'application/json'})
    if r.status_code != 200:
        raise Exception('Something went wrong with the iNaturalist API: {}'.format(r.status_code))
    
    df = pandas.read_json(r.content)
    
    if len(df.index) == api_params['per_page']: # if there are more pages to fetch
        api_params['page'] += 1
        df = df.append(get_data(api_params))
    return df
    
df = get_data(api_params)

basemap = folium.Map(
        location=[map_params['center_lat'], map_params['center_long']],
        zoom_start=map_params['zoom'],
        tiles=map_params['basemap_url'],
        attr=map_params['basemap_attr'])

obs_coords = list(zip(df['latitude'], df['longitude']))
heatmap = HeatMap(obs_coords, min_opacity=0.2)
heatmap.add_to(basemap)

basemap.save('map.html')

