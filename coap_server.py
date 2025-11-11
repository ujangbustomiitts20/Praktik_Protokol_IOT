import asyncio, logging, os
from dotenv import load_dotenv
from aiocoap import resource, Context, Message, Code

load_dotenv()
HOST = os.getenv("COAP_HOST","127.0.0.1")
PORT = int(os.getenv("COAP_PORT","5683"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [COAP-SRV] %(levelname)s: %(message)s")

class Telemetry(resource.Resource):
    async def render_post(self, request):
        logging.info(f"recv {len(request.payload)} bytes")
        return Message(code=Code.CONTENT, payload=b"OK")

async def main():
    root = resource.Site()
    root.add_resource(('telemetry',), Telemetry())
    context = await Context.create_server_context(root, bind=(HOST, PORT))
    logging.info(f"CoAP server on coap://{HOST}:{PORT}/telemetry")
    await asyncio.get_running_loop().create_future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
