from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

token_bot = ''
token_vk = ''

vk = vk_api.VkApi(token=token_bot)
users = vk_api.VkApi(token=token_vk)

longpoll = VkLongPoll(vk)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)})


def say_hi():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower()
                if request == 'привет':
                    write_msg(event.user_id,
                              f'Привет, {event.user_id}. '
                              f'Укажите минимальный и максимальный возраст Вашей второй половинки. Например: 20-25')
                    return request


def get_age():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                age = event.text.lower().split('-')
                age_from = age[0]
                age_to = age[1]
                write_msg(event.user_id, 'В каком городе ищем Вашу вторую половинку?')
                return age_from, age_to


def get_city():
    for event in longpoll.listen():
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

                    write_msg(event.user_id, 'Ваш избранник мужчина или женщина?')
                    return city_ids['items'][0]['id']

                except (LookupError, TypeError):
                    write_msg(event.user_id, 'Такого города не существует, попробуйте ещё раз.')
                    get_city()


def get_sex():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                sex = event.text.lower()
                if sex == 'мужчина':
                    sex = 2
                    # write_msg(event.user_id, sex)
                elif sex == 'женщина':
                    sex = 1
                    # write_msg(event.user_id, sex)
                else:
                    write_msg(event.user_id, 'Необходимо написать "мужчина" или "женщина" ')
                    print()
                    get_sex()

                write_msg(event.user_id, 'Есть несколько подходящих людей. Хотите получить фотографии и ссылки на них?')
                return sex


def search_users():
    say_hi()
    age = get_age()
    url = 'https://vk.com/id'
    users_list = []
    photos_list = []
    params = {
        'is_closed': 'False',
        'count': 100,
        'fields': 'city, country, relation, photo_max, bdate',
        'age_from': age[0],
        'age_to': age[1],
        'city': get_city(),
        'sex': get_sex(),
        'status': 1 or 6,
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
                'fields': 'photo'})
            user_photo = []

            for photo in user_info['items']:
                likes_coms = int(photo['comments']['count'] + photo['likes']['count'])
                user_photo.append({'likes': likes_coms,
                                   'url': photo['sizes'][-1]['url']})
            best_photos = sorted(user_photo, key=lambda k: k['likes'])
            photos_list.append([url + str(photo['owner_id']), best_photos[-3:]])
    return photos_list


users_url = search_users()
print(users_url)


def send_users():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower()
                if request == 'да':
                    write_msg(event.user_id, users_url)


send_users()


# def get_age_from():
#     for event in longpoll.listen():
#         if event.type == VkEventType.MESSAGE_NEW:
#             if event.to_me:
#                 age_from = event.text.lower()
#                 try:
#                     age_from = int(age_from)
#                     if 0 < age_from <= 100:
#                         write_msg(event.user_id, age_from)
#                         write_msg(event.user_id, 'Укажите максимальный возраст Вашей второй половинки')
#                         return age_from
#                     else:
#                         return write_msg(event.user_id, 'Необходимо указать число от 0 до 100')
#                         get_age_from()
#                 except:
#                     write_msg(event.user_id, '!!!Необходимо указать число от 0 до 100')
#                     get_age_from()
#
#
# age_from = get_age_from()
#
#
# def get_age_to():
#
#     for event in longpoll.listen():
#         if event.type == VkEventType.MESSAGE_NEW:
#             if event.to_me:
#                 age_to = event.text.lower()
#                 try:
#                     age_to = int(age_to)
#                     if age_from <= int(age_to) <= 100:
#                         write_msg(event.user_id, 'В каком городе ищем Вашу вторую половинку?')
#                         return age_to
#
#                     else:
#                         write_msg(event.user_id, 'Необходимо указать число больше минимального возраста и меньше 100')
#                         get_age_to()
#
#                 except:
#                     write_msg(event.user_id, '!!!!Необходимо указать число больше минимального возраста и меньше 100')
#                     get_age_to()