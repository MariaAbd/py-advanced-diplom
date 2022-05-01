from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

import vkinder_db
import vkinder_vkapi

token_bot = ''
vk = vk_api.VkApi(token=token_bot)
vk_long = VkLongPoll(vk)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)})


def say_hi():
    for event in vk_long.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower()
                if request == 'привет':
                    write_msg(event.user_id,
                              f'Привет, {event.user_id}. '
                              f'Укажите минимальный и максимальный возраст Вашей второй половинки. Например: 20-25')
                    return request


def send_users():
    for event in vk_long.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower()
                if request == 'да':
                    for user in vkinder_vkapi.users_url:
                        shown_user = vkinder_db.session.query(
                            vkinder_db.shown_users_table).filter(
                            vkinder_db.shown_users_table.c.user_url == user[0]).first()
                        if shown_user:
                            continue
                        else:
                            write_msg(event.user_id, user[0])
                            vk.method('messages.send', {
                                'user_id': event.user_id,
                                'attachment': user[1],
                                'random_id': randrange(10 ** 7)})
                            vk.method('messages.send', {
                                'user_id': event.user_id,
                                'attachment': user[2],
                                'random_id': randrange(10 ** 7)})
                            vk.method('messages.send', {
                                'user_id': event.user_id,
                                'attachment': user[3],
                                'random_id': randrange(10 ** 7)})
                            write_msg(event.user_id, 'Отправить ещё?')

                            vkinder_db.connection.execute(vkinder_db.shown_users_table.insert(), {'user_url': user[0]})
                            break
                else:
                    write_msg(event.user_id, 'пока :)')


