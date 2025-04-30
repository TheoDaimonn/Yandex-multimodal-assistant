import requests

def get_vk_posts(group_domain, count=50, access_token='ed3d8b43ed3d8b43ed3d8b435dee0de69beed3ded3d8b43853274dd83d4c20ccf7b5670'):
    # Получаем ID группы
    group_info = requests.get(
        'https://api.vk.com/method/groups.getById',
        params={
            'group_id': group_domain,
            'access_token': access_token,
            'v': '5.131'
        }
    ).json()
    
    if 'error' in group_info:
        print(f"Ошибка: {group_info['error']['error_msg']}")
        return None
    
    group_id = group_info['response'][0]['id']
    
    # Получаем посты
    posts = requests.get(
        'https://api.vk.com/method/wall.get',
        params={
            'owner_id': -group_id,  # Для групп используем отрицательный ID
            'count': count,
            'access_token': access_token,
            'v': '5.131',
            'filter': 'owner'  # Только посты от владельца
        }
    ).json()
    
    if 'error' in posts:
        print(f"Ошибка: {posts['error']['error_msg']}")
        return None
    
    return posts['response']['items']

for group_id, name in [('maiuniversity', 'МАИ | Московский авиационный институт'), ('eights_fac_mai', "8 факультет МАИ"), ('itmai', "IT-Центр МАИ"), ('aviatechmai', "Институт №1 Авиационная Техника МАИ"), ("2inst", "ИНСТИТУТ №2 МАИ"), ("frela_mai", "ФРЭЛА МАИ"), ("5instmai", "Институт № 5 МАИ"), ("mai_institute7", "Поступи в Институт №7 МАИ"), ("prof9fak", "МАИ Институт №9 | Общеинженерной подготовки"), ]:

    posts = get_vk_posts(group_id, 100)
    result = []
    for post in posts:
        result.append( str(post['date']) + '\n' + post['text'] )
    with open('data/vk_parse/' + name , 'w+', encoding='utf-8') as f:
        f.write('\n$$$\n'.join(result))
