from random import randrange
import requests
from pprint import pprint
import vk_api
import pandas as pd
from vk_api.longpoll import VkLongPoll, VkEventType

token_bot = ''
token_vk = ''

vk = vk_api.VkApi(token=token_bot)
users = vk_api.VkApi(token=token_vk)

longpoll = VkLongPoll(vk)


def get_city():
    city = input('В каком городе ищем Вашу вторую половинку? ').lower()
    try:
        city_ids = users.method('database.getCities', {
            'country_id': 1,
            'q': city,
            'need_all': 0,
            'count': 1
            })
        return city_ids['items'][0]['id']
    except (LookupError, TypeError):
        print('Такого города не существует, попробуйте ещё раз.')
        print()
        get_city()


def get_sex():
    sex = input('Ваш избранник мужчина или женщина?').lower()
    if sex == 'мужчина':
        sex = 2
    elif sex == 'женщина':
        sex = 1
    else:
        print('Необходимо написать "мужчина" или "женщина" ')
        print()
        get_sex()
    return sex


def get_age_from():
    age_from = input('Укажите минимальный возраст: ')
    try:
        age_from = int(age_from)
        if 0 < int(age_from) <= 100:
            return age_from

        else:
            print('Необходимо указать число от 0 до 100: ')
            print()
            get_age_from()

    except (TypeError, ValueError):
        print('Необходимо указать число от 0 до 100: ')
        print()
        get_age_from()

get_age_from()

#     age_to = input('Укажите максимальный возраст: ')
#     try:
#         age_to = int(age_to)
#         if age_from < int(age_to) <= 100:
#             return age_to
#         else:
#             print('Необходимо указать число больше минмимального возраста и меньше 100: ')
#             print()
#             get_age_to()
#
#     except (TypeError, ValueError):
#         print('Необходимо указать число больше минмимального возраста и меньше 100: ')
#         print()
#         get_age_to()
#
# get_age_to()


def search_users():
    url = 'https://vk.com/id'
    users_list = []
    photos_list = []
    params = {
        'is_closed': 'False',
        'count': 10,
        'fields': 'city, country, relation, photo_max, bdate',
        'city': get_city(),
        'sex': get_sex(),
        'status': 1 or 6,
        'age_from': get_age_from(),
        'age_to': get_age_to(),
        'has_photo': 1
    }

    responce = users.method('users.search', params)
    users_list.append(responce)

    for ids in users_list[0]['items']:
        if not ids['is_closed']:

            user_info = users.method('photos.getProfile', {
                'owner_id': ids['id'],
                'album_id': 'profile',
                'extended': 1,
                'fileds': 'photo'})
            user_photo = []

            for photo in user_info['items']:
                likes_coms = int(photo['comments']['count'] + photo['likes']['count'])
                user_photo.append({'likes': likes_coms,
                                    'url': photo['sizes'][-1]['url']})
            best_photos = sorted(user_photo, key=lambda k: k['likes'])
            photos_list.append([url + str(photo['owner_id']), best_photos[-3:]])
    pprint(photos_list)
    return photos_list


# search_users()


# def write_msg(user_id, message):
#     vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})
#
#
# for event in longpoll.listen():
#     if event.type == VkEventType.MESSAGE_NEW:
#
#         if event.to_me:
#             request = event.text
#
#             if request == "привет":
#                 write_msg(event.user_id, f"Хай, {event.user_id}")
#             elif request == "пока":
#                 write_msg(event.user_id, "Пока((")
#             else:
#                 write_msg(event.user_id, "Не поняла вашего ответа...")