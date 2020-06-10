#!/usr/bin/env python3
"""
@summary: found an error, reported in https://github.com/polkascan/py-substrate-interface/issues/13

@version: v01 (10/June/2020)
@since:   10/June/2020
@author:  https://github.com/drandreaskrueger
@see:     https://github.com/drandreaskrueger/chainhammer-substrate for updates
"""

# import requests; print(requests.__version__) # example for __version__
import substrateinterface
# import scalecodec
# print (substrateinterface.__version__, scalecodec.__version__)
substrate = substrateinterface.SubstrateInterface(url="ws://127.0.0.1:9944/")
ch=substrate.get_chain_head()
chb=substrate.get_chain_block(ch)
chbn=int(chb['block']['header']['number'],16)
print("block #%s (%s)" % (chbn, ch))
print(substrate.get_runtime_events(ch))
print(substrate.get_runtime_events())



