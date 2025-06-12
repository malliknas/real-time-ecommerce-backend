
---

# Real-Time E-commerce Backend

This project implements a **real-time backend architecture** for processing and visualizing synthetic e-commerce transaction data using a fully containerized microservices approach. The system is designed to simulate, stream, store, and visualize transaction flows in real-time using technologies like **Apache Kafka**, **PostgreSQL**, **FastAPI**, and **Streamlit**, all orchestrated through **Docker Compose**.

The goal is to establish a reliable, scalable, and maintainable infrastructure for handling high-throughput transaction streams. Kafka enables fault-tolerant ingestion, while FastAPI serves RESTful endpoints for dashboard integration. PostgreSQL is used as the persistent storage backend, and the user-friendly Streamlit interface allows live monitoring of transaction KPIs. This setup also supports local development and testing through Docker and `.env` configuration, enabling seamless reproducibility.

---

## 🧩 System Components

### Microservices

* 🧪 **Simulator**: Publishes synthetic transaction events to Kafka.
* 📬 **Kafka Broker + ZooKeeper**: Facilitates distributed event streaming.
* 📥 **Consumer**: Consumes Kafka messages and persists data to PostgreSQL.
* 🧠 **Backend API (FastAPI)**: Serves REST endpoints for transactions.
* 🗃️ **PostgreSQL**: Stores structured transaction data.
* 📈 **Dashboard (Streamlit)**: Displays real-time analytics using backend API.

---

## 🏗️ Architecture Diagram

```
    A[Simulator] -->|Send Events| B(Kafka Broker)
    B --> C[Consumer]
    C --> D[(PostgreSQL)]
    D --> E[FastAPI Backend]
    E --> F[Streamlit Dashboard]
```

---

## 🚀 Quick Start

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/malliknas/real-time-ecommerce-backend.git
cd real-time-ecommerce-backend
```

### 2️⃣ Make Kafka Wait Script Executable

The simulator includes a script (`wait-for-kafka.sh`) that ensures Kafka is available before sending data.
You must mark it executable:

```bash
chmod +x simulator/wait-for-kafka.sh
```

### 2️⃣ Start All Services

```bash
docker-compose up --build
```

This will start all components: Kafka, ZooKeeper, PostgreSQL, Simulator, Consumer, Backend API, and the Streamlit Dashboard.

> ✅ Prerequisites: Ensure Docker & Docker Compose are installed.

---

## 🔎 Service Access & Test

| Component           | URL / Command                                                                    |
| ------------------- | -------------------------------------------------------------------------------- |
| FastAPI Docs        | [http://localhost:8000/docs](http://localhost:8000/docs)                         |
| Streamlit Dashboard | [http://localhost:8501](http://localhost:8501)                                   |
| PostgreSQL Shell    | `docker-compose exec db psql -U postgres -d financial_db`                        |
| Kafka Topic Check   | `docker-compose exec kafka kafka-topics.sh --list --bootstrap-server kafka:9092` |

---

## 📁 Folder Structure

```bash
.
├── .env
├── docker-compose.yml
├── Architecture/
│   ├── architecture.png
│   ├── fastapi_swagger.png
│   ├── streamlit_dashboard.png
│   └── kafka_output.png
├── backend/
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
├── consumer/
│   ├── consumer.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
├── dashboard/
│   ├── dashboard.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
├── simulator/
│   ├── data_simulator.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── wait-for-kafka.sh
│   └── .env
```

---

## ⚙️ Environment Variables (`.env`)

```env
# PostgreSQL
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=financial_db

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
TRANSACTION_TOPIC=transactions_topic

# Backend API
API_BASE_URL=http://backend:8000
```

---

## 🐍 Local Run (Manual)

```bash
# Start core services first
docker-compose up kafka zookeeper db

# Then run each microservice locally

# Simulator
cd simulator
python data_simulator.py

# Consumer
cd consumer
python consumer.py

# Backend
cd backend
uvicorn app:app --host 0.0.0.0 --port 8000

# Dashboard
cd dashboard
streamlit run dashboard.py
```

---

## ✅ Validate Setup

```bash
# Kafka
docker-compose exec kafka kafka-console-consumer.sh \
  --bootstrap-server kafka:9092 \
  --topic transactions_topic \
  --from-beginning

# PostgreSQL Query
docker-compose exec db psql -U postgres -d financial_db
# Then run:
SELECT * FROM transactions LIMIT 10;

# Test API
curl http://localhost:8000/transactions/all
```

---

## 🔒 Python Requirements Summary

Each service has its own `requirements.txt`, here’s a reference:

### `simulator/requirements.txt`

```
faker
kafka-python
python-dotenv
```

### `consumer/requirements.txt`

```
kafka-python
psycopg2-binary
python-dotenv
```

### `backend/requirements.txt`

```
fastapi
uvicorn
psycopg2-binary
python-dotenv
```

### `dashboard/requirements.txt`

```
streamlit
pandas
plotly
requests
python-dotenv
streamlit-autorefresh
```

---

## 🌟 Features

* 🧠 Kafka-based streaming pipeline
* 🔄 Real-time transaction simulation and ingestion
* 🔍 REST API endpoints for filtered data
* 🧮 PostgreSQL-backed persistent storage
* 📈 Live dashboard using Streamlit
* 🐳 Dockerized microservices architecture

---

## 📸 Screenshots

> Screenshots for:
>
> * Architecture
> * Kafka consumer output
> * FastAPI Swagger UI
> * Streamlit Dashboard
>
> ➡️ Added in `Architecture/`.

---

## 🧑‍💻 Author

**Malik Naseruddin**
IU University – Task Submission
`AI Use Case Project`

---

## 📄 License

This project is open-source and free to use under the MIT License.

```
