from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import sqlalchemy as sq
from sqlalchemy import MetaData, Table, func, Column, String, Integer, ForeignKey, Numeric, select, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

token_bot = ''
token_vk = ''

vk = vk_api.VkApi(token=token_bot)
users = vk_api.VkApi(token=token_vk)

longpoll = VkLongPoll(vk)

Base = declarative_base()

engine = sq.create_engine('postgresql://postgres:Artem_Arya0315SQL@localhost:5432/py_48')
connection = engine.connect()
Session = sessionmaker(bind=engine)
session = Session()
meta = MetaData(bind=engine)

users_table = Table(
    'users_table', meta,
    Column('user_url', String, primary_key=True),
    Column('photo_1', String, nullable=False)
)

shown_users_table = Table(
    'shown_users_table', meta,
    Column('user_url', String, ForeignKey('users_table.user_url'), primary_key=True)
)

meta.create_all(engine)


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
                elif sex == 'женщина':
                    sex = 1
                else:
                    write_msg(event.user_id, 'Необходимо написать "мужчина" или "женщина" ')
                    print()
                    get_sex()

                write_msg(event.user_id, 'Есть несколько подходящих людей. Отправить фотографии и ссылку?')
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
# print(users_url)


def save_users_in_database():
    i = int()
    for user in users_url:
        connection.execute(users_table.insert(), {'user_url': users_url[i][0], 'photo_1': users_url[i][1]})
        i += 1
    return users_table


# save_users_in_database()


def send_users():
    i = int()
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower()
                if request == 'да':
                    for user in users_url:
                        if not users_url[i][0]:
                            write_msg(event.user_id, users_url[i][0])
                            vk.method('messages.send', {
                                'user_id': event.user_id,
                                'attachment': users_url[i][1],
                                'random_id': randrange(10 ** 7)})
                            vk.method('messages.send', {
                                'user_id': event.user_id,
                                'attachment': users_url[i][2],
                                'random_id': randrange(10 ** 7)})
                            vk.method('messages.send', {
                                'user_id': event.user_id,
                                'attachment': users_url[i][3],
                                'random_id': randrange(10 ** 7)})
                            write_msg(event.user_id, 'Отправить ещё?')
                            connection.execute(shown_users_table.insert(), {'user_url': users_url[i][0]})
                            i += 1
                            break
                        else:
                            print(user)
                            i += 1
                else:
                    write_msg(event.user_id, 'пока :)')


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
