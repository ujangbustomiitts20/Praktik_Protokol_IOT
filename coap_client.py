import asyncio, argparse, logging, os
from dotenv import load_dotenv
from aiocoap import Context, Message, POST
from tools.payload_gen import gen_payload

load_dotenv()
HOST = os.getenv("COAP_HOST","127.0.0.1")
PORT = int(os.getenv("COAP_PORT","5683"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [COAP-CLI] %(levelname)s: %(message)s")

async def run(count, payload):
    context = await Context.create_client_context()
    uri = f"coap://{HOST}:{PORT}/telemetry"
    for i in range(count):
        data = gen_payload(payload)
        req = Message(code=POST, uri=uri, payload=data)
        resp = await context.request(req).response
        logging.info(f"POST {resp.code} bytes={len(data)}")
    await context.shutdown()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=10)
    ap.add_argument("--payload", type=int, default=32)
    args = ap.parse_args()
    asyncio.run(run(args.count, args.payload))

if __name__ == "__main__":
    main()
