import pika, sys, os, json
import requests

def main():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
    except pika.exceptions.AMQPConnectionError:
        print("Failed to connect to RabbitMQ service. Message wont be sent.")
        return

    channel = connection.channel()
    channel.queue_declare(queue='conversion_process', durable=True)

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body.decode())
        x = requests.post ("http://127.0.0.1:5000/api/convert",json = body)
        print(x)
        print("Done")

channel.basic_consume(queue='conversion_process', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)