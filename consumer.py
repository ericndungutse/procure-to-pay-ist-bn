import json
import pika
import django
import os

from django.conf import settings

# -----------------------------
# Setup Django (so we can use ORM)
# -----------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from purchase_requests.models import PurchaseRequest, PurchaseOrderReceiptMismatch  # import your models here

# -----------------------------
# RabbitMQ URL from environment
# -----------------------------
RABBITMQ_URL = settings.RABBITMQ_URL
if not RABBITMQ_URL:
    raise RuntimeError("RABBITMQ_URL environment variable is not set")

# -----------------------------
# Message handler
# -----------------------------
def handle_message(body):
    print("Received:", body)
    try:
        data = json.loads(body)

        # If message updates a PurchaseRequest purchase_order (existing behavior)
        if data.get("pdf_url") and (data.get("purchase_order_id") or data.get("purchase_request_id")):
            pr_id = data.get("purchase_order_id") or data.get("purchase_request_id")
            try:
                obj = PurchaseRequest.objects.get(id=pr_id)
                obj.purchase_order = data["pdf_url"]
                obj.save()
                print("PurchaseRequest updated with purchase_order pdf_url")
            except PurchaseRequest.DoesNotExist:
                print(f"PurchaseRequest {pr_id} not found")
            return

        # If message contains a `result` field (verifier message), record minimal mismatch
        # Expected incoming payload: { "purchaseRequestId": "...", "result": { ... } }
        if "result" in data:
            pr_id = (
                data.get("purchaseRequestId")
                or data.get("purchase_request_id")
                or data.get("purchaseOrderId")
                or data.get("purchase_order_id")
            )

            if not pr_id:
                print("Mismatch message missing purchaseRequestId; skipping")
                return

            try:
                pr = PurchaseRequest.objects.get(id=pr_id)
            except PurchaseRequest.DoesNotExist:
                print(f"PurchaseRequest {pr_id} not found; cannot record mismatch")
                return

            mismatch = PurchaseOrderReceiptMismatch(
                purchase_request_id=pr.id,
                result=data.get("result"),
            )
            mismatch.save()
            print(f"Saved PurchaseOrderReceiptMismatch for PurchaseRequest {pr_id}")
            return

        print("Unhandled message type or missing fields; nothing to do")
    except Exception as e:
        print("Error processing message:", e)


# -----------------------------
# RabbitMQ Consumer
# -----------------------------
def main():
     # Connect to RabbitMQ using URL (supports CloudIMQ)
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()

    # ensure queues exist
    channel.queue_declare(queue="purchase_orders_queue", durable=True)
    channel.queue_declare(queue="purchase_order_receipt_mismatch", durable=True)

    print(" [*] Waiting for messages. CTRL+C to exit.")

    # callback when message arrives
    def callback(ch, method, properties, body):
        handle_message(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue="purchase_orders_queue",
        on_message_callback=callback
    )
    # also consume verifier/mismatch messages
    channel.basic_consume(
        queue="purchase_order_receipt_mismatch",
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
