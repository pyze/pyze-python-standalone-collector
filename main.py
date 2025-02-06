import datetime
import json
import logging
import time
import uuid

import uvicorn
from confluent_kafka import Producer
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from config import Config

# ------------------------------------------------------------------------------
# Logging Setup
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
runtime_handler = logging.FileHandler("runtime.log")
runtime_handler.setLevel(logging.DEBUG)
logger.addHandler(runtime_handler)

error_logger = logging.getLogger("error_logger")
error_logger.setLevel(logging.ERROR)
error_handler = logging.FileHandler("error.log")
error_handler.setLevel(logging.ERROR)
error_logger.addHandler(error_handler)

# ------------------------------------------------------------------------------
# Confluent Kafka Producer
# ------------------------------------------------------------------------------
bootstrap_servers = (
    ",".join(Config.KAFKA_BOOTSTRAP_SERVERS)
    if isinstance(Config.KAFKA_BOOTSTRAP_SERVERS, list)
    else Config.KAFKA_BOOTSTRAP_SERVERS
)

producer = Producer({"bootstrap.servers": bootstrap_servers})
KAFKA_TOPIC_INGESTION_RAW = Config.KAFKA_TOPIC_INGESTION_RAW

# ------------------------------------------------------------------------------
# FastAPI App + CORS Middleware
# ------------------------------------------------------------------------------
app = FastAPI()

# Configure the CORS middleware using the same rules from the original custom headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "t", "v", "messageid"],
    allow_credentials=True,
)


# ------------------------------------------------------------------------------
# Kafka Delivery Callback
# ------------------------------------------------------------------------------
def delivery_report(err, msg):
    if err:
        error_logger.error(f"Delivery failed: {err}. Message: {msg.value()}")
    else:
        logger.debug(f"Message delivered to {msg.topic()} [Partition: {msg.partition()}], Offset: {msg.offset()}")


# ------------------------------------------------------------------------------
# GET Endpoint (Health Check)
# ------------------------------------------------------------------------------
@app.get("/", summary="Healthcheck usage")
def healthcheck():
    try:
        producer.list_topics(timeout=5)  # Example Kafka readiness check
        return JSONResponse(content={"status": "ok"}, status_code=200)
    except Exception as exc:
        error_logger.error(f"Healthcheck failure: {exc}")
        return JSONResponse(content={"status": "unhealthy"}, status_code=503)


# ------------------------------------------------------------------------------
# POST Endpoint (Publish to Kafka)
# ------------------------------------------------------------------------------
@app.post("/", summary="Process event and publish to Kafka")
async def process_event(request: Request):
    """
    Parses incoming JSON, enriches the payload, and publishes to Kafka asynchronously.
    Returns HTTP 202 on success, or error codes on failure.
    """
    # Log raw request data
    raw_body = await request.body()
    logger.debug(raw_body)

    # Attempt to parse JSON
    try:
        data = await request.json()
    except Exception as exc:
        error_logger.error(f"No valid JSON received: {exc}")
        return JSONResponse(
            content={"error": "No valid JSON received."},
            status_code=400
        )

    if not data:
        error_logger.error("No data in the request body.")
        return JSONResponse(
            content={"error": "No data received in the request."},
            status_code=400
        )

    logger.debug(json.dumps(data))

    # Build payload
    payload = {"pyzejsonpayload": data, "pyzeContext": {
        # "ip": ip,
        "receivedEpoch": int(time.time_ns() / 1_000_000),
    }}

    # # Extract IP (if x-forwarded-for and comma present)
    # ip = request.headers.get("x-forwarded-for")
    # if ip and "," in ip:
    #     ip = ip.split(",")[-2].strip()

    # Add messageId if missing
    if "messageId" not in payload["pyzejsonpayload"]:
        message_id = str(uuid.uuid4())
        payload["pyzejsonpayload"]["messageId"] = message_id
    else:
        message_id = payload["pyzejsonpayload"]["messageId"]

    # Convert eventTime -> collectedEpoch if present
    if "eventTime" in payload["pyzejsonpayload"]:
        dt = datetime.datetime.fromisoformat(payload["pyzejsonpayload"]["eventTime"])
        payload["pyzejsonpayload"]["collectedEpoch"] = int(dt.timestamp() * 1000)

    # Publish to Kafka
    try:
        producer.produce(
            topic=KAFKA_TOPIC_INGESTION_RAW,
            value=json.dumps(payload).encode("utf-8"),
            callback=delivery_report
        )
        # Poll to trigger delivery callbacks
        producer.poll(0)
        logger.debug("Message published")

        return Response(status_code=202)

    except Exception as exc:
        error_logger.error(f"Error publishing message: {exc}")
        return JSONResponse(
            content={"error": "Failed to publish message"},
            status_code=500
        )


# ------------------------------------------------------------------------------
# Entry Point (Local Run)
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        # Print configuration
        logger.info("Application Configuration:")
        logger.info(f"KAFKA_BOOTSTRAP_SERVERS: {Config.KAFKA_BOOTSTRAP_SERVERS}")
        logger.info(f"KAFKA_TOPIC_INGESTION_RAW: {Config.KAFKA_TOPIC_INGESTION_RAW}")
        logger.info(f"LISTEN_PORT: {Config.LISTEN_PORT}")

        # Start the server
        uvicorn.run(app, host="0.0.0.0", port=int(Config.LISTEN_PORT))
    except Exception as e:
        error_logger.error(f"Failed to start the server: {e}")
        raise
