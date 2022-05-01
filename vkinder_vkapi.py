from vk_api import vk_api
from vk_api.longpoll import VkEventType

import vkinder_vkbot

token_vk = ''
users = vk_api.VkApi(token=token_vk)


def get_age():
    for event in vkinder_vkbot.vk_long.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                age = event.text.lower().split('-')
                age_from = age[0]
                age_to = age[1]
                vkinder_vkbot.write_msg(event.user_id, 'В каком городе ищем Вашу вторую половинку?')
                return age_from, age_to


def get_city():
    for event in vkinder_vkbot.vk_long.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                city = event.text.lower()
                try:
                    city_ids = users.method('database.getCities', {
                        'country_id': 1,
                        'q': city,
                        'need_all': 0,
                        'count': 1
                    })

                    vkinder_vkbot.write_msg(event.user_id, 'Ваш избранник мужчина или женщина?')
                    return city_ids['items'][0]['id']

                except (LookupError, TypeError):
                    vkinder_vkbot.write_msg(event.user_id, 'Такого города не существует, попробуйте ещё раз.')
                    get_city()


def get_sex():
    for event in vkinder_vkbot.vk_long.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                sex = event.text.lower()
                if sex == 'мужчина':
                    sex = 2
                elif sex == 'женщина':
                    sex = 1
                else:
                    vkinder_vkbot.write_msg(event.user_id, 'Необходимо написать "мужчина" или "женщина" ')
                    print()
                    get_sex()

                vkinder_vkbot.write_msg(event.user_id, 'Есть несколько подходящих людей. Отправить фотографии и ссылку?')
                return sex


def search_users():
    vkinder_vkbot.say_hi()
    age = get_age()
    url = 'https://vk.com/id'
    users_list = []
    photos_list = []
    params = {
        'is_closed': 'False',
        'count': 100,
        'fields': 'city, country, relation, photo_max, bdate',
        'age_from': int(age[0]),
        'age_to': int(age[1]),
        'city': get_city(),
        'sex': get_sex(),
        'status': 1 or 6,
        'has_photo': 1
    }

    responce = users.method('users.search', params)
    users_list.append(responce)
    for ids in users_list[0]['items']:
        # print(ids)
        if not ids['is_closed']:
            user_info = users.method('photos.getProfile', {
                'owner_id': ids['id'],
                'album_id': 'profile',
                'extended': 1,
                'fields': 'photo'})

            user_photo = []
            if user_info['count'] >= 3:
                for photo in user_info['items']:
                    likes_coms = int(photo['comments']['count'] + photo['likes']['count'])
                    user_photo.append({'id': photo['id'],
                                       'likes': likes_coms,
                                       'url': photo['sizes'][-1]['url']})
                best_photos = sorted(user_photo, key=lambda k: k['likes'])
                photos_list.append([url + str(photo['owner_id']),
                                    'photo{}_{}'.format(photo['owner_id'], best_photos[-1]['id']),
                                    'photo{}_{}'.format(photo['owner_id'], best_photos[-2]['id']),
                                    'photo{}_{}'.format(photo['owner_id'], best_photos[-3]['id'])
                                    ])

    return photos_list


users_url = search_users()
