import os, time, sys, json, logging
from datetime import datetime
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

load_dotenv()
HOST = os.getenv("MQTT_HOST", "localhost")
PORT = int(os.getenv("MQTT_PORT", "1883"))
TOPIC = os.getenv("MQTT_TOPIC", "IOTS/LAB/telemetry")
QOS = int(os.getenv("MQTT_QOS", "1"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [SUB] %(levelname)s: %(message)s")

def on_connect(client, userdata, flags, reason_code, properties=None):
    logging.info(f"Connected with result code {reason_code}")
    client.subscribe(TOPIC, qos=QOS)

def on_message(client, userdata, msg):
    ts = datetime.utcnow().isoformat()
    payload = msg.payload
    logging.info(f"recv topic={msg.topic} qos={msg.qos} bytes={len(payload)} ts={ts}")

def on_disconnect(client, userdata, reason_code, properties=None):
    logging.warning(f"Disconnected: {reason_code}")

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="lab-subscriber")
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    # Optional TLS/username can be added here if needed
    client.will_set(TOPIC, b'{"status":"offline"}', qos=QOS, retain=False)

    client.connect(HOST, PORT, keepalive=60)
    client.loop_forever()

if __name__ == "__main__":
    main()
