#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.basic_publish(exchange='', routing_key='conversion_process', body='Hello World!')
print(" [x] Sent 'Hello World!'")
connection.close()