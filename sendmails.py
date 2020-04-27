import termcolor

DEBUG = False
LISTOFLINKS = "listoflinks.txt"

def printDebug(message):
    if DEBUG == True:
        print(termcolor.colored("[D] {0}".format(message), 'yellow'))

def readLine(fname):
    printDebug("Read file '{0}'".format(fname))
    with open(fname) as f:
        lines = f.readlines()
        
    return lines


print("hi")
