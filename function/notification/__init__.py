import azure.functions as func
import logging
import os
from datetime import datetime
import psycopg2
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def main(msg: func.ServiceBusMessage):

    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s', notification_id)

    # Done: Get connection to database
    conn = psycopg2.connect(dbname="techconfdb", user="admin_pg@techconf-sqlserver", password="Password123!", host="techconf-sqlserver.postgres.database.azure.com")
    cursor = conn.cursor()
    try:
        notification_query = cursor.execute("SELECT message, subject FROM notification WHERE id = {};".format(notification_id))

        cursor.execute("SELECT first_name, last_name, email FROM attendee;")
        attendees = cursor.fetchall()

        for attendee in attendees:
            Mail('{}, {}, {}'.format({'admin@techconf.com'}, {attendee[2]}, {notification_query}))

        notification_completed_date = datetime.utcnow()

        notification_status = 'Notified {} attendees'.format(len(attendees))

        update_query = cursor.execute("UPDATE notification SET status = '{}', completed_date = '{}' WHERE id = {};".format(notification_status, notification_completed_date, notification_id))

        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
