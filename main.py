import vkinder_db
import vkinder_vkapi
import vkinder_vkbot


def main():
    vkinder_vkbot.say_hi()
    vkinder_vkapi.search_users()
    vkinder_db.save_users_in_database()
    vkinder_vkbot.send_users()


if __name__ == '__main__':
    main()
