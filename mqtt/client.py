import logging
import paho.mqtt.client as mqtt
import time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import os
from app.db.influxdb import write_csi_data_to_influxdb, influxdb_client

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
    """
    MQTT 토픽에 메시지가 들어왔을 때 호출되는 콜백 함수
    데이터 파싱 후, InfluxDB 저장 함수를 호출합니다.
    """
    try:
        data_str = msg.payload.decode("utf-8")
        logger.info(f"✅ 메시지 수신: {data_str}")
        
        # 데이터 파싱 로직
        parts = data_str.strip().split(',')
        
        # ... 파싱 로직은 동일
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
        
        csi_data_start_index = data_str.find('"[')
        csi_data_end_index = data_str.rfind(']"') + 2
        csi_data_str = data_str[csi_data_start_index:csi_data_end_index]
        
        logger.info(f"➡️ RSSI: {parsed_data['rssi']}, MAC: {parsed_data['mac']}")
        logger.info(f"➡️ CSI_DATA (길이): {len(csi_data_str)}")

        # 분리된 함수를 호출하여 InfluxDB에 데이터를 저장합니다.
        write_csi_data_to_influxdb(parsed_data, csi_data_str)

    except (IndexError, ValueError) as e:
        logger.error(f"❌ 데이터 파싱 실패: {e}")
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