#!/usr/bin/env python
import pika
import json
"""
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.basic_publish(exchange='', routing_key='conversion_process', body='Hello World!')
print(" [x] Sent 'Hello World!'")
connection.close()
"""

def publish_task_queue(mensaje):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost',heartbeat=0))
    except pika.exceptions.AMQPConnectionError:
        print("Failed to connect to RabbitMQ service. Message wont be sent.")
        return
    
    channel = connection.channel()
    channel.queue_declare(queue='conversion_process', durable=True)
    channel.basic_publish(
            exchange='',
            routing_key='conversion_process',
            body=json.dumps(mensaje),
            properties=pika.BasicProperties(delivery_mode=2)  # make message persistent
            )

    connection.close()



