import json
import pika
import django
import os

# -----------------------------
# Setup Django (so we can use ORM)
# -----------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from purchase_requests.models import PurchaseRequest  # import your models here

# -----------------------------
# RabbitMQ URL from environment
# -----------------------------
# RABBITMQ_URL = os.environ.get("RABBITMQ_URL")
RABBITMQ_URL = "amqps://twfcsfdi:g8yfowCdbcdLzFGHtDPl3lR2dUKYblB7@seal.lmq.cloudamqp.com/twfcsfdi"
if not RABBITMQ_URL:
    raise RuntimeError("RABBITMQ_URL environment variable is not set")

# -----------------------------
# Message handler
# -----------------------------
def handle_message(body):
    print("Received:", body)
    try:
        data = json.loads(body)
        obj = PurchaseRequest.objects.get(id=data["purchase_order_id"])
        obj.purchase_order = data["pdf_url"]
        obj.save()
        print("Database updated")
    except PurchaseRequest.DoesNotExist:
        print(f"PurchaseRequest {data.get('purchase_order_id')} not found")
    except Exception as e:
        print("Error processing message:", e)


# -----------------------------
# RabbitMQ Consumer
# -----------------------------
def main():
     # Connect to RabbitMQ using URL (supports CloudIMQ)
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()

    # ensure queue exists
    channel.queue_declare(queue="purchase_orders_queue", durable=True)

    print(" [*] Waiting for messages. CTRL+C to exit.")

    # callback when message arrives
    def callback(ch, method, properties, body):
        handle_message(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue="purchase_orders_queue",
        on_message_callback=callback
    )

        # Graceful shutdown
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Consumer interrupted. Closing connection...")
        connection.close()


if __name__ == "__main__":
    main()
