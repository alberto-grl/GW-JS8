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


if(exists("TelegramAPI.json")):
    print('Using API values from TelegramAPI.json')
    print('Insert you own values from my telegram.org!')
    f=open("TelegramAPI.json")
    TelegramAPI=json.load(f)
    f.close()
    api_id = TelegramAPI['api_id']
    api_hash = TelegramAPI['api_hash']
    group_id = TelegramAPI['group_id']
else:
    print('TelegramAPI.json not found! Insert you own values from my telegram.org!')
    exit()
    
TClient = TelegramClient('anon', api_id, api_hash)
loop = asyncio.get_event_loop()
last_hb = 0
RxFilter = ''

async def js8handler():
    global RxFilter
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

    # Load spots.json for some historical context, unless the file is
    # missing, or the user asks not to.
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
                    JS8RXString = 'JS8 RX: ' + str(rx['params']['OFFSET']) + ' | ' + str(rx['params']['SNR'])  + ' | ' + rx['params']['TEXT']
                    if RxFilter in rx['params']['TEXT'] or RxFilter == '':
                        await TClient.send_message(group_id,JS8RXString)
                    
                    JS8RxTokens = rx['params']['TEXT'].split()
                    print("JS8RxTokens[2] :   ",JS8RxTokens[2])
                    if JS8RxTokens[2] == '#HKU' and rx['params']['TO'] == 'I4NZX' :
                        print("P DETECTED IN DIRECTED:   ",rx['params']['TEXT'][0:3])
                        send_message(rx['params']['FROM'] + ' ' + 'Static fills the air Tuning in to distant waves Whispers from afar Melodies unfold Radio s rhythmic embrace Echoes linger on Through the crackling hiss Voices carry on the wind Unseen connections')
                        send_message(rx['params']['FROM'] + ' ' + 'TEST2')
                        print("#HKU DETECTED IN :   ",rx['params']['TEXT'])
                       
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
    global last_hb
    global RxFilter
    TgramTokens = event.message.to_dict()['message'].split()

    if len(TgramTokens) > 0: 

        if (TgramTokens[0] == '/hb' and len(TgramTokens) == 1): 
            if (time.time() > last_hb + 300):
                grid=get_grid()
                send_heartbeat(grid)
                last_hb = time.time()
                await TClient.send_message(group_id, 'JS8 Heartbeat sent.')
            else:
                await TClient.send_message(group_id, 'Max one HB every 5 min. Wait')

        elif (TgramTokens[0] == '/offset' and len(TgramTokens) == 2):   
            set_freq(7078000, int(TgramTokens[1]))
            print("change offset")
            await TClient.send_message(group_id, 'Offset changed.')

        elif (TgramTokens[0] == '/sgrid' and len(TgramTokens) == 2):   
            send_aprs_grid(TgramTokens[1])
            print("Grid sent")
            await TClient.send_message(group_id, 'Grid sent.')

        elif (TgramTokens[0] == '/tx'):   
            send_message( event.message.to_dict()['message'][4:])
            await TClient.send_message(group_id, 'MSG sent.')

        elif (TgramTokens[0] == '/qsnr' and len(TgramTokens) == 2):   
            query_snr( TgramTokens[1])
            await TClient.send_message(group_id, 'Query SNR sent.')

        elif (TgramTokens[0] == '/semail' and len(TgramTokens) >= 2):
            EmailMessage = event.message.to_dict()['message'].split(" ", 2)
            send_email( TgramTokens[1], EmailMessage[2])
            await TClient.send_message(group_id, 'Email sent')
            
        elif (TgramTokens[0] == '/srxfilt'):
            if (len(TgramTokens) == 2):
                RxFilter = TgramTokens[1]
                await TClient.send_message(group_id, 'RX filter set')
            elif(len(TgramTokens) == 1):
                RxFilter = ''
                await TClient.send_message(group_id, 'RX filter reset')
      
        elif (TgramTokens[0] == '/qinfo' and len(TgramTokens) == 2):   
            query_info( TgramTokens[1])
            await TClient.send_message(group_id, 'Query info sent.')
async def main():
   

    await TClient.start()
    print('Starting main loop')

    await asyncio.gather(js8handler(), TClient.run_until_disconnected())
#    await asyncio.gather(f3('f3 test'), js8handler(), TClient.run_until_disconnected())

    

# Main program.
if(__name__ == '__main__'):   
    TClient.loop.run_until_complete(main())
