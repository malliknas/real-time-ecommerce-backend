import os
import time
import json
import logging
import psycopg2
from kafka import KafkaConsumer, errors
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Consumer")


def init_db():
    """Initializes and returns a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            dbname=os.getenv("POSTGRES_DB", "financial_db")
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ecommerce_transactions (
                transaction_id VARCHAR(50) PRIMARY KEY,
                timestamp TIMESTAMP,
                customer_id VARCHAR(50),
                loyalty_tier VARCHAR(20),
                customer_region VARCHAR(50),
                channel VARCHAR(20),
                product_category VARCHAR(100),
                product_id VARCHAR(50),
                product_name VARCHAR(200),
                price NUMERIC,
                quantity INT,
                payment_method VARCHAR(50),
                shipping_country VARCHAR(100),
                shipping_city VARCHAR(100),
                discount_percent NUMERIC,
                shipping_method VARCHAR(50),
                shipping_cost NUMERIC,
                order_total NUMERIC
            );
        """)
        cur.close()
        logger.info("Database initialized and table ensured.")
        return conn
    except Exception as e:
        logger.error(f"DB connection or initialization failed: {e}")
        raise


def insert_transaction(conn, tx):
    """Inserts a transaction into the ecommerce_transactions table."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO ecommerce_transactions (
                    transaction_id, timestamp, customer_id, loyalty_tier,
                    customer_region, channel, product_category, product_id,
                    product_name, price, quantity, payment_method,
                    shipping_country, shipping_city, discount_percent,
                    shipping_method, shipping_cost, order_total
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (transaction_id) DO NOTHING;
            """, (
                tx["transaction_id"],
                tx["timestamp"],
                tx["customer_id"],
                tx["loyalty_tier"],
                tx["customer_region"],
                tx["channel"],
                tx["product_category"],
                tx["product_id"],
                tx["product_name"],
                tx["price"],
                tx["quantity"],
                tx["payment_method"],
                tx["shipping_country"],
                tx["shipping_city"],
                tx["discount_percent"],
                tx["shipping_method"],
                tx["shipping_cost"],
                tx["order_total"]
            ))
        logger.info(f"Inserted transaction: {tx['transaction_id']}")
    except Exception as e:
        logger.error(f"Failed to insert transaction {tx.get('transaction_id', 'UNKNOWN')}: {e}")


def wait_for_kafka(bootstrap_servers, topic, retries=10, delay=5):
    """Waits for Kafka broker to become available."""
    for attempt in range(1, retries + 1):
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=[bootstrap_servers],
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                group_id="connectivity_check",
                value_deserializer=lambda v: json.loads(v.decode("utf-8"))
            )
            consumer.close()
            logger.info("Kafka broker is available.")
            return
        except errors.NoBrokersAvailable:
            logger.warning(f"No Kafka brokers available, retrying in {delay}s... (Attempt {attempt}/{retries})")
            time.sleep(delay)
    raise ConnectionError("Kafka broker not available after several retries.")


def main():
    # Database connection retry loop
    conn = None
    while not conn:
        try:
            conn = init_db()
        except Exception as e:
            logger.error(f"Waiting to retry DB connection: {e}")
            time.sleep(5)

    kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic = os.getenv("TRANSACTION_TOPIC", "transactions_topic")

    wait_for_kafka(kafka_bootstrap, topic)

    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=[kafka_bootstrap],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="ecommerce_consumer_group",
        value_deserializer=lambda v: json.loads(v.decode("utf-8"))
    )
    logger.info(f"Kafka consumer started. Listening to topic: '{topic}'")

    try:
        for message in consumer:
            tx = message.value
            insert_transaction(conn, tx)
    except KeyboardInterrupt:
        logger.info("Consumer stopped by user.")
    except Exception as e:
        logger.error(f"Unexpected error in consumer loop: {e}")


if __name__ == "__main__":
    main()
