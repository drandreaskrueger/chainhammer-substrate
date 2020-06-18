#!/usr/bin/env python3
"""
@summary: found an error, reported in https://github.com/polkascan/py-substrate-interface/issues/14

@version: v02 (17/June/2020)
@since:   10/June/2020
@author:  https://github.com/drandreaskrueger
@see:     https://github.com/drandreaskrueger/chainhammer-substrate for updates
"""

def errorenous():
    """
    answered here https://github.com/polkascan/py-substrate-interface/issues/14
    this would work but only with newer substrate version than rc2
    """
    from substrateinterface import SubstrateInterface, Keypair, SubstrateRequestException
    from pprint import pformat
    substrate = SubstrateInterface( url="ws://127.0.0.1:9944" )
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

if __name__ == '__main__':
    errorenous()