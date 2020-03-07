'''
Created on 7 Mar 2020

@author: andreas
'''

import substrateinterface

substrate = substrateinterface.SubstrateInterface(url="http://127.0.0.1:9800") # , address_type=42) # "http://127.0.0.1:9933")

PS_EXAMPLE_ADDRESS ='EaG2CRhJWPb7qmdcJvy3LiWdh26Jreu9Dx6R1rXxPmYXoDk'; print (len(PS_EXAMPLE_ADDRESS))
ALICE_ADDRESS =     '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY'; print (len(ALICE_ADDRESS))
ALICE_PUBKEY =      '0xd43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d'

"""
subkey inspect //Alice
Secret Key URI `//Alice` is account:
  Secret seed:      0xe5be9a5092b81bca64be81d212e7f2f9eba183bb7a90954f7b76361f6edb5c0a
  Public key (hex): 0xd43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d
  Account ID:       0xd43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d
  SS58 Address:     5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY
"""


def balance_transfer(dest, value):
    payload = substrate.compose_call(call_module='Balances',
                                     call_function='transfer',
                                     call_params={'dest': dest,
                                                  'value': value})
    print (payload)


balance_transfer(dest=PS_EXAMPLE_ADDRESS,      value=1000000000000)

"""
balance_transfer(dest=     ALICE_ADDRESS,      value=1000000000000)  # ValueError: Invalid account index length
balance_transfer(dest=     ALICE_ADDRESS[1:],  value=1000000000000)  # ValueError: Invalid checksum
balance_transfer(dest=     ALICE_ADDRESS[:-1], value=1000000000000)  # ValueError: Invalid address length
"""
balance_transfer(dest=     ALICE_PUBKEY,      value=1000000000000)  # ValueError: Invalid account index length