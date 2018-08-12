import asyncio
import datetime
import random
import websockets
import json

import deluge_cli

async def hello(websocket, path):
	name = await websocket.recv()
	print(f"< {name}")

	greeting = f"Hello {name}, welcome to the world of websockets!"

	await websocket.send(greeting)
	print(f"> {greeting}")

async def time(websocket, path):
	while True:
		now = datetime.datetime.utcnow().isoformat() + 'Z'
		await websocket.send(now)
		await asyncio.sleep(1)


async def deluge(websocket, path):
	while True:
		downloading = deluge_cli.main(['progress'])
		await websocket.send(json.dumps(downloading))

		await asyncio.sleep(1)

serve_hello = websockets.serve(hello, '0.0.0.0', 8765)
serve_deluge = websockets.serve(deluge, '0.0.0.0', 5678)

asyncio.get_event_loop().run_until_complete(serve_hello)
asyncio.get_event_loop().run_until_complete(serve_deluge)
asyncio.get_event_loop().run_forever()
