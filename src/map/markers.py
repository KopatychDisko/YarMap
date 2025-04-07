'''fad'''

import folium
import pandas as pd
import requests
import base64


    
def add_markers_to_map(map_obj, data_path):
    '''da'''
    
    df = pd.read_json(data_path)
    