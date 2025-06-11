import os
import logging
from typing import List
from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FastAPI-App")

app = FastAPI(title="E-commerce Transaction API")


def get_db_connection():
    """Establish and return a PostgreSQL database connection."""
    try:
        return psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            dbname=os.getenv("POSTGRES_DB", "financial_db"),
            cursor_factory=RealDictCursor
        )
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed.")


@app.get("/health", tags=["Utility"])
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/transactions/all", tags=["Transactions"])
def get_all_transactions():
    """
    Fetch all transactions from the database,
    ordered by latest timestamp.
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT transaction_id, timestamp, customer_id, loyalty_tier,
                           customer_region, channel, product_category, product_id,
                           product_name, price, quantity, payment_method,
                           shipping_country, shipping_city, discount_percent,
                           shipping_method, shipping_cost, order_total
                    FROM ecommerce_transactions
                    ORDER BY timestamp DESC;
                """)
                rows = cur.fetchall()
                return {"all_transactions": rows}
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch transactions.")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
