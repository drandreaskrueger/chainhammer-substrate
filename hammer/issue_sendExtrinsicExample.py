#!/usr/bin/env python3
"""
@summary: send extrinsic - how to?
          found an error, reported in https://github.com/polkascan/py-substrate-interface/issues/14
          output results = see bottom of this file

@version: v03 (18/June/2020)
@since:   10/June/2020
@author:  https://github.com/drandreaskrueger
@see:     https://github.com/drandreaskrueger/chainhammer-substrate for updates

@attention: versions!
            pip uninstall scalecodec substrateinterface substrate-interface;
            pip install scalecodec substrate-interface
            pip freeze | grep "scalecodec\|substrate"

scalecodec==0.9.54
substrate-interface==0.9.14
"""

from substrateinterface import SubstrateInterface, Keypair, SubstrateRequestException
from pprint import pformat, pprint

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
        result = substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)
        print("Extrinsic '{}' sent and included in block '{}'".format(result['extrinsic_hash'], result['block_hash']))
    except (SubstrateRequestException, ValueError) as e:
        print("Failed to send: {} with args:".format(type(e)))
        print("{}".format(pformat(e.args[0])))


def with_custom_type_registry():
    custom_type_registry = {
                            "runtime_id": 1,
                            "types": {
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
                            "versioning": []
                            }
    substrate = SubstrateInterface(url="ws://127.0.0.1:9944",
                                   address_type=42, 
                                   type_registry_preset='default', 
                                   type_registry=custom_type_registry)
    return substrate


def print_getRuntimeVersion(substrate):
    print ("get_version() = %s" % substrate.get_version())
    # AttributeError: 'SubstrateInterface' object has no attribute 'chain_getRuntimeVersion'
    # grv = substrate.chain_getRuntimeVersion()
    grv=substrate.rpc_request(method="chain_getRuntimeVersion", params=[])
    print ("chain_getRuntimeVersion():")
    pprint(grv)
           

if __name__ == '__main__':
    
    substrate = SubstrateInterface( url="ws://127.0.0.1:9944" )
    print_getRuntimeVersion(substrate)
    
    print ("\nDefault SubstrateInterface:")
    compose_sign_and_send_extrinsic(substrate)
    
    print ("\nSubstrateInterface with custom type registry:")
    substrate=with_custom_type_registry()
    compose_sign_and_send_extrinsic(substrate)

    
"""
# RESULT:
# first:  node-template --dev
# second: substrate --dev

### node-template --dev

get_version() = 2.0.0-rc3-f5acce1-x86_64-linux-gnu
chain_getRuntimeVersion():
{'id': 1,
 'jsonrpc': '2.0',
 'result': {'apis': [['0xdf6acb689907609b', 3],
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
            'transactionVersion': 1}}

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
{'code': 1002,
 'data': 'RuntimeApi("Execution(ApiError(\\"Could not convert parameter `tx` '
         'between node and runtime: No such variant in enum '
         'MultiSignature\\"))")',
 'message': 'Verification Error: Execution(ApiError("Could not convert '
            'parameter `tx` between node and runtime: No such variant in enum '
            'MultiSignature"))'}


### substrate --dev

get_version() = 2.0.0-rc2-45b9f0a9c-x86_64-linux-gnu
chain_getRuntimeVersion():
{'id': 1,
 'jsonrpc': '2.0',
 'result': {'apis': [['0xdf6acb689907609b', 3],
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
            'implVersion': 0,
            'specName': 'node',
            'specVersion': 251,
            'transactionVersion': 1}}

Default SubstrateInterface:
sending from: 5HmubXCdmtEvKmvqjJ7fXkxhPXcg6JTS62kMMphqxpEE6zcG
Failed to send: <class 'substrateinterface.exceptions.SubstrateRequestException'> with args:
{'code': 1010, 'data': 'Payment', 'message': 'Invalid Transaction'}

SubstrateInterface with custom type registry:
sending from: 5HmubXCdmtEvKmvqjJ7fXkxhPXcg6JTS62kMMphqxpEE6zcG
Failed to send: <class 'substrateinterface.exceptions.SubstrateRequestException'> with args:
{'code': 1010, 'data': 'BadProof', 'message': 'Invalid Transaction'}

"""