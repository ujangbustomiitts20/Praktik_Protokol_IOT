import os, argparse, time, logging, json, requests
from dotenv import load_dotenv
from tools.payload_gen import gen_payload

load_dotenv()
HOST = os.getenv("HTTP_HOST","127.0.0.1")
PORT = int(os.getenv("HTTP_PORT","5000"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [HTTP-CLI] %(levelname)s: %(message)s")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=10)
    ap.add_argument("--payload", type=int, default=32)
    args = ap.parse_args()
    url = f"http://{HOST}:{PORT}/ingest"
    for i in range(args.count):
        body = {
            "device_id":"dev-001",
            "seq": i,
            "payload": gen_payload(args.payload).decode("latin1")
        }
        r = requests.post(url, json=body, timeout=5)
        logging.info(f"POST {r.status_code} len={len(json.dumps(body))}")
    logging.info("done")

if __name__ == "__main__":
    main()
