#!/usr/bin/env python3
"""
@summary: explore the substrate API

@version: v01 (6/March/2020)
@since:   6/March/2020
@author:  https://github.com/drandreaskrueger
@see:     https://github.com/drandreaskrueger/chainhammer-substrate for updates
"""

import sys, inspect
import substrateinterface

WS = "ws://127.0.0.1:9900/"

substrate = substrateinterface.SubstrateInterface(url=WS)

functions, errors = [], []
for name in sorted(dir(substrate)):
    if name.startswith("__"):
        continue
    member = getattr(substrate, name)
    if type(member) in [type(None), type(1), type({}), type(True), type("")]: # or inspect.isclass(member):
        print ("%20s = %s" % (name, member))
    else:
        try:
            result = member()
            functions.append((name, result))
        except (TypeError, NotImplementedError) as e:
            missing = str(e).split("required positional argument")
            missing = missing [1].split(":")[1] if len(missing) > 1 else missing[0]
            # print (missing)
            err = str(type(e)) .replace("<class '","") .replace("'>", ":")
            msg = str(e).replace(name+"() ", "") .replace("argument:", "argument: ") 
            errors.append((name, "%s %s" % (err, msg), missing))
            
print ()
print ("\n".join(["%31s() = %s" % (n,r) for n,r in functions]))

print ()
errors.sort(key = lambda x: x[2]) # sort by "missing xyz" message
print ("\n".join(["%30s() = %s" % (n,e) for n,e, _ in errors]))

