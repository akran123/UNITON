import os
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


INFLUXDB_URL = "http://influxdb:8086" 
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

def write_to_influxdb(sensor_data: schemas.SensorData):
    """센서 데이터를 InfluxDB에 저장하는 함수"""
    with InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)

        # InfluxDB에 저장할 데이터 포인트(Point)를 생성합니다.
        point = Point("sensor_data") \
            .tag("device_id", sensor_data.device_id) \
            .field("temperature", sensor_data.temperature) \
            .field("humidity", sensor_data.humidity)

        # 지정된 버킷(Bucket)에 데이터를 씁니다.
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        print(f"✅ Successfully wrote to InfluxDB: {sensor_data.device_id}")
        