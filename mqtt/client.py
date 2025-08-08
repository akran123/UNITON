import logging
import paho.mqtt.client as mqtt
import time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import json # JSON 데이터를 처리하기 위해 추가

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MQTT 브로커 설정 (VM 내부에서 실행하므로 localhost 사용)
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "test/topic"

# InfluxDB 설정 (VM 내부에서 실행하므로 localhost 사용)
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")  # <-- 여기에 실제 토큰을 넣어주세요
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

# InfluxDB 클라이언트 초기화
try:
    influxdb_client = InfluxDBClient(
        url=INFLUXDB_URL,
        token=INFLUXDB_TOKEN,
        org=INFLUXDB_ORG
    )
    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
    logger.info("✅ InfluxDB 클라이언트 초기화 성공.")
except Exception as e:
    logger.error(f"❌ InfluxDB 클라이언트 초기화 실패: {e}")
    exit()

# MQTT 클라이언트 인스턴스 생성
mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("✅ MQTT 브로커에 성공적으로 연결되었습니다!")
        client.subscribe(MQTT_TOPIC)
        logger.info(f"➡️ '{MQTT_TOPIC}' 토픽을 구독 중입니다...")
    else:
        logger.error(f"❌ 연결 실패, 반환 코드: {rc}")

def on_message(client, userdata, msg):
    try:
        data_str = msg.payload.decode("utf-8")
        logger.info(f"✅ 메시지 수신: {data_str}")
        
        # 데이터 파싱
        # 데이터 구조: type,mac,rssi,rate,... "[...]"
        parts = data_str.strip().split(',')
        
        # CSI 데이터는 마지막에 문자열로 들어오므로,
        # CSI 데이터 앞까지의 필드를 먼저 파싱합니다.
        # 인덱스 0부터 12까지의 필드를 파싱하고, 나머지를 CSI_DATA로 처리합니다.
        parsed_data = {
            "type": parts[0],
            "mac": parts[1],
            "rssi": int(parts[2]),
            "rate": int(parts[3]),
            "sig_mode": int(parts[4]),
            "mcs": int(parts[5]),
            "ch_width": int(parts[6]),
            "secondary_channel": int(parts[7]),
            "local_timestamp": int(parts[8]),
            "real_time_timestamp": int(parts[9]),
            "rx_state": int(parts[10]),
            "real_time_timestamp_us": int(parts[11]),
        }
        
        # CSI 데이터는 문자열 형태로 추출합니다.
        csi_data_start_index = data_str.find('"[')
        csi_data_end_index = data_str.rfind(']"') + 2 # ']"'까지 포함
        csi_data_str = data_str[csi_data_start_index:csi_data_end_index]

        logger.info(f"➡️ RSSI: {parsed_data['rssi']}, MAC: {parsed_data['mac']}")
        logger.info(f"➡️ CSI_DATA (길이): {len(csi_data_str)}")

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
            .field("remote_timestamp", parsed_data["remote_timestamp"]) \
            .field("rx_state", parsed_data["rx_state"]) \
            .field("real_time_timestamp", parsed_data["real_time_timestamp"]) \
            .field("real_time_timestamp_us", parsed_data["real_time_timestamp_us"]) \
            .field("csi_data_raw", csi_data_str) # CSI 데이터 전체를 문자열로 저장

        # InfluxDB에 데이터 쓰기
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        logger.info("➡️ InfluxDB에 데이터 포인트가 성공적으로 저장되었습니다.")

    except (IndexError, ValueError, json.JSONDecodeError) as e:
        logger.error(f"❌ 데이터 파싱 또는 저장 실패: {e}")
    except Exception as e:
        logger.error(f"❌ 예기치 않은 오류 발생: {e}")

# 콜백 함수 등록
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

try:
    logger.info(f"브로커에 연결 중: {MQTT_BROKER}:{MQTT_PORT}")
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_forever()
except KeyboardInterrupt:
    logger.info("프로그램을 종료합니다.")
except Exception as e:
    logger.error(f"❌ MQTT 연결 실패: {e}")
finally:
    if 'influxdb_client' in locals():
        influxdb_client.close()