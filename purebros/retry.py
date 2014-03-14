# encoding: utf-8
import datetime

import redis
from django.utils import simplejson
from rapidsms.router.api import send, lookup_connections
import logging

logger = logging.getLogger("pastoral")

class Retry(object):
    def __init__(self, time=30, host='localhost', port=6379, db=0, password=None):
        self.connection = redis.StrictRedis(host, port, db, password)
        self.retry_queue = "retry_queue"
        self.retry_counter = "retry_counter"
        self.ctime_format = "%a %b %d %H:%M:%S %Y"
        self.retry_time = datetime.timedelta(seconds=int(time))

    def queue(self, message):
        notification = {"message": message, "timer": datetime.datetime.ctime()}
        self.connection.hset(self.retry_queue, message['msg_id'], simplejson.dumps(notification))

    def in_queue(self, message_id):
        return self.connection.hexists(self.retry_queue, message_id)

    def remove_from_queue(self, message_id):
        return self.connection.hdel(self.retry_queue, message_id)

    def get_message(self, message_id):
        return simplejson.loads(self.connection.hget(self.retry_queue, message_id))

    def get_queue(self):
        notifications = simplejson.loads(self.connection.hgetall(self.retry_queue))

        for key in notifications.keys():
            notifications[key]["timer"] = datetime.datetime.strptime(notifications[key]["timer"], self.ctime_format)

        return notifications

    def retry(self):
        messages_to_retry = [(message_id, notification["message"])
                             for message_id, notification in self.get_queue().iteritems()
                             if datetime.datetime.now() - notification["timer"] > self.retry_time]
        for notification in messages_to_retry:
            message_id, message = notification
            if message_id and message:
                logger.debug("Retrying message %s" % message_id)
                send(message.text, message.connection)

    def handle_response(self, response, text, identity, context):
        if response.isdigit():
            response = int(response)
        else:
            return

        responses_to_retry = (32, 35, 45, 51, 48, 93, 95, 96, 97, 99, 302)

        if response != 0:
            if response in responses_to_retry:
                if not self.in_queue(context['pb_id']):

                    submission = {'text': text,
                                  'connection': lookup_connections('purebros', identity),
                                  'msg_id': context['pb_id']}

                    self.queue(submission)
            else:
                if self.in_queue(context['pb_id']):
                    self.remove_from_queue(context['pb_id'])

                logger.error("Cannot send message due to error returned by provider Purebros: %d" % response)

