#!/usr/bin/env python3
"""
@summary: how to send a signed transaction

@version: v03 (6/March/2020)
@since:   6/March/2020
@author:  https://github.com/drandreaskrueger
@see:     https://github.com/drandreaskrueger/chainhammer-substrate for updates
"""

import time, sys
from threading import Thread
from queue import Queue
from subprocess import run, PIPE
import substrateinterface

URL = "http://127.0.0.1:9800" # "http://127.0.0.1:9933"

ALICE_ADDRESS = '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY'
X_ADDRESS     = '5Gdc7hM6WqVjd23YaJR1bUWJheCo4ymrcKAFc35FpfbeH68f'
ALICE_PUBKEY = '0xd43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d'
X_PUBKEY     = '0xca08b4e0f53054628a43912ffbb6d00a0362921ba9781932297edc037d197a5d'
BOB_ADDRESS = '5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty'

SIGN_CLI = 'docker run jacogr/polkadot-js-tools signer sign --type {type} --account {account} --seed "{seed}" {payload}'
# docker run jacogr/polkadot-js-tools signer sign --type sr25519 --account //Alice --seed "//Alice" 0xa8040400ffca08b4e0f53054628a43912ffbb6d00a0362921ba9781932297edc037d197a5d070010a5d4e8

def get_balance(substrate, address, block_hash=None):
    balance = substrate.get_runtime_state(module='Balances',
                                          storage_function='FreeBalance',
                                          params=[address],
                                          block_hash=block_hash
                                          ).get('result') 
    dot = float(balance) / 10**12 if balance else 0
    print("Current balance: {} DOT on address {}".format(*(dot, address)))
    return dot
    
class SubkeyError(Exception): pass 

def os_command(command=['ls', '-la']):
    """
    execute a CLI command, and return the output
    """
    p = run(command, stdout=PIPE, encoding='ascii')
    # p = run(command, encoding='ascii')
    if p.returncode != 0:
        raise SubkeyError(p.returncode)
    return p.stdout


def sign(payload, signer="//Alice", seed="//Alice", ifprint=False):
    """
    docker run jacogr/polkadot-js-tools signer sign --type sr25519 --account //Alice --seed "//Alice" payload
    """
    args =  {"type": "sr25519",
             "account" : signer,
             "seed" : seed,
             "payload" : payload}
    command = SIGN_CLI.format(**args)
    if ifprint:
        print (command)
    signed = os_command(command.split(" ")).replace("Signature: ", "").strip() # removal of newline character! 
    return signed


def test_sign(container, payload="0xa8040400ff8eaf04151687736326c9fea17e25fc5287613693c912909cb226aa4794f26a48070010a5d4e8", ifprint=True):
    signed = sign(payload)
    if ifprint:
        print (signed)
    container.append(signed)
    

def sign_many_threaded(N=5, payload="0xa8040400ff8eaf04151687736326c9fea17e25fc5287613693c912909cb226aa4794f26a48070010a5d4e8"):
    threads = []
    signed = [] # container to keep all signed payloads
    for i in range(N):
        t = Thread(target = test_sign,
                   args   = (signed, payload))
        threads.append(t)
        print (".", end="")
    print ("%d transaction threads created." % len(threads))

    for t in threads:
        t.start()
        print (".", end="")
        sys.stdout.flush()
    print ("all threads started.")
    
    for t in threads: 
        t.join()
    print ("all threads ended.")
    
    print ("results:")
    print (signed)
    

def sign_many_threaded_queue(numTx=20, num_worker_threads=4, payload="0xa8040400ff8eaf04151687736326c9fea17e25fc5287613693c912909cb226aa4794f26a48070010a5d4e8"):
    
    line = "sign %d transactions, via multi-threading queue with %d workers:\n"
    print (line % (numTx, num_worker_threads))

    q = Queue()
    txs = [] # container to keep all transaction hashes
    
    def worker():
        while True:
            item = q.get()
            test_sign(txs, item)
            print ("T", end=""); sys.stdout.flush()
            q.task_done()

    for i in range(num_worker_threads):
         t = Thread(target=worker)
         t.daemon = True
         t.start()
         print ("W", end=""); sys.stdout.flush()
    print ("\n%d worker threads created." % num_worker_threads)

    for i in range(numTx):
        q.put (payload)
        print ("I", end=""); sys.stdout.flush()
    print ("\n%d items queued." % numTx)

    q.join()
    print ("\nall items - done.")
    
    return txs


def balance_transfer(dest, value, signer):
    payload = substrate.compose_call(call_module='Balances',
                                     call_function='transfer',
                                     call_params={'dest': dest,
                                                  'value': value})
    print ("payload:", payload)
    signed = sign(payload, signer)
    print ("signed: >>>%s<<<" % signed)
    # result = substrate.rpc_request(method="author_submitAndWatchExtrinsic", params=[signed])
    result = substrate.rpc_request(method="author_submitExtrinsic", params=[signed])
    print (result)
    
    

if __name__ == '__main__':
    # print(os_command())
    # test_sign(); exit()
    
    timed = time.time()
    # sign_many_threaded_queue(numTx=20, num_worker_threads=10);
    sign_many_threaded(N=50) 
    timed = time.time() - timed
    print ("that took %.3f seconds" % timed)
    exit()
    
    substrate = substrateinterface.SubstrateInterface(url=URL) # , address_type=42)
    
    dot = get_balance(substrate, address=BOB_ADDRESS)
    print ()
    
    balance_transfer(dest=BOB_ADDRESS, value=1000000000000, signer='//Alice')
    time.sleep(10)
    
    print ()
    dot = get_balance(substrate, address=BOB_ADDRESS)
    