# Real-time Data Pipeline with Kafka, Flink and BigQuery
## (Hệ thống xử lý dữ liệu thời gian thực sử dụng Kafka, Flink và BigQuery)

## 📌 Mục đích/Mục tiêu (Purpose)
Xây dựng pipeline xử lý dữ liệu clickstream thời gian thực:
- **Producer**: Tạo dữ liệu clickstream giả lập
- **Kafka**: Trung gian truyền dữ liệu
- **Flink**: Xử lý dữ liệu thời gian thực
- **BigQuery**: Lưu trữ kết quả

(Build a real-time clickstream processing pipeline:
- **Producer**: Generates synthetic clickstream data
- **Kafka**: Message broker
- **Flink**: Real-time processing
- **BigQuery**: Storage for processed results)

## 🛠 Công nghệ sử dụng (Technology Stack)
- **Apache Kafka** (Message Broker)
- **Apache Flink** (Stream Processing)
- **Google BigQuery** (Data Warehouse)
- **Python** (Producer & Flink Job)
- **Docker** (Containerization)

## 🚀 Cách chạy (How to Run)

### Điều kiện tiên quyết (Prerequisites)
- Docker Desktop
- Python 3.7+
- GCP Service Account Key


### 1. Khởi động hệ thống (Start Infrastructure)
```bash
docker-compose up -d
```

### 2. Chạy Kafka Producer
```bash
cd kafka-producer
pip install -r requirements.txt
python producer.py
```

### 3.1 Setup env Flink Job
```bash
docker exec -it ex1-jobmanager-1 /bin/bash

apt-get update && apt-get install -y python3 python3-pip

ln -s /usr/bin/python3 /usr/bin/python

pip install -r /opt/flink/usrlib/src/main/python/requirements.txt

echo "python.executable: /usr/bin/python3.10" >> /opt/flink/conf/flink-conf.yaml
echo "python.client.executable: /usr/bin/python3.10" >> /opt/flink/conf/flink-conf.yaml

export PYFLINK_EXECUTABLE=/usr/bin/python3.10
export PYFLINK_PYTHON=/usr/bin/python3.10
export PYTHONPATH=/opt/flink/usrlib/src/main/python
```

### 3.2 Submit Flink Job
```bash
docker exec -it flink-jobmanager_1 \
  PYFLINK_EXECUTABLE=/usr/bin/python3.10 PYFLINK_PYTHON=/usr/bin/python3.10 flink run -py stream-process.py -pyexec /usr/bin/python3.10 -pyfs /opt/flink/usrlib/src/main/python
```

### 4. Giám sát (Monitoring)
- **Kafka UI**: http://localhost:8080
- **Flink Dashboard**: http://localhost:8081
- **BigQuery**: Truy cập GCP Console

## 📂 Cấu trúc thư mục (Project Structure)
```
.
├── docker-compose.yml          # Docker configuration
├── kafka-producer/            # Kafka producer code
│   ├── producer.py            # Clickstream generator
│   └── requirements.txt       # Python dependencies
└── flink-job/                 # Flink processing
    ├── src/main/python/       # Flink Python code
    │   └── stream_processor.py 
    └── src/main/resources/    # GCP credentials
        └── gcp_credentials.json
```

## ⚙ Cấu hình (Configuration)
| File | Mục đích (Purpose) |
|------|-------------------|
| `docker-compose.yml` | Cấu hình Kafka, Flink containers |
| `producer.py` | Tạo dữ liệu clickstream ngẫu nhiên |
| `stream_processor.py` | Xử lý dữ liệu và ghi vào BigQuery |

## 🔍 Kiểm tra dữ liệu (Data Verification)
```sql
-- BigQuery SQL
SELECT * FROM `your-project.clickstream_dataset.user_activity` 
ORDER BY processing_time DESC LIMIT 10
```

## 🛠 Khắc phục sự cố (Troubleshooting)
1. **Kafka connection issues**:
   ```bash
   docker exec -it kafka kafka-topics --list --bootstrap-server kafka:29092
   ```

2. **Flink job failures**:
   ```bash
   docker logs flink-jobmanager_1
   ```

3. **BigQuery permissions**:
   - Kiểm tra Service Account có quyền `BigQuery Data Editor`



