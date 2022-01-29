import traceback

import psycopg2

from dbwrapper import connect_database
from exceptions import CustomErrors
from utilis.media import generate_url


def fetch_room_members(data):
    """
        fetch room's members
        Parameters
        ----------
        data: dict
            includes sender_id, room_id and message

        Returns
            receiver_id and their profile picture
        -------

    """
    try:
        db_connection = connect_database.ConnectDatabase()
        query = "SELECT user_id FROM chat_room_users WHERE chat_room_id = {} and status =true;".format(data['room_id'])
        db_connection.cursor.execute(query)
        users_data = db_connection.cursor.fetchall()
        users_data = list(users_data)
        for user_id in users_data:
            if data['sender_id'] == user_id[0]:
                pass
            else:
                receiver_id = user_id[0]

        query = "SELECT name, profile_picture_key FROM users WHERE id = {} ;".format(receiver_id)
        db_connection.cursor.execute(query)
        user_info = db_connection.cursor.fetchall()
        data['receiver_id'] = receiver_id
        data['receiver_name'] = user_info[0][0]
        data['receiver_profile_key'] = generate_url(user_info[0][1]) if user_info[0][1] else ""
        return data

    except psycopg2.DatabaseError:
        db_connection.connection.rollback()
        traceback.print_exc()
        raise CustomErrors("Unknown Error occurred.", 500)

    finally:
        db_connection.cursor.close()
        db_connection.connection.close()

