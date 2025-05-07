'''fad'''

import folium
import pandas as pd

from folium.plugins import MarkerCluster, Search


def add_markers_to_map(map_obj, data_path):
    '''Добавление маркеров на карту из файла'''
    
    df = pd.read_json(data_path)
      
    markers_cluster = MarkerCluster(name='Метки').add_to(map_obj)

    for _, row in df.iterrows():
        point = row['point']  # Это список вида [широта, долгота]
        rating = row['star']
        name = row['name']
        photos = create_url_for_photo(row['id'], row['photo'])
        stars = '★' * rating + '☆' * (10 - rating)

        html_content = create_html(
            photos,
            name,
            row['addres'],
            row['describe'],
            rating,
            stars
        )

        popup = folium.Popup(folium.Html(html_content, script=True), max_width=300)

        folium.Marker(
            name=name,
            location=point,
            popup=popup,
            tooltip=name
        ).add_to(markers_cluster)
        
    Search(
        layer=markers_cluster,
        search_label='name',
        placeholder='Поиск объектов',
        collapsed=False,
        geom_type="Point",
        position='topright',
        search_zoom=17,
        search_kwargs={'animateZoom': True, 'autoCollapse': True, 'highlight': False}
    ).add_to(map_obj)
        

def create_url_for_photo(id: str, num: int):
    '''create url'''
    photos = []
    
    for i in range(1, num + 1):
        photos.append(f'https://raw.githubusercontent.com/KopatychDisko/for_image/main/image/{id}/{i}.jpg')
        
    return photos


def create_html(photos, name, address, description, rating, stars):
    '''fad'''
    photo_html = ''
    
    for photo in photos:
        photo_html += f'''
            <a href="{photo}" data-lightbox="gallery" data-title="{name}">
                <img src="{photo}" width="60" height="60" style="object-fit:cover; margin:2px; border-radius:5px;" />
            </a>
        '''

    # Основной HTML контент
    html_content = f"""
        <div>
            <h4>{name}</h4>
            <p><b>📍 Адрес:</b> {address}</p>
            <p>{description}</p>
            <p><b>Оценка:</b> {rating}/10 <span style="color:gold; font-size:1.2em;">{stars}</span></p>
            <div style="display:flex; flex-wrap:wrap;">{photo_html}</div>
        </div>
    """
        
    return html_content