import network as net
import uasyncio as a
import json
from random import randint
from machine import Pin
import gc

from math import pi
from .omni import OmniSeeker

from async_websocket_client import AsyncWebsocketClient


# trying to read config --------------------------------------------------------
# if config file format is wrong, exception is raised and program will stop
print("Trying to load config...")

f = open("../config.json")
text = f.read()
f.close()
config = json.loads(text)
del text
# ------------------------------------------------------------------------------

print("Create WS instance...")
# create instance of websocket
ws = AsyncWebsocketClient(config['socket_delay_ms'])
print("Created ws.")

print("Create OmniSeeker instance...")
omni = OmniSeeker()
omni.addMotors(0, 2, 15, 13, 4, 16, 17, 26, 14, 27, 12, 5000)
print("Created omni.")


# this lock will be used for data interchange between loops --------------------
# better choice is to use uasynio.queue, but it is not documented yet
lock = a.Lock()
# this array stores messages from server
data_from_ws = []
# ------------------------------------------------------------------------------

# SSID - network name
# pwd - password
# attempts - how many time will we try to connect to WiFi in one cycle
# delay_in_msec - delay duration between attempts
async def wifi_connect(SSID: str, pwd: str, attempts: int = 3, delay_in_msec: int = 200) -> net.WLAN:
    wifi = net.WLAN(net.STA_IF)

    wifi.active(1)
    count = 1

    while not wifi.isconnected() and count <= attempts:
        print("WiFi connecting. Attempt {}.".format(count))
        if wifi.status() != net.STAT_CONNECTING:
            wifi.connect(SSID, pwd)
        await a.sleep_ms(delay_in_msec)
        count += 1

    if wifi.isconnected():
        print("ifconfig: {}".format(wifi.ifconfig()))
    else:
        print("Wifi not connected.")

    return wifi


# ------------------------------------------------------
# Main loop function: send data to server to keep connected.
# This code emulates main control cycle for controller.
async def blink_loop():
    global lock
    global data_from_ws
    global ws

    # Main "work" cycle. It should be awaitable as possible.
    while True:
        if ws is not None:
            if await ws.open():
                await ws.send('SOS!')

            # lock data archive
            await lock.acquire()
            if data_from_ws:
                data_from_ws = []
            lock.release()
            gc.collect()

        await a.sleep_ms(400)
# ------------------------------------------------------

# ------------------------------------------------------
# Task for read loop
async def read_loop():
    global config
    global lock
    global data_from_ws

    # may be, it
    wifi = await wifi_connect(config["wifi"]["SSID"], config["wifi"]["password"])
    while True:
        gc.collect()
        if not wifi.isconnected():
            wifi = await wifi_connect(config["wifi"]["SSID"], config["wifi"]["password"])
            if not wifi.isconnected():
                await a.sleep_ms(config["wifi"]["delay_in_msec"])
                continue
        try:
            print("Handshaking...")
            # connect to test socket server with random client number
            if not await ws.handshake("{}{}".format(config["server"], randint(1, 100))):
                raise Exception('Handshake error.')
            print("...handshaked.")

            mes_count = 0
            while await ws.open():
                data = await ws.recv()
                print("Data: " + str(data) + "; " + str(mes_count))
                data = data.split("=")
                if len(data) == 2 and data[0] == 'move':
                    move = int(data[1])
                    if move == 0:
                        omni.stop()
                    elif move == 3:
                        omni.moveRobot(0.75, 0, pi/2)
                    elif move == 4:
                        omni.moveRobot(-0.75, 0, pi/2)
                    elif move == 1:
                        omni.moveRobot(0.75, 0, pi)
                    elif move == 2:
                        omni.moveRobot(-0.75, 0, pi)
                    elif move == 5:
                        omni.moveRobot(0, pi/8, 0)
                    elif move == 6:
                        omni.moveRobot(0, -pi/8, 0)

                    print(f"Move command received: {move}")
                else:
                    print("Invalid message format")
                # close socket for every 10 messages (even ping/pong)
                if mes_count == 10:
                    await ws.close()
                    print("ws is open: " + str(await ws.open()))
                mes_count += 1

                if data is not None:
                    await lock.acquire()
                    data_from_ws.append(data)
                    lock.release()

                await a.sleep_ms(50)
        except Exception as ex:
            print("Exception: {}".format(ex))
            await a.sleep(1)
# ------------------------------------------------------