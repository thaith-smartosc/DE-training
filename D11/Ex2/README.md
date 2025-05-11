# Kafka Avro Schema Management with Python

## 🌟 Overview

This project demonstrates how to implement **Avro schema management** for Kafka with Python, focusing on:
- Designing Avro schemas for structured data
- Configuring and using Schema Registry
- Creating Kafka producers with Avro serialization
- Building Kafka consumers with Avro deserialization
- Handling schema evolution while maintaining compatibility

## 🔧 Prerequisites

- Docker and Docker Compose
- Python 3.7+
- `pip` packages:
  - `confluent-kafka`
  - `confluent-kafka[avro]`
  - `requests`

## 🚀 Setup

1. **Install dependencies**:
   ```bash
   pip install confluent-kafka confluent-kafka[avro] requests
   ```

2. **Start the Kafka ecosystem**:
   ```bash
   docker-compose up -d
   ```

3. **Verify services are running**:
   ```bash
   curl http://localhost:8081/subjects
   ```

## 📂 Project Structure

```
kafka-avro-python/
├── schemas/
│   ├── user_v1.avsc       # Initial schema
│   └── user_v2.avsc       # Evolved schema with new field
├── producer.py            # Avro producer
├── consumer.py            # Avro consumer
├── schema_evolution.py    # Demonstrates schema changes
├── docker-compose.yml     # Docker setup
└── README.md              # This file
```

## 📝 Step-by-Step Guide

### 1. Starting the Infrastructure

The `docker-compose.yml` file creates a complete environment with:
- Zookeeper for Kafka coordination
- Kafka broker for message handling
- Schema Registry for managing Avro schemas

Run:
```bash
docker-compose up -d
```

### 2. Producing Messages with Avro Schema

The producer:
- Loads the Avro schema from file
- Configures connection to Kafka and Schema Registry
- Serializes data according to the schema
- Sends records to Kafka

Run:
```bash
python producer.py
```

### 3. Consuming Messages with Avro Schema

The consumer:
- Connects to Kafka and Schema Registry
- Automatically retrieves the correct schema for deserialization
- Deserializes and processes the messages

Run:
```bash
python consumer.py
```

### 4. Schema Evolution

The schema evolution script:
- Checks compatibility of a new schema version with the existing one
- Registers the new schema if compatible
- Produces messages using the new schema format

Run:
```bash
python schema_evolution.py
```

## 🔄 Schema Evolution Explained

Schema evolution allows changing data structures without breaking producers or consumers:

1. **Original Schema**: Contains basic user fields (id, name, email)
2. **Evolution**: Adding optional fields with defaults (age)
3. **Compatibility Types**:
   - **Backward**: New schema can read old data
   - **Forward**: Old schema can read new data
   - **Full**: Both backward and forward compatible

The Schema Registry enforces these compatibility rules automatically.

## ⚙️ Configuration Options

### Schema Registry

- Default URL: `http://localhost:8081`
- Key endpoints:
  - `/subjects` - List all schemas
  - `/subjects/{subject}/versions` - List versions of a schema
  - `/compatibility/subjects/{subject}/versions/latest` - Check compatibility

### Kafka Producer/Consumer

- Bootstrap servers: `localhost:9092`
- Key configuration:
  - Schema Registry URL
  - Serialization/deserialization settings
  - Consumer group ID

## 🛠️ Troubleshooting

- **Schema Registry not responding**: Ensure the container is running with `docker ps`
- **Serialization errors**: Verify schema format and compatibility
- **Connection refused**: Check that the Kafka broker is accessible

## 🧪 Example Output

When running the consumer after schema evolution:

```
Starting Avro consumer...
Received user record:
  ID: 1
  Name: John Doe
  Email: john.doe@example.com
-----------------------
Received user record:
  ID: 2
  Name: Jane Smith
  Email: jane.smith@example.com
-----------------------
Received user record:
  ID: 3
  Name: Bob Johnson
  Email: bob.johnson@example.com
  Age: 25
-----------------------
```

## 📚 Additional Resources

- [Confluent Schema Registry Documentation](https://docs.confluent.io/platform/current/schema-registry/index.html)
- [Apache Avro Documentation](https://avro.apache.org/docs/)
- [Confluent Python Client for Apache Kafka](https://github.com/confluentinc/confluent-kafka-python)