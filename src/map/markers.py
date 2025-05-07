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

        popup = folium.Popup(folium.Html(html_content, script=True), max_width=250)

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


def create_html(photos, name, address, description, rating, stars, max_preview=5):
    """Генерация HTML контента для popup с кнопкой-плейсхолдером"""
    # Определяем превью и дополнительные фото
    preview = photos[:max_preview]
    extra_count = len(photos) - len(preview)

    # Собираем HTML для превью первых max_preview фото
    photo_html = ''
    for photo in preview:
        photo_html += f'''
            <a href="{photo}" data-lightbox="gallery" data-title="{name}" class="visible-photo">
                <img src="{photo}" width="60" height="60" 
                     style="object-fit:cover; margin:2px; border-radius:5px;" />
            </a>
        '''
    # Кнопка-плейсхолдер после превью
    if extra_count > 0:
        photo_html += f'''
            <div class="more-photo" onclick="
                // Найти первую скрытую фотографию и открыть галерею
                var hidden = this.parentNode.querySelectorAll('a.hidden-photo');
                if(hidden.length>0) {{ hidden[0].click(); }}
            "
            style="
                width:60px;
                height:60px;
                margin:2px;
                border-radius:5px;
                background: #ddd;
                display:flex;
                align-items:center;
                justify-content:center;
                cursor:pointer;
                font-weight:bold;
                font-size:1em;
            ">
                +{extra_count}
            </div>
        '''
    # Генерируем скрытые фото для lightbox
    hidden_html = ''
    for photo in photos[max_preview:]:
        hidden_html += f'''
            <a href="{photo}" data-lightbox="gallery" data-title="{name}" 
               class="hidden-photo" style="display:none;"></a>
        '''

    # Описание
    p_description = ''.join(
        [f'<p style="margin:2px 0; padding:0;">{line}</p>' for line in description.split('\n')]
    )

    # Итоговый HTML
    html_content = f"""
        <div>
            <h4>{name}</h4>
            <p><b>📍 Адрес:</b> {address}</p>
            <div class="popup-description">{p_description}</div>
            <p><b>Оценка:</b> {rating}/10 <span style="color:gold; font-size:1.2em;">{stars}</span></p>
            <div style="display:flex; flex-wrap:wrap; margin-top:4px;">
                {photo_html}
                {hidden_html}
            </div>
        </div>
    """
    return html_content