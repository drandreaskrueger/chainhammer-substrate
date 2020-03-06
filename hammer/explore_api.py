#!/usr/bin/env python3
"""
@summary: explore the substrate API via the new 'polkascan' library substrateinterface

@version: v02 (6/March/2020)
@since:   6/March/2020
@author:  https://github.com/drandreaskrueger
@see:     https://github.com/drandreaskrueger/chainhammer-substrate for updates
"""

import time #, sys, inspect
from pprint import pprint
import substrateinterface

URL = "ws://127.0.0.1:9900/"  # "ws://127.0.0.1:9944/"
URL = "http://127.0.0.1:9800" # "http://127.0.0.1:9933"

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
    

if __name__ == '__main__':
    substrate = substrateinterface.SubstrateInterface(url=URL)
    explore_all_members(substrate)
    # loop_report_new_chain_head(substrate)
    explore_get_metadata_call_functions(substrate)
    explore_get_metadata_storage_functions(substrate)
    
    yes = has_call_function(substrate, ifprint=True); 

