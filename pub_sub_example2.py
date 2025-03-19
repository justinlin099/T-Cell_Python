import sys
import time
import asyncio
import websockets
from websockets.connection import State
from pubsub import pub
import meshtastic
import meshtastic.serial_interface

WEBSOCKET_URI = "ws://localhost:8080"  # WebSocket 伺服器 URI
websocket = None

async def connect_websocket():
    global websocket
    try:
        websocket = await websockets.connect(WEBSOCKET_URI)
        print("Connected to WebSocket server")
    except Exception as e:
        print(f"Error connecting to WebSocket server: {e}")

async def send_message_to_websocket(message):
    global websocket
    if websocket and websocket.state == State.OPEN:  # 使用 websocket.state 檢查連線狀態
        try:
            await websocket.send(message)
            print(f"Sent message to WebSocket server: {message}")
        except Exception as e:
            print(f"Error sending message to WebSocket server: {e}")
    else:
        print("WebSocket connection is not open.")

def onReceive(packet, interface):
    """called when a packet arrives"""
    print(f"Received packet")
    if packet["decoded"]["portnum"] == "TEXT_MESSAGE_APP":
        message = packet['decoded']['payload'].decode('utf-8')
        print(f"Message: {message}")
        asyncio.run(send_message_to_websocket(message)) #send message to websocket

def onConnection(interface, topic=pub.AUTO_TOPIC):
    """called when we (re)connect to the radio"""
    # defaults to broadcast, specify a destination ID if you wish
    interface.sendText("hello mesh")

async def main():
    pub.subscribe(onReceive, "meshtastic.receive")
    pub.subscribe(onConnection, "meshtastic.connection.established")
    try:
        await connect_websocket()  # Connect to WebSocket server
        iface = meshtastic.serial_interface.SerialInterface()
        while True:
            await asyncio.sleep(1000)
        iface.close()
    except Exception as ex:
        print(f"Error: Could not connect to Serial {ex}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())