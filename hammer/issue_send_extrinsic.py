#!/usr/bin/env python3
"""
@summary: how to send a signed transaction

@version: v03 (6/March/2020)
@since:   6/March/2020
@author:  https://github.com/drandreaskrueger
@see:     https://github.com/drandreaskrueger/chainhammer-substrate for updates
"""

import time
from subprocess import run, PIPE
import substrateinterface

URL = "http://127.0.0.1:9800" # "http://127.0.0.1:9933"

ALICE_ADDRESS = '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY'
X_ADDRESS     = '5Gdc7hM6WqVjd23YaJR1bUWJheCo4ymrcKAFc35FpfbeH68f'
ALICE_PUBKEY = '0xd43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d'
X_PUBKEY     = '0xca08b4e0f53054628a43912ffbb6d00a0362921ba9781932297edc037d197a5d'

SIGN_CLI = 'docker run jacogr/polkadot-js-tools signer sign --type {type} --account {account} --seed "{seed}"'
# SIGN_CLI = 'docker run jacogr/polkadot-js-tools signer sign --type {type} --account {account} --seed "{seed}" {payload}'

def get_balance(substrate, address, block_hash=None):
    balance = substrate.get_runtime_state(module='Balances',
                                          storage_function='FreeBalance',
                                          params=[address],
                                          block_hash=block_hash
                                          ).get('result') 
    dot = float(balance) / 10**12 if balance else 0
    print("Current balance: {} DOT".format(dot))
    return dot
    
class SubkeyError(Exception): pass 

def os_command_with_pipe(command=['grep', 'f'], 
                         data='one\ntwo\nthree\nfour\nfive\nsix\n'):
    """
    https://stackoverflow.com/a/165662
    """
    p = run(command, stdout=PIPE, input=data, encoding='ascii')
    if p.returncode != 0:
        raise SubkeyError(p.returncode)
    return p.stdout


def sign(payload, signer="//Alice", seed="//Alice"):
    """
    docker run jacogr/polkadot-js-tools signer sign --type sr25519 --account //Alice --seed "//Alice" payload
    """
    args =  {"type": "sr25519",
             "account" : signer,
             "seed" : seed}
    command = SIGN_CLI.format(**args).split(" ")
    # print (command); exit()
    signed = os_command_with_pipe(command, payload).replace("Signature: ", "")
    return signed


def test_sign(payload="0xa8040400ff8eaf04151687736326c9fea17e25fc5287613693c912909cb226aa4794f26a48070010a5d4e8"):
    signed = sign(payload)
    print (signed)
    

def balance_transfer(dest, value, signer):
    payload = substrate.compose_call(call_module='Balances',
                                     call_function='transfer',
                                     call_params={'dest': dest,
                                                  'value': value})
    print ("payload:", payload)
    signed = sign(payload, signer)
    print ("signed:", signed)
    # result = substrate.rpc_request(method="author_submitAndWatchExtrinsic", params=[signed])
    result = substrate.rpc_request(method="author_submitExtrinsic", params=[signed])
    print (result)
    
    

if __name__ == '__main__':
    # test_sign(); exit()
    
    substrate = substrateinterface.SubstrateInterface(url=URL) # , address_type=42)
    
    dot = get_balance(substrate, address=X_ADDRESS)
    balance_transfer(dest=X_PUBKEY, value=1000000000000, signer='//Alice')
    time.sleep(10)
    dot = get_balance(substrate, address=X_ADDRESS)
    