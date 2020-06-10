#!/usr/bin/env python3
"""
@summary: how to send a signed transaction

@version: v03 (6/March/2020)
@since:   6/March/2020
@author:  https://github.com/drandreaskrueger
@see:     https://github.com/drandreaskrueger/chainhammer-substrate for updates
"""

import time, sys
from pprint import pformat
from threading import Thread
from queue import Queue
from subprocess import run, PIPE
import substrateinterface

URL = "http://127.0.0.1:9800" 
URL = "http://127.0.0.1:9933"

ALICE_ADDRESS = '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY'
X_ADDRESS     = '5Gdc7hM6WqVjd23YaJR1bUWJheCo4ymrcKAFc35FpfbeH68f'
ALICE_PUBKEY = '0xd43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d'
X_PUBKEY     = '0xca08b4e0f53054628a43912ffbb6d00a0362921ba9781932297edc037d197a5d'
BOB_ADDRESS = '5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty'

# see README.md:
# https://github.com/polkascan/py-substrate-interface#create-and-send-signed-extrinsics

from substrateinterface import SubstrateInterface, SubstrateRequestException, Keypair

def keypair_printer(keypair):
    print ([key for key in dir(keypair) if not key.startswith("__")])
    for member in "address_type mnemonic private_key public_key ss58_address".split(" "):
        print ("keypair.%s=%s" % (member, getattr(keypair,member)))

def example_send_transaction():
    """
    similar to what is given in polkascan github README.md
    issue reported back to polkascan
    https://github.com/polkascan/py-substrate-interface/issues/14
    """

    # substrate = SubstrateInterface( url="ws://127.0.0.1:9944", address_type=42, type_registry_preset='kusama' )
    # substrate = SubstrateInterface( url="ws://127.0.0.1:9944", address_type=2)
    substrate = SubstrateInterface( url="ws://127.0.0.1:9944" )
    
    keypair = Keypair.create_from_mnemonic('episode together nose spoon dose oil faculty zoo ankle evoke admit walnut')
    # keypair = Keypair.create_from_private_key('//Alice')
    # keypair = Keypair.create_from_mnemonic('//Alice')
    
    keypair_printer(keypair)
    print ("sending from:", keypair.ss58_address)
    
    BOB_ADDRESS = '5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty'
    
    call = substrate.compose_call(
        call_module='Balances',
        call_function='transfer',
        call_params={
            'dest': BOB_ADDRESS,
            'value': 1 * 10**12
        }
    )
    extrinsic = substrate.create_signed_extrinsic(call=call, keypair=keypair)
    try:
        result = substrate.send_extrinsic(extrinsic, wait_for_inclusion=True)
        print("Extrinsic '{}' sent and included in block '{}'".format(result['extrinsic_hash'], result['block_hash']))
    except SubstrateRequestException as e:
        print("Failed to send: {} with args:".format(type(e)))
        print("{}".format(pformat(e.args[0])))
    

def keypair_example():
    mnemonic = Keypair.generate_mnemonic()
    keypair = Keypair.create_from_mnemonic(mnemonic)
    signature = keypair.sign("Test123")
    if keypair.verify("Test123", signature):
        print('Verified')
        

    
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
    
    
def benchmark_signing_workaround(N=50):
    """
    100 transactions took 77.0 seconds, i.e. 0.770 per transaction.
    --> max bandwidth is 1.3 TPS
    """
    timed = time.time()
    # sign_many_threaded_queue(numTx=20, num_worker_threads=10);
    sign_many_threaded(N=N) 
    timed = time.time() - timed
    print ("that took %.1f seconds, i.e. %.3f per transaction" % (timed, timed/N))
    

if __name__ == '__main__':
    
    example_send_transaction(); exit()
    
    # print(os_command())
    # test_sign(); exit()
    
    benchmark_signing_workaround(5); exit()
    
    substrate = substrateinterface.SubstrateInterface(url=URL) # , address_type=42)
    
    dot = get_balance(substrate, address=BOB_ADDRESS)
    print ()
    
    balance_transfer(dest=BOB_ADDRESS, value=1000000000000, signer='//Alice')
    time.sleep(10)
    
    print ()
    dot = get_balance(substrate, address=BOB_ADDRESS)
    