import os, sys
def findPy(p):
    print "DEBUG", sys.argv[0], os.path.abspath(sys.argv[0])
    return os.path.dirname(os.path.abspath(sys.argv[0])) + "/" + p

##def findPy(p):
##    for e in ("./", "../", "../../"):
##        for f in ("", "py/"):
##            if os.path.exists(e + f + p):
##                return e + f + p
##    print "cannot find", p, "anywhere"
##    exit()
