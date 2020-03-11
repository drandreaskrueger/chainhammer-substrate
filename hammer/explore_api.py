#!/usr/bin/env python3
"""
@summary: explore the substrate API via the new 'polkascan' library substrateinterface

@version: v02 (6/March/2020)
@since:   6/March/2020
@author:  https://github.com/drandreaskrueger
@see:     https://github.com/drandreaskrueger/chainhammer-substrate for updates
"""

import time #, sys, inspect
from subprocess import run, PIPE
from pprint import pprint
import substrateinterface
from substrateinterface.utils.ss58 import ss58_encode

URL = "ws://127.0.0.1:9900/"  # "ws://127.0.0.1:9944/"
# URL = "http://127.0.0.1:9800" # "http://127.0.0.1:9933"

ALICE_ADDRESS=     '5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY'
BOB_ADDRESS=       '5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty'

"""
subkey inspect //Bob
Secret Key URI `//Bob` is account:
  Secret seed:      0x398f0c28f98885e046333d4a41c19cee4c37368a9832c6502f6cfd182e2aef89
  Public key (hex): 0x8eaf04151687736326c9fea17e25fc5287613693c912909cb226aa4794f26a48
  Account ID:       0x8eaf04151687736326c9fea17e25fc5287613693c912909cb226aa4794f26a48
  SS58 Address:     5FHneW46xGXgs5mUiveU4sbTyGBzmstUspZC92UhjJM694ty
"""

PS_EXAMPLE_ADDRESS ='EaG2CRhJWPb7qmdcJvy3LiWdh26Jreu9Dx6R1rXxPmYXoDk'; #print (len(PS_EXAMPLE_ADDRESS)); exit()
X_ADDRESS         ='5Gdc7hM6WqVjd23YaJR1bUWJheCo4ymrcKAFc35FpfbeH68f'; #print (len(X_ADDRESS)); exit()
X_PHRASE = 'observe analyst fabric sentence burden injury inmate wheat flash labor save antenna'
X_SECRET = '0x7c15195c7e2d6026175f2d6d53a9cfab948a275a09ccfea13bb658d53f1ce9fb'
X_PUBKEY = '0xca08b4e0f53054628a43912ffbb6d00a0362921ba9781932297edc037d197a5d'

def title (title):
    print ()
    print ("-" * len(title))
    print (title)
    print ("-" * len(title))

def explore_all_members(substrate):
    
    title ("exploring 'substrate'" )    
    functions, errors = [], []
    for name in sorted(dir(substrate)):
        
        if name.startswith("__") and name not in ("__doc__", "__module__", "__sizeof__", "__class__"): 
            continue # ignore most object.__ members
        
        member = getattr(substrate, name)
        if type(member) in [type(None), type(1), type({}), type(True), type("")]:
            print ("%20s = %s" % (name, member))
        else:
            try:
                result = member()
                
            except (TypeError, NotImplementedError) as e:
                missing_args = str(e).split("required positional argument")
                missing_args = missing_args[1].split(":")[1] if len(missing_args) > 1 else missing_args[0]
                err = str(type(e)) .replace("<class '","") .replace("'>", ":")
                msg = str(e).replace(name+"() ", "") .replace("argument:", "argument: ") 

                errors.append((name, "%s %s" % (err, msg), missing_args))
            else:
                functions.append((name, result))
                
    print ("\n" + ("\n".join(["%31s() = %s" % (n,r) for n,r in functions])))
    errors.sort(key = lambda x: x[2]) # sort by "missing xyz" message
    print ("\n" + ("\n".join(["%30s() = %s" % (n,e) for n,e, _ in errors])))


def explore_block(substrate, bh):
    print ("block with hash:", bh)
    b = substrate.get_chain_block(bh)
    bn = int(b["block"]["header"]["number"], 16)
    nt = len(b["block"]["extrinsics"])
    print ("... that is block number:", bn)
    print ("... that block has transactions (extrinsics):", nt)
    return b, bn, nt 

def loop_report_new_chain_head(substrate):
    
    old_chh = None
    while True:
        while True:
            chh = substrate.get_chain_head()
            if chh!=old_chh:
                break
            time.sleep(0.5)
        print ("Chain head is now at", end=" ")
        b, bn, nt = explore_block(substrate, chh)
        old_chh = chh


def explore_get_metadata_call_functions(substrate):
    
    chh = substrate.get_chain_head()
    
    title ("exploring get_metadata_call_functions( %s )" % chh)
    mdcf = substrate.get_metadata_call_functions(chh)
    # pprint (mdcf)
    module_prefix_charlength = max([len(func["module_prefix"]) for func in mdcf])
    for func in mdcf:
        pattern = '{module_prefix:>%ds}.{call_name}(' % ( module_prefix_charlength +1 )
        text = pattern .format(**func)
        args = func["call_args"]
        if len(args):
            text+=" "
            for a in args:
                text += "{name}:{type}, ".format(**a)
            text = text [:-2] + " " # remove last comma
        text += ")" 
        print (text)
    return chh, mdcf


def explore_get_metadata_storage_functions(substrate, chh=None):
    if not chh:
        chh = substrate.get_chain_head()
    
    title ("exploring get_metadata_storage_functions( %s )" % chh)
    mdsf = substrate.get_metadata_storage_functions(chh)
    #pprint (mdsf)
    
    module_prefix_charlength = max([len(func["module_prefix"]) for func in mdsf])
    for func in mdsf:
        pattern = '{module_prefix:>%ds}.{storage_name}(' % ( module_prefix_charlength +1 )
        text = pattern .format(**func)
        if not func["type_key1"]:
            text += ")"
        else:
            text += " {type_key1}".format(**func)
            if func["type_key2"]:
                text += ", {type_key2}".format(**func)
            text += " )"
        
        text += " --> " + func["type_value"]
        text += " --> fallback = {storage_fallback} ({storage_fallback_scale})".format(**func)
            
        print (text)
    return chh, mdsf

def has_call_function(substrate, module_prefix="TemplateModule", call_name="do_something", ifprint=False ):
    chh = substrate.get_chain_head()
    mdcf = substrate.get_metadata_call_functions(chh)
    exists = (module_prefix, call_name) in [(cf["module_prefix"], cf["call_name"]) for cf in mdcf]
    if ifprint:
        title("has call_function: %s.%s" % (module_prefix, call_name))
        print (exists)
    return exists
    
    
def show_extrinsics_of_block(substrate, bh = None): # Set block_hash to None for chaintip
    """
    variation of
    https://github.com/polkascan/py-substrate-interface/blob/master/README.md#get-extrinsics-for-a-certain-block
    """

    # Retrieve extrinsics in block
    result = substrate.get_runtime_block(block_hash=bh)

    for extrinsic in result['block']['extrinsics']:
    
        if 'account_id' in extrinsic:
            signed_by_address = ss58_encode(address=extrinsic['account_id'], address_type=2)
        else:
            signed_by_address = None
    
        print('\n{}.{} Signer={}'.format(
            extrinsic['call_module'],
            extrinsic['call_function'],
            signed_by_address
        ), end=". ")
    
        # Loop through params
        
        numParams = len(extrinsic['params'])
        if numParams:
            print ("Param/s: ", end="")
        for i, param in enumerate(extrinsic['params']):
    
            if param['type'] == 'Address':
                param['value'] = ss58_encode(address=param['value'], address_type=2)
    
            if param['type'] == 'Compact<Balance>':
                param['value'] = '{} DOT'.format(param['value'] / 10**12)
    
            print("{}={}".format(param['name'], param['value']), end="")
            if i+1 < numParams:
                print (", ")
    
        print()


def get_balance(substrate, address, block_hash=None, ifprint=False):
    balance = substrate.get_runtime_state(module='Balances',
                                      storage_function='FreeBalance',
                                      params=[address],
                                      block_hash=block_hash
                                      ).get('result') 
    dot = float(balance) / 10**12 if balance else 0
    
    if ifprint:
        print("Current balance: {} DOT".format(dot))
    return dot
    

def rpc_methods(substrate):
    """
    read from node:   rpc_methods
    """
    title("rpc_methods")
    result = substrate.rpc_request(method="rpc_methods", params=None)
    methods = sorted(result["result"]["methods"])
    module_function = [dict(zip(("module", "function"), name.split("_"))) for name in methods]
    leftsidelen = max([len(parts["module"]) for parts in module_function])
    pattern = '{module:>%ds}_{function}' % ( leftsidelen +1 )
    print("\n".join([pattern.format(**pair) for pair in module_function]))



class SubkeyError(Exception): pass 

def os_command_with_pipe(command=['grep', 'f'], text='one\ntwo\nthree\nfour\nfive\nsix\n'):
    """
    https://stackoverflow.com/a/165662
    """
    p = run(command, stdout=PIPE, input=text, encoding='ascii')
    if p.returncode != 0:
        raise SubkeyError(p.returncode)
    return p.stdout

def sign(payload, signer):
    signed = os_command_with_pipe(["subkey", "sign-transaction", signer], payload)
    return signed


def balance_transfer(dest, value, signer='//Alice'):
    payload = substrate.compose_call(call_module='Balances',
                                     call_function='transfer',
                                     call_params={'dest': dest,
                                                  'value': value})
    print ("payload", payload)
    # signed = sign(payload, signer)
    exit()
    print (signed)
    # result = substrate.rpc_request(method="author_submitAndWatchExtrinsic", params=[signed])
    
    result = substrate.rpc_request(method="author_submitExtrinsic", params=[signed])
    print (result)


if __name__ == '__main__':
    substrate = substrateinterface.SubstrateInterface(url=URL) # , address_type=42)
    
    """   
    explore_all_members(substrate)
    
    # loop_report_new_chain_head(substrate)
    explore_get_metadata_call_functions(substrate)
    explore_get_metadata_storage_functions(substrate)
    yes = has_call_function(substrate, ifprint=True)
    
    title("extrinsics of a block")
    show_extrinsics_of_block(substrate)
    """
    
    title("balances")
    dot = get_balance(substrate, address=ALICE_ADDRESS, ifprint=True)
    # dot = get_balance(substrate, address=X_ADDRESS, ifprint=True)
    dot = get_balance(substrate, address=BOB_ADDRESS, ifprint=True)

    # print (os_command_with_pipe())
    # balance_transfer(dest=BOB_ADDRESS, value=1000000000000)
    
    
    rpc_methods(substrate)

    