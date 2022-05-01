import sqlalchemy as sq
from sqlalchemy import MetaData, Table, Column, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import vkinder_vkapi
import vkinder_vkbot

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


def save_users_in_database():
    for user in vkinder_vkapi.users_url:
        connection.execute(users_table.insert(), {'user_url': user[0], 'photo_1': user[1]})

    return users_table


save_users_in_database()
vkinder_vkbot.send_users()