import pika, sys, os, json
import requests

def main():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS']= '../../audioconverter-service-key.json'
    """Receives messages from a pull subscription."""
    from concurrent.futures import TimeoutError
    from google.cloud import pubsub_v1

    project_id = "audioconverter-366014"
    subscription_id = "SuscriptorWorker"

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    def callback(message: pubsub_v1.subscriber.message.Message) -> None:
        print(f"Received {message}.")
        print(message.data.decode("utf-8").replace("'","\""))
        bodyAsJson = json.loads(message.data.decode("utf-8").replace("'","\""))
        x = requests.post (url = "http://127.0.0.1:4000/api/convert",json = bodyAsJson)
        message.ack()
        print("Done")

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}..\n")

    with subscriber:
        try:
            streaming_pull_future.result()
        except TimeoutError:
            streaming_pull_future.cancel()  # Trigger the shutdown.
            streaming_pull_future.result()  # Block until the shutdown is complete.

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)