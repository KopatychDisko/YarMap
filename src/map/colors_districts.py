from math import dist
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from shapely import Point, Polygon


def set_point_to_district(path_districts, path_markers):
    '''fda'''
    markers = pd.read_json(path_markers)
    districts = pd.read_json(path_districts)
    
    polygons = []
    for i, row in districts.iterrows():
        coords = row['geometry'][0]
        polygons.append((row['name'], Polygon(coords)))
    
    distrcts_name_markers = []
    
    for index, row in markers.iterrows():
        point = Point(row['point'])
        for name, location in polygons:
            if location.contains(point):
                distrcts_name_markers.append(name)
                break
        if len(distrcts_name_markers) != index + 1:
            distrcts_name_markers.append('Unknown')
            
    markers['district'] = distrcts_name_markers
    
    markers.to_json(path_markers, orient='records', indent=4, force_ascii=False)

    
def give_stars_districts(path_districts, path_markers):
    markers = pd.read_json(path_markers)
    districts = pd.read_json(path_districts)

    for name in districts['name']:
        stars = markers[markers['district'] == name]['star']
        avg_star = stars.mean() if len(stars) > 0 else 0
        districts.loc[districts['name'] == name, 'star'] = avg_star

    districts.to_json(path_districts, orient='records', force_ascii=False, indent=4)

   
def give_colors_districts(path_districts, path_markers):
    '''fad'''
    set_point_to_district(path_districts, path_markers)
    give_stars_districts(path_districts, path_markers)
    
    districts = pd.read_json(path_districts)
    cmap = plt.get_cmap('RdYlGn')
    
    colors = []
    for rating in districts['star']:
        rgb = cmap(rating / 10)[:3] 
        hex_color = '#{:02x}{:02x}{:02x}'.format(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
        colors.append(hex_color)
    
    districts['color'] = colors
    
    districts.to_json(path_districts, orient='records', force_ascii=False)
    

if __name__ == '__main__':    
    give_colors_districts('../../data/yar_districts.json', '../../data/markers.json')