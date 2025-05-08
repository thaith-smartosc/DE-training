# Spark + Kafka Streaming Project

This project demonstrates real-time data streaming from Kafka, processed using Apache Spark Structured Streaming. It provides a simple Kafka producer and a Spark streaming script to consume and process messages in real-time.

## 📄 Table of Contents

- [Spark + Kafka Streaming Project](#spark--kafka-streaming-project)
  - [📄 Table of Contents](#-table-of-contents)
  - [📝 Overview](#-overview)
  - [🗂️ Project Structure](#️-project-structure)
  - [⚙️ Requirements](#️-requirements)
  - [🚀 Setup Instructions](#-setup-instructions)
    - [1. Start Kafka and Zookeeper](#1-start-kafka-and-zookeeper)
    - [2. Run the Kafka Producer](#2-run-the-kafka-producer)
    - [3. Run the Spark Streaming Script](#3-run-the-spark-streaming-script)
  - [🛠️ Customization](#️-customization)
  - [🩺 Troubleshooting](#-troubleshooting)
- [📦 **Hệ thống gồm 2 phần chính:**](#-hệ-thống-gồm-2-phần-chính)
  - [🎯 **Producer gửi dữ liệu gì?**](#-producer-gửi-dữ-liệu-gì)
  - [🔎 **Spark Structured Streaming đọc và xử lý gì?**](#-spark-structured-streaming-đọc-và-xử-lý-gì)
  - [📝 **Tóm tắt Workflow:**](#-tóm-tắt-workflow)

---

## 📝 Overview

- **Kafka** acts as the message broker, receiving and storing streaming messages (e.g., from the sample producer).
- **Apache Spark Structured Streaming** consumes and processes these messages in real time.

---

## 🗂️ Project Structure

```
project-root/
│
├── kafka/                 # Kafka producer/consumer code
│   └── producer.py
├── spark/                 # Spark streaming code
│   └── spark_streaming.py
├── configs/               # Sample Kafka/Spark config files
├── scripts/               # Utilities to start/stop services, create topics
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── .gitignore
```

---

## ⚙️ Requirements

- Python 3.8+
- Apache Kafka (locally installed or Docker)
- Apache Spark 3.x (with PySpark)
- Python packages in `requirements.txt`:
  - `pyspark`
  - `kafka-python`

**Install Python dependencies:**
```bash
pip install -r requirements.txt
```

---

## 🚀 Setup Instructions

### 1. Start Kafka and Zookeeper

If you're using Docker Compose (recommended for cp-kafka):

```bash
docker-compose up -d
```
- Ensure that ports and advertised listeners in `docker-compose.yml` match your scripts and producer.

To shut down:
```bash
docker-compose down
```


### 2. Run the Kafka Producer
Open a new terminal:
```bash
python kafka/producer.py
```

### 3. Run the Spark Streaming Script
Open another terminal:
```bash
python spark/spark_streaming.py
```

---

## 🛠️ Customization

- To change the Kafka topic, update the topic name in both the producer and Spark scripts.
- For advanced transformations, edit `spark_streaming.py` (e.g., process data, run analytics).

---

## 🩺 Troubleshooting

- **Kafka Errors:** Make sure Zookeeper and Kafka are both running before starting producer or Spark jobs.
- **Connection Issues:** Ensure `localhost:9092` (or configured broker) is correct.
- **Dependency Errors:** Reinstall requirements via `pip install -r requirements.txt`.

---

# 📦 **Hệ thống gồm 2 phần chính:**
1. **Kafka Producer:** Sinh và gửi dữ liệu sensor (JSON) lên Kafka topic.
2. **Spark Structured Streaming:** Lấy dữ liệu từ Kafka, parse/hiển thị/tiền xử lý trên console.

---

## 🎯 **Producer gửi dữ liệu gì?**  
**(What does the producer send?)**

Producer liên tục sinh ra các bản ghi dạng JSON đại diện cho giá trị đo từ nhiều sensor môi trường, gồm các trường sau:

```json
{
  "sensor_id": "1",
  "temperature": 30.5,
  "humidity": 55.2,
  "pressure": 1012.4,
  "pm25": 40.3,
  "pm10": 65.1,
  "co2": 900.0
}
```
- **Giải thích:**
  - `sensor_id`: ID của thiết bị sensor (chuỗi số).
  - `temperature`: Nhiệt độ (°C), giá trị thực.
  - `humidity`: Độ ẩm (%), giá trị thực.
  - `pressure`: Áp suất (hPa), giá trị thực.
  - `pm25`, `pm10`: Chỉ số bụi mịn (µg/m³).
  - `co2`: Hàm lượng CO2 trong không khí (ppm).

**Producer sẽ gửi một bản ghi mới lên Kafka topic `sensor-data-full` mỗi giây.**

---

## 🔎 **Spark Structured Streaming đọc và xử lý gì?**  
**(What does Spark streaming consume and process?)**

- **Spark đọc trực tiếp các bản ghi từ Kafka topic** `sensor-data-full`.
- **Parse dữ liệu JSON** thành các cột/kiểu dữ liệu Spark.
- **Hiển thị kết quả từng batch lên màn hình console** ở dạng bảng rõ ràng ("pretty").

Ví dụ kết quả console:
```
+---------+-----------+--------+--------+-----+-----+------+
|sensor_id|temperature|humidity|pressure|pm25|pm10| co2  |
+---------+-----------+--------+--------+-----+-----+------+
|   1     |   31.0    |  52.3  | 1009.7 | 10.4|22.3| 630  |
+---------+-----------+--------+--------+-----+-----+------+
|   3     |   28.7    |  60.1  | 1003.5 | 15.1|23.1| 800  |
+---------+-----------+--------+--------+-----+-----+------+
```

**(Spark does NOT yet store, aggregate, or transform further—it just parses and prints.  
Bạn có thể mở rộng để ghi xuống DB, tính toán trung bình, phát hiện bất thường, v.v. theo nhu cầu.)**

---

## 📝 **Tóm tắt Workflow:**

1. **Start Kafka/Zookeeper container bằng Docker Compose**
2. **Start cả producer và spark consumer  
   bằng lệnh:**  
   ```bash
   ./scripts/start_all.sh
   ```
3. **Producer phát dữ liệu sensor lên Kafka**  
4. **Spark đọc, parse, và hiển thị sensor lên cửa sổ console**

---
