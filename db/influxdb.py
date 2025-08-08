import os
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import logging

INFLUXDB_URL = "http://influxdb:8086" 
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 스크립트 상단: InfluxDB 클라이언트 및 API 초기화
try:
    influxdb_client = InfluxDBClient(
        url=INFLUXDB_URL,
        token=INFLUXDB_TOKEN,
        org=INFLUXDB_ORG
    )
    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)

except Exception as e:
    exit()


def write_csi_data_to_influxdb(parsed_data, csi_data_str):
    """
    파싱된 CSI 데이터를 InfluxDB에 저장하는 함수
    """
    try:
        # InfluxDB에 저장할 데이터 포인트 생성
        point = Point("csi_measurement") \
            .tag("type", parsed_data["type"]) \
            .tag("mac", parsed_data["mac"]) \
            .tag("device_id", "esp32-device-01") \
            .field("rssi", parsed_data["rssi"]) \
            .field("rate", parsed_data["rate"]) \
            .field("sig_mode", parsed_data["sig_mode"]) \
            .field("mcs", parsed_data["mcs"]) \
            .field("ch_width", parsed_data["ch_width"]) \
            .field("secondary_channel", parsed_data["secondary_channel"]) \
            .field("local_timestamp", parsed_data["local_timestamp"]) \
            .field("real_time_timestamp", parsed_data["real_time_timestamp"]) \
            .field("rx_state", parsed_data["rx_state"]) \
            .field("real_time_timestamp_us", parsed_data["real_time_timestamp_us"]) \
            .field("csi_data_raw", csi_data_str) # CSI 데이터 전체를 문자열로 저장

        # InfluxDB에 데이터 쓰기
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        logger.info(f"➡️ InfluxDB에 데이터 포인트가 성공적으로 저장되었습니다.")

    except Exception as e:
        logger.error(f"❌ InfluxDB에 데이터 쓰기 실패: {e}")
        