import os
import time
import json
import random
import logging
from datetime import datetime
from faker import Faker
from kafka import KafkaProducer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DataSimulator")

# Initialize constants
faker = Faker()

CATEGORIES = {
    "Electronics": ["Smartphone", "Laptop", "Headphones", "Smartwatch"],
    "Clothing": ["T-Shirt", "Jeans", "Jacket", "Sneakers"],
    "Home & Kitchen": ["Mixer", "Cookware", "Vacuum", "Chair"],
    "Beauty": ["Lipstick", "Perfume", "Moisturizer", "Foundation"],
    "Books": ["Fiction", "Biography", "Science", "Philosophy"],
    "Sports": ["Football", "Yoga Mat", "Tennis Racket", "Cycling Gloves"]
}
PAYMENT_METHODS = ["Credit Card", "PayPal", "Crypto", "Cash on Delivery", "Debit Card"]
SHIPPING_METHODS = ["Standard", "Express", "Overnight"]
CHANNELS = ["Web", "Mobile App", "In-Store"]
LOYALTY_TIERS = ["Bronze", "Silver", "Gold", "Platinum"]
DISCOUNT_OPTIONS = [0, 0, 0, 5, 10, 15, 20]
COUNTRIES_CITIES = [
    ("USA", "New York"), ("USA", "San Francisco"), ("Canada", "Toronto"),
    ("UK", "London"), ("Germany", "Berlin"), ("India", "Mumbai"),
    ("Japan", "Tokyo"), ("Australia", "Sydney"), ("Brazil", "São Paulo"),
    ("France", "Paris")
]


def get_kafka_producer(bootstrap_servers: str) -> KafkaProducer:
    """Create a Kafka producer with retries."""
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            logger.info("Kafka Producer connected.")
            return producer
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}. Retrying in 5 seconds...")
            time.sleep(5)


def generate_transaction(counter: int) -> dict:
    """Generate a synthetic transaction."""
    timestamp = datetime.utcnow().isoformat()
    country, city = random.choice(COUNTRIES_CITIES)
    category = random.choice(list(CATEGORIES.keys()))
    product_name = random.choice(CATEGORIES[category])
    product_id = f"{category[:3].upper()}-{random.randint(1000, 9999)}"
    quantity = random.randint(1, 4)
    price = round(random.uniform(10, 1000), 2)
    discount_percent = random.choice(DISCOUNT_OPTIONS)
    shipping_cost = round(random.uniform(5, 25), 2)

    subtotal = price * quantity
    discount_amount = round(subtotal * discount_percent / 100, 2)
    order_total = round(subtotal - discount_amount + shipping_cost, 2)

    return {
        "transaction_id": f"T{counter:07d}",
        "timestamp": timestamp,
        "customer_id": f"C{random.randint(1, 1000):05d}",
        "loyalty_tier": random.choices(LOYALTY_TIERS, weights=[0.4, 0.3, 0.2, 0.1])[0],
        "customer_region": country,
        "channel": random.choice(CHANNELS),
        "product_category": category,
        "product_id": product_id,
        "product_name": product_name,
        "price": price,
        "quantity": quantity,
        "payment_method": random.choice(PAYMENT_METHODS),
        "shipping_country": country,
        "shipping_city": city,
        "discount_percent": discount_percent,
        "shipping_method": random.choice(SHIPPING_METHODS),
        "shipping_cost": shipping_cost,
        "customer_lifetime_value": round(random.uniform(100, 10000), 2),
        "order_total": order_total
    }


def main():
    kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic_name = os.getenv("TRANSACTION_TOPIC", "transactions_topic")

    producer = get_kafka_producer(kafka_servers)
    logger.info(f"Starting data simulation. Publishing to '{topic_name}' on {kafka_servers}")

    counter = 1
    try:
        while True:
            transaction = generate_transaction(counter)
            producer.send(topic_name, transaction)
            logger.info(f"Produced: {transaction}")
            counter += 1
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Data simulator stopped by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
