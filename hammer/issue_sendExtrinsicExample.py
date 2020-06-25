#!/usr/bin/env python3
"""
@summary: Send extrinsic - how to? Example doesn't work yet for substrate & node-template.
          For reporting in https://github.com/polkascan/py-substrate-interface/issues/14
          Output RESULTS = see bottom of this file

@version: v05 (25/June/2020)
@since:   10/June/2020
@author:  https://github.com/drandreaskrueger
@see:     https://github.com/drandreaskrueger/chainhammer-substrate for updates

@attention: versions:
                pip freeze | grep "scalecodec\|substrate"
                    scalecodec==0.9.55
                    substrate-interface==0.9.14

@quickstart:
          python3 -m venv env
          source env/bin/activate
          pip3 install --upgrade pip
          pip3 install substrate-interface
          wget https://gist.githubusercontent.com/drandreaskrueger/053bfe0c8ddfaeeb50134a977708f999/raw -O send_extrinsic.py

          node-template --dev
          python3 send_extrinsic.py 
"""

from substrateinterface import SubstrateInterface, Keypair, SubstrateRequestException
from pprint import pformat, pprint

# URL =   "ws://127.0.0.1:9944"
URL = "http://127.0.0.1:9933"

def compose_sign_and_send_extrinsic(substrate):
    """
    see https://github.com/polkascan/py-substrate-interface/issues/14
    """
    keypair = Keypair.create_from_mnemonic('episode together nose spoon dose oil faculty zoo ankle evoke admit walnut')
    print ("sending from:", keypair.ss58_address)
    BOB_ADDRESS = '5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty'
    call = substrate.compose_call(
        call_module='Balances', call_function='transfer',
        call_params={
            'dest': BOB_ADDRESS,
            'value': 1 * 10**12})
    try:
        extrinsic = substrate.create_signed_extrinsic(call=call, keypair=keypair)
        # result = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True) # works only with ws not http
        result = substrate.submit_extrinsic(extrinsic) # works with both http AND ws
        print("Extrinsic '{}' sent and included in block '{}'".format(result['extrinsic_hash'], result.get('block_hash', None)))
        
    except (SubstrateRequestException, ValueError) as e:
        print("Failed to send: {} with args:".format(type(e)))
        print("{}".format(pformat(e.args[0])))


custom_type_registry_1 = {  "runtime_id": 1,
                              "types": {
                                "Address": "AccountIdAddress",
                                "ExtrinsicPayloadValue": {
                                  "type": "struct",
                                  "type_mapping": [
                                    ["call", "CallBytes"],
                                    ["era", "Era"],
                                    ["nonce", "Compact<Index>"],
                                    ["tip", "Compact<Balance>"],
                                    ["specVersion", "u32"],
                                    ["genesisHash", "Hash"],
                                    ["blockHash", "Hash"]
                                  ]
                                }
                              },
                              "versioning": [
                              ]
                            }

custom_type_registry_2 = {"please help" : "thanks."}


def with_custom_type_registry(custom_type_registry):

    substrate = SubstrateInterface(url=URL,
                                   address_type=42, 
                                   type_registry_preset='default', 
                                   type_registry=custom_type_registry)
    return substrate


def print_getRuntimeVersion(substrate):
    print ("get_version() = %s" % substrate.get_version())
    grv=substrate.rpc_request(method="chain_getRuntimeVersion", params=[])
    print ("chain_getRuntimeVersion()['result']:")
    pprint(grv['result'])
           

if __name__ == '__main__':
    
    substrate = SubstrateInterface( url=URL )
    print_getRuntimeVersion(substrate)
    
    print ("\nDefault SubstrateInterface:")
    compose_sign_and_send_extrinsic(substrate)
    
    print ("\nSubstrateInterface with custom type registry:")
    substrate=with_custom_type_registry(custom_type_registry_1)
    compose_sign_and_send_extrinsic(substrate)

    
"""
######################################
# RESULTS:
#        first:  node-template --dev
#        second: substrate --dev
######################################

#########################
### node-template --dev
#########################

get_version() = 2.0.0-rc3-f5acce1-x86_64-linux-gnu
chain_getRuntimeVersion()['result']:
{'apis': [['0xdf6acb689907609b', 3],
          ['0x37e397fc7c91f5e4', 1],
          ['0x40fe3ad401f8959a', 4],
          ['0xd2bc9897eed08f15', 2],
          ['0xf78b278be53f454c', 2],
          ['0xdd718d5cc53262d4', 1],
          ['0xab3c0572291feb8b', 1],
          ['0xed99c5acb25eedf5', 2]],
 'authoringVersion': 1,
 'implName': 'node-template',
 'implVersion': 1,
 'specName': 'node-template',
 'specVersion': 1,
 'transactionVersion': 1}

Default SubstrateInterface:
sending from: 5HmubXCdmtEvKmvqjJ7fXkxhPXcg6JTS62kMMphqxpEE6zcG
Failed to send: <class 'substrateinterface.exceptions.SubstrateRequestException'> with args:
{'code': 1002,
 'data': 'RuntimeApi("Execution(ApiError(\\"Could not convert parameter `tx` '
         'between node and runtime: No such variant in enum '
         'MultiSignature\\"))")',
 'message': 'Verification Error: Execution(ApiError("Could not convert '
            'parameter `tx` between node and runtime: No such variant in enum '
            'MultiSignature"))'}

SubstrateInterface with custom type registry:
sending from: 5HmubXCdmtEvKmvqjJ7fXkxhPXcg6JTS62kMMphqxpEE6zcG
Failed to send: <class 'substrateinterface.exceptions.SubstrateRequestException'> with args:
{'code': 1010, 'data': 'BadProof', 'message': 'Invalid Transaction'}


#####################
### substrate --dev
#####################

get_version() = 2.0.0-rc3-34695a856-x86_64-linux-gnu
chain_getRuntimeVersion()['result']:
{'apis': [['0xdf6acb689907609b', 3],
          ['0x37e397fc7c91f5e4', 1],
          ['0x40fe3ad401f8959a', 4],
          ['0xd2bc9897eed08f15', 2],
          ['0xf78b278be53f454c', 2],
          ['0xed99c5acb25eedf5', 2],
          ['0xcbca25e39f142387', 2],
          ['0x687ad44ad37f03c2', 1],
          ['0xbc9d89904f5b923f', 1],
          ['0x68b66ba122c93fa7', 1],
          ['0x37c8bb1350a9a2a8', 1],
          ['0xab3c0572291feb8b', 1]],
 'authoringVersion': 10,
 'implName': 'substrate-node',
 'implVersion': 2,
 'specName': 'node',
 'specVersion': 251,
 'transactionVersion': 1}

Default SubstrateInterface:
sending from: 5HmubXCdmtEvKmvqjJ7fXkxhPXcg6JTS62kMMphqxpEE6zcG
Failed to send: <class 'substrateinterface.exceptions.SubstrateRequestException'> with args:
{'code': 1010, 'data': 'Payment', 'message': 'Invalid Transaction'}

SubstrateInterface with custom type registry:
sending from: 5HmubXCdmtEvKmvqjJ7fXkxhPXcg6JTS62kMMphqxpEE6zcG
Failed to send: <class 'substrateinterface.exceptions.SubstrateRequestException'> with args:
{'code': 1002,
 'data': 'RuntimeApi("Execution(ApiError(\\"Could not convert parameter `tx` '
         'between node and runtime: No such variant in enum '
         'MultiSignature\\"))")',
 'message': 'Verification Error: Execution(ApiError("Could not convert '
            'parameter `tx` between node and runtime: No such variant in enum '
            'MultiSignature"))'}

"""
