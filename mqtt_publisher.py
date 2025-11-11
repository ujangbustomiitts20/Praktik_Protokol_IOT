import os, argparse, time, json, logging, random
from datetime import datetime
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from tools.payload_gen import gen_payload

load_dotenv()
HOST = os.getenv("MQTT_HOST", "localhost")
PORT = int(os.getenv("MQTT_PORT", "1883"))
TOPIC = os.getenv("MQTT_TOPIC", "IOTS/LAB/telemetry")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [PUB] %(levelname)s: %(message)s")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--qos", type=int, default=int(os.getenv("MQTT_QOS","1")), choices=[0,1,2])
    ap.add_argument("--count", type=int, default=10)
    ap.add_argument("--rate", type=float, default=0)  # messages per second, 0 = as fast as possible
    ap.add_argument("--payload", type=int, default=32) # bytes
    ap.add_argument("--retain", action="store_true")
    args = ap.parse_args()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"lab-publisher-{int(time.time())}")
    client.connect(HOST, PORT, keepalive=60)
    client.loop_start()

    interval = 1.0/args.rate if args.rate>0 else 0
    for i in range(args.count):
        body = gen_payload(args.payload)
        msg = json.dumps({
            "device_id":"dev-001",
            "seq": i,
            "ts": datetime.utcnow().isoformat(),
            "payload": body.decode("latin1")  # keep binary-ish bytes pass-through
        }).encode("latin1")
        info = client.publish(TOPIC, msg, qos=args.qos, retain=args.retain)
        info.wait_for_publish()
        logging.info(f"sent i={i} qos={args.qos} bytes={len(msg)} rc={info.rc}")
        if interval>0:
            time.sleep(interval)

    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    main()
