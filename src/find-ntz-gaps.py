#!/usr/bin/env python3
# @author dimxy, Komodo
# find-ntz-gap - finds blocks not included in any notarisation MoM
# installation:
# you'll need slickrpc py lib to run this
# usage:
# python3 find-ntz-gap.py <path-to-node-config>

from lib import rpclib, tuilib
import os
import time
import json
import argparse
from slickrpc.exc import RpcException
import configparser



# create localhost rpc connection to a chain node by reading config file
def get_chain_rpc(config) :

    rpc = None
    with open(config) as file:
        lines = file.readlines()
    rpcuser = ''
    rpcpassword = ''
    rpcport = 0
    for l in lines :
        t = l.split('=')
        if len(t) == 2 : 
            if t[0] == 'rpcuser' :
                rpcuser = t[1].strip()
            elif t[0] == 'rpcpassword' :
                rpcpassword = t[1].strip()
            elif t[0] == 'rpcport' :
                rpcport = int(t[1])

    print('rpcuser', rpcuser, 'rpcpassword', rpcpassword, 'rpcport', rpcport)
    rpc = rpclib.rpc_connect(rpcuser, rpcpassword, int(rpcport))
    rpc.getinfo() # try connect
    print('rpc connected')
    return rpc


# finds gaps
def run_find_ntz_gaps(config) :

    rpc = get_chain_rpc(config)
    getinfo = rpc.getinfo()
    # print('getinfo', getinfo)
    if getinfo['blocks'] is None :
      print('cannot connect to chain')
      return

    tip_ht = getinfo['blocks']
    ntz_first = 0
    ntz_last = 0
    ht = 1

    while(ht <= tip_ht) :
      ntz_data = rpc.height_MoM(str(ht))
      # print('ntz_data', ntz_data )
      if ntz_data.get('error') is not None :
        ht = ht + 1
        # print('adding ht=ht+1, continue')
        continue

      if ntz_data.get('notarized_height') is None :
        print('could not get notarized data (notarized_height empty)')
        break

      # print('found ntz:', 'notarized_height', ntz_last, ntz_data['notarized_height'] - ntz_data['depth'] + 1, ntz_data['notarized_height'], 'depth', ntz_data['depth'])

      if ntz_first == 0 :
        ntz_first = int(ntz_data['notarized_height'])

      ntz_ht = int(ntz_data['notarized_height'])
      depth = int(ntz_data['depth'])
      
      if ntz_last > 0 :
        if ntz_ht - depth > ntz_last :   # actually current 'notarised height' minus 'depth' must point to the 'last notarised height'
          print('found gap:', ntz_last+1, ntz_ht - depth)

      ntz_last = ntz_ht
      ht = ntz_ht + 1

    if ntz_first == 0 :
      print('could not get notarized data (first ntz not found)')
    else :
      print('ntz_start_ht', ntz_first, 'ntz_last_ht', ntz_last, 'tip_ht', tip_ht)

if __name__ == "__main__":
    print("Finds notarisation gaps in a chain. Use path to your node config file as the param to run this tool")
    parser = argparse.ArgumentParser()
    parser.add_argument("configfile", help='path to node config file')
    args = parser.parse_args()
    print(args)

    run_find_ntz_gaps(args.configfile)

