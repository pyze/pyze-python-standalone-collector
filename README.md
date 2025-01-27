# Standalone Python Collector

HTTP POST -> Kafka

Basic config set via env vars defined in config.py

## Configuration

To configure the application, you can set the following environment variables:

1. **Kafka Bootstrap Servers**
    - **Variable**: `KAFKA_BOOTSTRAP_SERVERS`
    - **Default**: `localhost:9092`
    - **Description**: A comma-separated list of Kafka brokers to connect to.

2. **Kafka Topic for Ingestion**
    - **Variable**: `KAFKA_TOPIC_INGESTION_RAW`
    - **Default**: `quickstart`
    - **Description**: The Kafka topic where data will be sent.

3. **Application Listen Port**
    - **Variable**: `LISTEN_PORT`
    - **Default**: `9001`
    - **Description**: The port on which the FastAPI server will listen for HTTP requests.

## Example Configuration

You can configure the application by setting environment variables or using a `.env` file. Here is an example `.env`
file:

```env
# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS=broker1:9092,broker2:9092
KAFKA_TOPIC_INGESTION_RAW=my-ingestion-topic

# Application settings
LISTEN_PORT=8080
```

## Running the Application

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python main.py
   ```

3. Use the provided API endpoints to send HTTP POST requests, which will be forwarded to the specified Kafka topic.
