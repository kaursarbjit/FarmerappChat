import re
import traceback

import psycopg2
import pytz
from flask import request
from flask_socketio import SocketIO, join_room, leave_room
from datetime import datetime, timezone

from dbwrapper import connect_database
from dbwrapper.db_utils import fetch_room_members
from exceptions import CustomErrors

socketio = SocketIO(engineio_logger=True)

connected_users = {}
logged_in_users = {}
logged_in_users_on_mobile = {}


@socketio.on('connection')
def handle_connection(data):
    '''

    Parameters
    ----------
    data: int
          include user_id which associate with user
    -------

    '''
    try:
        global logged_in_users
        logged_in_users[data['user_id']] = request.sid
        join_room(data['user_id'])
        socketio.emit('connection_done', data, room=data['user_id'])

    except Exception as e:
        traceback.print_exc()
        error = {"detail": e.__str__(),
                 "message": "Could not retrieve results"}
        socketio.emit('connection_done', error, room=data['user_id'])


@socketio.on('send_message')
def handle_send_message_event(data):
    """
    web sockets associate to send message to user's room_id

    param data: information about the user that joined the room
        sender_id: id associate with user
        message: message send
        room_id: id associate with chat room
    """
    try:
        global connected_users
        room_id = data['room_id']
        date = datetime.utcnow()
        created_at = date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata'))
        # fetch data receiver data with the help of sender_id and room_id
        data = fetch_room_members(data)

        # insert data in message table
        try:
            db_connection = connect_database.ConnectDatabase()
            query = "INSERT INTO messages(chat_room_id, sender_id, receiver_id, message, created_at)\
                    VALUES({},{},{},'{}','{}') RETURNING id;".format(data['room_id'], data['sender_id'],
                                                                     data['receiver_id'], data['message'],
                                                                     created_at)
            db_connection.cursor.execute(query)
            message_id = db_connection.cursor.fetchone()[0]
            db_connection.connection.commit()
            data['message_id'] = message_id

        except (psycopg2.ProgrammingError, psycopg2.DatabaseError):
            db_connection.connection.rollback()
            traceback.print_exc()
            raise CustomErrors("Unknown Error occurred.", 500)
        finally:
            db_connection.cursor.close()
            db_connection.connection.close()
        data['created_at'] = str(created_at)

        socketio.emit('receive_message', data, room=data['room_id'])

    # except InvalidUsage as e:
    #     traceback.print_exc()
    #     error = {"message": e.message, "status": e.status_code}
    #     socketio.emit('receive_message', error, room=data['room'])
    except Exception as e:
        traceback.print_exc()
        error = {"detail": e.__str__(),
                 "message": "Could not retrieve results"}
        socketio.emit('receive_message', error, room=data['room_id'])


@socketio.on('join_room')
def handle_join_room_event(data):
    """
    This api is activated when the user joins the room. The server stores the information
    that user has joint the room and in response sends the join room annoucements that lets
    the other user know that the client has joined the room
    :param data: information about the user that joined the room
    :return: sends notification to the room that user has joined the room
    """
    try:
        global connected_users
        if data['room_id'] in connected_users:
            connected_users[data['room_id']].add(data['user_id'])
        else:
            connected_users[data['room_id']] = {data['user_id']}

        # update the user's unread message status of joined room chat
        try:
            db_connection = connect_database.ConnectDatabase()
            query = "UPDATE messages SET status = true WHERE receiver_id = {} and chat_room_id ={} and status = false;" \
                .format(data['user_id'], data['room_id'])
            db_connection.cursor.execute(query)
            db_connection.connection.commit()
        except (psycopg2.ProgrammingError, psycopg2.DatabaseError):
            db_connection.connection.rollback()
            traceback.print_exc()
            raise CustomErrors("Unknown Error occurred.", 500)

        finally:
            db_connection.cursor.close()
            db_connection.connection.close()

        sid = request.sid
        if logged_in_users.get(data['user_id']):
            logged_in_users[data['user_id']] = sid
        else:
            logged_in_users[data['user_id']] = sid
        join_room(data['room_id'])
        socketio.emit('join_room_announcement', data, room=data['room_id'])
    except Exception as e:
        traceback.print_exc()
        error = {"detail": e.__str__(),
                 "message": "Could not retrieve results"}
        data['error'] = error
        socketio.emit('join_room_announcement', data, room=data['room_id'])


@socketio.on('send_permission', namespace='/notifs')
def handle_chat_request_event(data):
    """
    sends chat request to user and save data in db
    data: includes sender_id and receiver_id

    """
    try:
        created_at = datetime.utcnow()
        data['button_key'] = 'pending'
        try:
            db_connection = connect_database.ConnectDatabase()
            query = "INSERT INTO chat_requests(sender_id, receiver_id, created_at, button_key) VALUES({},{},'{}','{}');" \
                .format(data['sender_id'], data['receiver_id'], created_at, data['button_key'])
            db_connection.cursor.execute(query)
            db_connection.connection.commit()
        except (psycopg2.ProgrammingError, psycopg2.DatabaseError):
            db_connection.connection.rollback()
            traceback.print_exc()
            raise CustomErrors("Unknown Error occurred.", 500)
        finally:
            db_connection.cursor.close()
            db_connection.connection.close()
        data['created_at'] = str(created_at)
        socketio.emit('receive_permission', data, namespace='/notifs')

    # except InvalidUsage as e:
    #     traceback.print_exc()
    #     error = {"message": e.message, "status": e.status_code}
    #     socketio.emit('receive_permission', error, namespace='/notifs')

    except Exception as e:
        traceback.print_exc()
        error = {"detail": e.__str__(),
                 "message": "Could not retrieve results"}
        socketio.emit('receive_permission', error, namespace='/notifs')


@socketio.on('leave_room')
def handle_leave_room_event(data):
    """
    refers to user's leave the room
    data: includes user_id and room_id
    """
    global connected_users

    try:
        if data['room_id'] in connected_users:
            connected_users[data['room_id']].remove(data['user_id'])
        leave_room(data['room_id'])

    except Exception as e:
        traceback.print_exc()
        error = {"detail": e.__str__(),
                 "message": "Could not retrieve results"}
        socketio.emit('leave_room_announcement', error, room=data['room_id'])


@socketio.on('message_acknowledgement')
def handle_message_acknowledgements(data):
    """
    refers to message acknowledgements which update the is_read status in db
    data: includes message_id and room_id
    """
    # update is_read status across that receiver_id and message_id
    try:
        db_connection = connect_database.ConnectDatabase()
        query = "UPDATE messages SET status = true WHERE id = {};".format(data['message_id'])
        db_connection.cursor.execute(query)
        db_connection.connection.commit()
    except (psycopg2.ProgrammingError, psycopg2.DatabaseError):
        db_connection.connection.rollback()
        traceback.print_exc()
        raise CustomErrors("Unknown Error occurred.", 500)

    finally:
        db_connection.cursor.close()
        db_connection.connection.close()

    socketio.emit('acknowledgement_announcement', data, room=data['room_id'])
