#!/usr/bin/env python3
"""
@summary: how to sign and submit a transaction

@version: v04 (11/March/2020)
@since:   6/March/2020
@author:  https://github.com/drandreaskrueger
@see:     https://github.com/drandreaskrueger/chainhammer-substrate for updates

@summary: wow, sending a transaction to a blockchain in any programming language 
          should be a very simple thing to do, but this is already day 5, and 
          the problem is still not fully solved. However, via chat a big hurdle was 
          removed today, so let's hope they can finish soon ... I have prepared everything: 
          https://github.com/polkascan/py-substrate-interface/issues/10#issuecomment-597420859   
"""

from pprint import pprint
import substrateinterface 
substrate = substrateinterface.SubstrateInterface(url="ws://127.0.0.1:9900/")

BOB_ADDRESS = '5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty'
payload = substrate.compose_call(call_module='Balances',
                                 call_function='transfer',
                                 call_params={'dest': BOB_ADDRESS,
                                              'value': 1000000000000})
print ("payload input: ", payload)
# 0xa8040400ff8eaf04151687736326c9fea17e25fc5287613693c912909cb226aa4794f26a48070010a5d4e8

# docker run jacogr/polkadot-js-tools signer sign --type sr25519 --account //Alice --seed "//Alice" 0xa8040400ff8eaf04151687736326c9fea17e25fc5287613693c912909cb226aa4794f26a48070010a5d4e8
# Signature: 0x019c9e11b24183d4864c401e267584fdeb08282eb0a7c21d0bd35fab99628d5f416c7c14ee94518579c4ff845508aee83f0006aab2e2c5ce091e2ba5006ee01081

signed = "0x019c9e11b24183d4864c401e267584fdeb08282eb0a7c21d0bd35fab99628d5f416c7c14ee94518579c4ff845508aee83f0006aab2e2c5ce091e2ba5006ee01081"
print ("payload signed:", signed)

extrinsic = {"signature": signed}

def encode_extrinsic(struct):
    # probably scale encoding again???
    # this might help: https://wiki.polkadot.network/docs/en/build-exchange-integration#transferring-balances
    return 0x0000

# result = substrate.rpc_request(method="rpc_methods", params=None)
method = "author_submitExtrinsic"; print ("RPC method:    ", method)
result = substrate.rpc_request(method=method, params=[encode_extrinsic(extrinsic)])
result = result["result"] if "result" in result.keys() else result["error"]
pprint (result, width=120)

