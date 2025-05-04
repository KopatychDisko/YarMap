'''Lib for map'''

from os import name
import folium
import pandas as pd

from folium.plugins import MiniMap, LocateControl
from folium import FeatureGroup, LayerControl

from map.markers import add_markers_to_map
from map.colors_districts import give_colors_districts


def create_map():
    '''Create map with some function'''

    center = [57.6261, 39.8845]
    map_obj = folium.Map(location=center, zoom_start=11, attributionControl=0, tiles=None)
    
    folium.TileLayer(
    'Esri.WorldImagery',  # Это слой спутниковых изображений от ESRI
    name='Спутник',
    attr='&copy; <a href="https://www.esri.com">Esri</a>'
    ).add_to(map_obj)
    
    folium.TileLayer(
    'OpenStreetMap',
    name='Схема',
    ).add_to(map_obj)

    MiniMap().add_to(map_obj)
    LocateControl().add_to(map_obj)
    folium.FitOverlays().add_to(map_obj)
     
    # Подключаем Lightbox2
    lightbox_css = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/lightbox2@2.11.3/dist/css/lightbox.min.css">'
    lightbox_js = '<script src="https://cdn.jsdelivr.net/npm/lightbox2@2.11.3/dist/js/lightbox.min.js"></script>'

    map_obj.get_root().header.add_child(folium.Element(lightbox_css))
    map_obj.get_root().html.add_child(folium.Element(lightbox_js))

    return map_obj


def add_districts(json_path, map_obj):
    '''Add bound of district Yaroslavl'''
    
    df = pd.read_json(json_path)
    district_group = FeatureGroup(name='Районы')
    
    for i, row in df.iterrows():
        folium.Polygon(
            locations=row['geometry'],
            color=row['color'],
            weight=6,
            fill_color=row['color'],
            fill_opacity=0.4,
            fill=True,
            popup=row['name']
        ).add_to(district_group)
        
    district_group.add_to(map_obj)

def map_to_html(path_district, path_markers, file_to_save):
    '''Do all'''
    yar_map = create_map()
    give_colors_districts(path_district, path_markers)
    add_districts(path_district, yar_map)
    add_markers_to_map(yar_map, path_markers)
    
    LayerControl().add_to(yar_map)

    yar_map.save(file_to_save)
    
    with open(file_to_save, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # HTML-теги, которые добавим в <head>
    meta_tags = """
    <title>Карта доступной среды в Ярославле</title>
    <link rel="icon" href="favicon.ico">
    <meta name="description" content="Интерактивная карта доступности городской среды для людей с ограниченными возможностями в Ярославле.">
    <meta name="keywords" content="Ярославль, доступная среда, карта, инвалидность, ОВЗ, урбанистика, доступность, инфраструктура">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    """

    html_content = html_content.replace('<head>', f'<head>\n{meta_tags}').replace('</head>', """
<style>
    .leaflet-interactive:focus {
        outline: none !important;
    }
</style>
</head>
""")   
    
    # Перезаписываем файл с обновлённым содержанием
    with open(file_to_save, 'w', encoding='utf-8') as file:
        file.write(html_content)


if __name__ == '__main__':
    map_to_html('../../data/yar_districts.json', '../../data/markers.json', '../../data/map.html')
