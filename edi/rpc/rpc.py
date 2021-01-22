
import json
import pika
import threading

from .resolvers import OdooResolver

# RABBIT_MQ = 'localhost'
RABBIT_MQ = '128.199.193.129'


class OdooGetCogsRpc(threading.Thread):

    @staticmethod
    def _get_connection():
        return pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBIT_MQ))

    def on_request(self, ch, method, props, body):

        # print('Someone Request ...')
        try:
            data = json.loads(body)
            odoo_resolver = OdooResolver(data)
            response = odoo_resolver.get_cogs()
        except Exception:
            odoo_resolver = OdooResolver()
            response = odoo_resolver.get_cogs()

        ch.basic_publish(
            exchange='', routing_key=props.reply_to,
            properties=pika.BasicProperties(
                correlation_id=props.correlation_id),
            body=str(response)
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        connection = self._get_connection()
        channel = connection.channel()
        channel.queue_declare(queue='odoo_edi.get_cogs')

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue='odoo_edi.get_cogs',
            on_message_callback=self.on_request
        )

        print(" [x] Awaiting RPC requests (odoo_edi.get_cogs)")
        channel.start_consuming()


class OdooGetStockRpc(threading.Thread):

    @staticmethod
    def _get_connection():
        return pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBIT_MQ))

    def on_request(self, ch, method, props, body):

        # print('Someone Request ...')
        try:
            data = json.loads(body)
            odoo_resolver = OdooResolver(data)
            response = odoo_resolver.get_stock()
        except Exception:
            odoo_resolver = OdooResolver()
            response = odoo_resolver.get_stock()

        ch.basic_publish(
            exchange='', routing_key=props.reply_to,
            properties=pika.BasicProperties(
                correlation_id=props.correlation_id),
            body=str(response)
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        connection = self._get_connection()
        channel = connection.channel()
        channel.queue_declare(queue='odoo_edi.get_stock')

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue='odoo_edi.get_stock',
            on_message_callback=self.on_request
        )

        print(" [x] Awaiting RPC requests (odoo_edi.get_stock)")
        channel.start_consuming()


class OdooListStockRpc(threading.Thread):

    @staticmethod
    def _get_connection():
        return pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBIT_MQ))

    def on_request(self, ch, method, props, body):

        # print('Someone Request ...')
        try:
            data = json.loads(body)
            odoo_resolver = OdooResolver(data)
            response = odoo_resolver.get_stock()
        except Exception:
            odoo_resolver = OdooResolver()
            response = odoo_resolver.get_stock()

        ch.basic_publish(
            exchange='', routing_key=props.reply_to,
            properties=pika.BasicProperties(
                correlation_id=props.correlation_id),
            body=str(response)
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        connection = self._get_connection()
        channel = connection.channel()
        channel.queue_declare(queue='odoo_edi.list_stock')

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue='odoo_edi.list_stock',
            on_message_callback=self.on_request
        )

        print(" [x] Awaiting RPC requests (odoo_edi.list_stock)")
        channel.start_consuming()
