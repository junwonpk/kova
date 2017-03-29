import os
import sys
import json
from kovat import *

if __name__ == '__main__':
    kovat = Kovat()
    while(1):
        message = raw_input('User: ')
        response = kovat.chat(message)
        print 'Kova: ' + response
