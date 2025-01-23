import os


class Config:
    KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    KAFKA_TOPIC_INGESTION_RAW = os.environ.get('KAFKA_TOPIC_INGESTION_RAW', "quickstart")
    LISTEN_PORT = os.environ.get('LISTEN_PORT', 9001)