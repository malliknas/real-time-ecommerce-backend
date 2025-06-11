#!/bin/bash
set -e

echo "Waiting for Kafka to be available at kafka:9092..."

while ! nc -z kafka 9092; do
  sleep 1
done

echo "Kafka is up - starting simulator..."
exec python data_simulator.py

