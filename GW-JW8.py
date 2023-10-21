#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import time
import json
import argparse
from os.path import exists
from js8net import *

import asyncio
from telethon.sync import TelegramClient
from telethon import TelegramClient, events, utils

# Remember to use your own values from my.telegram.org!
api_id = 21367587
api_hash = 'f4f258689a89677bc7455dec63ddf878'
TClient = TelegramClient('anon', api_id, api_hash)
loop = asyncio.get_event_loop()

async def js8handler():
    parser=argparse.ArgumentParser(description="Example of using js8net.py")
    parser.add_argument("--js8_host",default=False,help="IP/DNS of JS8Call server (default localhost, env: JS8HOST)")
    parser.add_argument("--js8_port",default=False,help="TCP port of JS8Call server (default 2442, env: JS8PORT)")
    parser.add_argument("--clean",default=False,action="store_true",help="Start with clean spots (ie, don't load spots.json)")
    parser.add_argument("--env",default=False,action="store_true",help="Use environment variables (cli options override)")
    parser.add_argument("--listen",default=False,action="store_true",help="Listen only - do not write files")
    parser.add_argument("--verbose",default=False,action="store_true",help="Lots of status messages")
    args=parser.parse_args()

    # Load spots.json for some historical context, unless the file is
    # missing, or the user asks not to.
    if(exists("spots.json") and not(args.clean)):
        with spots_lock:
            f=open("spots.json")
            spots=json.load(f)
            f.close()

    js8host=False
    js8port=False

    # If the user specified a command-line flag, that takes
    # priority. If they also specified --env, any parameters they did
    # not specify explicit flags for, try to grab from the
    # environment.
    if(args.js8_host):
        js8host=args.js8_host
    elif(os.environ.get("JS8HOST") and args.env):
        js8host=os.environ.get("JS8HOST")
    else:
        js8host="localhost"

    if(args.js8_port):
        js8port=args.js8_port
    elif(os.environ.get("JS8PORT") and args.env):
        js8port=int(os.environ.get("JS8PORT"))
    else:
        js8port=2442

    if(args.verbose):
        print("Connecting to JS8Call...")
    start_net(js8host,js8port)
    if(args.verbose):
        print("Connected.")
    """
    print("Call: ",get_callsign())
    print("Grid: ",get_grid())
    print("Info: ",get_info())
    print("Freq: ",get_freq())
    print("Speed: ",get_speed())
    print("Freq: ",set_freq(7078000,2000))
    """
    get_band_activity()
    last=time.time()

    while(True):
        await asyncio.sleep(0.1)
        if(not(rx_queue.empty())):
            with rx_lock:
                rx=rx_queue.get()
                if(not(args.listen)):
                    f=open("rx.json","a")
                    f.write(json.dumps(rx))
                    f.write("\n")
                    f.close()
                    if(time.time()>=last+300):
                        last=time.time()
                        f=open("spots.json","w")
                        f.write(json.dumps(spots))
                        f.write("\n")
                    f.close()
                if(rx['type']=="RX.DIRECTED"):
                    print("FROM:   ",rx['params']['FROM'])
                    print("TO:     ",rx['params']['TO'])
                    if('rxerror' in list(rx.keys())):
                        print("RX ERR: ",rx['rxerror'])
                    print("CMD:    ",rx['params']['CMD'])
                    print("GRID:   ",rx['params']['GRID'])
                    print("SPEED:  ",rx['params']['SPEED'])
                    print("SNR:    ",rx['params']['SNR'])
                    print("TDRIFT: ",str(int(rx['params']['TDRIFT']*1000)))
                    print("DIAL:   ",rx['params']['DIAL'])
                    print("OFFSET: ",rx['params']['OFFSET'])
#                    print("FREQ:   ",rx['params']['FREQ'])
                    print("EXTRA:  ",rx['params']['EXTRA'])
                    print("TEXT:   ",rx['params']['TEXT'])
#                    print("VALUE: ",rx['value'])
                    print()
#                    print(json.dumps(rx,indent=2,sort_keys=True))
#                    print()
                    JS8RXString = 'JS8 RX: ' + rx['params']['FROM'] + ' TO ' + rx['params']['TO'] + ' SNR ' + str(rx['params']['SNR']) + ' - ' + rx['params']['TEXT']
                    await TClient.send_message('testjs8',JS8RXString)
"""             print("JS8 Received")
                print("FROM:   ",rx['params']['FROM'])
                print("TO:     ",rx['params']['TO'])
                print("SNR:    ",rx['params']['SNR'])
                print("TEXT:   ",rx['params']['TEXT'])
"""


async def f3(name):
    print(f'{name} started')
    while(True):
        await asyncio.sleep(1)
        print(f'{name} f3')

@TClient.on(events.NewMessage())
async def my_event_handler(event):
    print(event.message.to_dict()['message'])
    if (event.message.to_dict()['message'] == '/hb'):
        grid=get_grid()
        send_heartbeat(grid)
        await TClient.send_message('testjs8', 'JS8 Heartbeat sent.')

    TgramTokens = event.message.to_dict()['message'].split()
    if (TgramTokens[0] == '/offset'):   
        set_freq(7078000, int(TgramTokens[1]))
        await TClient.send_message('testjs8', 'Offset changed.')
#    send_message('abc')


async def main():
   

    await TClient.start()
    print('Starting main loop')
    await asyncio.gather(js8handler(), TClient.run_until_disconnected())
#    await asyncio.gather(f3('f3 test'), js8handler(), TClient.run_until_disconnected())

    

# Main program.
if(__name__ == '__main__'):   
    TClient.loop.run_until_complete(main())
