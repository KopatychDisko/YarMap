'''Lib for map'''

import folium
import pandas as pd

from folium.plugins import MiniMap, LocateControl, Fullscreen


def create_map():
    '''Create map with some function'''

    center = [57.6261, 39.8845]
    map_obj = folium.Map(location=center, zoom_start=12, attributionControl=0)

    Fullscreen(
        position="topright",
        title="Expand me",
        title_cancel="Exit me",
        force_separate_button=True,
    ).add_to(map_obj)

    MiniMap().add_to(map_obj)
    LocateControl(auto_start=True).add_to(map_obj)
    folium.FitOverlays().add_to(map_obj)
    folium.LayerControl().add_to(map_obj)
     
    # Подключаем Lightbox2
    lightbox_css = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/lightbox2@2.11.3/dist/css/lightbox.min.css">'
    lightbox_js = '<script src="https://cdn.jsdelivr.net/npm/lightbox2@2.11.3/dist/js/lightbox.min.js"></script>'

    map_obj.get_root().header.add_child(folium.Element(lightbox_css))
    map_obj.get_root().html.add_child(folium.Element(lightbox_js))

    return map_obj


def add_districts(json_path, map_obj):
    '''Add bound of district Yaroslavl'''
    
    df = pd.read_json(json_path)
    for name in df.index:
        folium.Polygon(
            locations=df.loc[name, 'geometry'],
            color="blue",
            weight=6,
            fill_color="red",
            fill_opacity=0.5,
            fill=True,
            popup=name,
            tooltip=name,
        ).add_to(map_obj)
        

def map_to_html(json_path, file_to_save):
    '''Do all'''
    yar_map = create_map()
    add_districts(json_path, yar_map)

    yar_map.save(file_to_save)


if __name__ == '__main__':
    map_to_html('../../data/yar_districts.json', '../../data/map.html')
