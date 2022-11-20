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
            pika.ConnectionParameters(host='10.128.0.5',heartbeat=0))
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

def publish_messages(data_str: str) -> None:
    """Publishes multiple messages to a Pub/Sub topic."""
    # [START pubsub_quickstart_publisher]
    # [START pubsub_publish]
    from google.cloud import pubsub_v1

    # TODO(developer)
    project_id = "audioconverter-366014"
    topic_id = "ColaConverter"

    publisher = pubsub_v1.PublisherClient()
    # The `topic_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/topics/{topic_id}`
    topic_path = publisher.topic_path(project_id, topic_id)

    data = str(data_str).encode("utf-8")
    # When you publish a message, the client returns a future.
    future = publisher.publish(topic_path, data)
    print(future.result())

    print(f"Published message to {topic_path}.")
    # [END pubsub_quickstart_publisher]
    # [END pubsub_publish]