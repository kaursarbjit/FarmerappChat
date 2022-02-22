import traceback

import psycopg2

import config
from pyfcm import FCMNotification
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


def push_notification(user_id, sender_id, title, message_template, notification_id, notify_type, room_id=None):
    """
           Parameters
           ----------
           includes user_id,sender_id,title,message_template,notifiction_id,notify_type,room_id

    """

    try:
        db_connection = connect_database.ConnectDatabase()
        query = "Select array_agg(DISTINCT device_token) from user_device_info\
                where  user_id={} and is_active = true and device_token!='';".format(user_id, )
        db_connection.cursor.execute(query)
        token_list = db_connection.cursor.fetchone()[0]
        if token_list:
            push_service = FCMNotification(api_key=config.FIREBASE_API_KEY)
            valid_registration_ids = push_service.clean_registration_ids(token_list)
            extra_ids = [id for id in token_list if id not in valid_registration_ids]
            registration_ids = [id for id in token_list if id not in extra_ids]
            message_title = title
            message_body = message_template
            data_message = {"room_id": room_id,
                            "sender_id": sender_id,
                            "receiver_id": user_id,
                            "notification_id": notification_id,
                            "notification_type": notify_type}

            result = push_service.notify_multiple_devices(registration_ids=registration_ids,
                                                          message_title=message_title,
                                                          message_body=message_body, data_message=data_message)
            return result

    except (psycopg2.ProgrammingError, psycopg2.DatabaseError):
        db_connection.connection.rollback()
        traceback.print_exc()
        raise CustomErrors("Unknown Error occurred.", 500)

    finally:
        db_connection.cursor.close()
        db_connection.connection.close()