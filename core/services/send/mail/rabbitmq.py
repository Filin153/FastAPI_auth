import json

import pika

from core.config import settings
from .mail import Mail
from .schemas import CreateMessage


class RabbitMqMail:
    _instance = None
    _initialized = False
    __queue = "email_msg"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RabbitMqMail, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if self.__class__._initialized:
            return  # Уже инициализирован, повторная инициализация не требуется
        self.__class__._initialized = True

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=settings.RABITMQ_HOST, port=settings.RABITMQ_PORT)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.__queue, arguments={'x-max-priority': 2})

        self.email = Mail(
            settings.smtp_server, settings.smtp_port, settings.smtp_username,
            settings.smtp_password, True
        )

    async def _worker(self):
        def callback(ch, method, properties, body):
            body = json.loads(body)
            self.email.send_sync(body['send_to'], body['title'], body['message'])

        while True:
            self.channel.basic_consume(queue=self.__queue, on_message_callback=callback, auto_ack=True)
            self.channel.start_consuming()

    async def send_msg(self, create_message: CreateMessage):
        if create_message.type == 'admin':
            self.channel.basic_publish(exchange='', routing_key=self.__queue, body=create_message.json(),
                                       properties=pika.BasicProperties(priority=2))
        elif create_message.type == 'info':
            self.channel.basic_publish(exchange='', routing_key=self.__queue, body=create_message.json(),
                                       properties=pika.BasicProperties(priority=1))
        else:
            self.channel.basic_publish(exchange='', routing_key=self.__queue, body=create_message.json(),
                                       properties=pika.BasicProperties(priority=0))

    async def close_rabbitmq(self):
        self.connection.close()
