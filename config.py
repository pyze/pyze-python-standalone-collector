import os


class Config:
    # Basic Kafka and app configuration
    KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    KAFKA_TOPIC_INGESTION_RAW = os.environ.get('KAFKA_TOPIC_INGESTION_RAW', 'quickstart')
    LISTEN_PORT = int(os.environ.get('LISTEN_PORT', 9001))

    # SSL configuration (optional)
    # Set KAFKA_USE_SSL=true to enable SSL settings
    KAFKA_USE_SSL = os.environ.get('KAFKA_USE_SSL', 'false').lower() == 'true'
    KAFKA_SSL_CA_LOCATION = os.environ.get('KAFKA_SSL_CA_LOCATION', '/path/to/ca-cert.pem')
    KAFKA_SSL_CERTIFICATE_LOCATION = os.environ.get('KAFKA_SSL_CERTIFICATE_LOCATION', '/path/to/client-cert.pem')
    KAFKA_SSL_KEY_LOCATION = os.environ.get('KAFKA_SSL_KEY_LOCATION', '/path/to/client-key.pem')
