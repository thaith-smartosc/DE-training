#!/bin/bash
# Start Kafka Producer and Spark Streaming in background tabs

SCRIPT_DIR="$(dirname "$0")"
ROOT_DIR="$SCRIPT_DIR/.."

# Start Kafka Producer in the current terminal
echo "Starting Kafka Producer..."
cd "$ROOT_DIR/kafka"
python producer.py

sleep 3

# Start Spark Structured Streaming in new terminal
echo "Starting Spark Structured Streaming (opens new terminal)..."
gnome-terminal -- bash -c "cd '$ROOT_DIR/spark'; python spark_streaming.py; exec bash" &



