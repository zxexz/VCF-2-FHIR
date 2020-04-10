import re
from itertools import cycle
import numpy as np
import math
import warnings
warnings.simplefilter("ignore", UserWarning)

def cleanVCFOld(f,nextelem):
    for key, value in f['REF'].iteritems():
        if not value.isalpha():
            f = f.drop(key)

    for key, value in f['FILTER'].iteritems():
        if not value in ["pass", "PASS", '.']:
            f = f.drop(key)

    for key, value in f['ALT'].iteritems():
            if not value in ['.']:
                if not re.match("^[a-zA-Z,]*[a-zA-Z]+(?:, [a-zA-Z,]*[a-zA-Z]+)*$",value):
                    f = f.drop(key)
    
    for i in f.index:
        if f.at[i,'FORMAT'].split(':')[0] == 'GT':
            if f.at[i,nextelem].split(':')[0] in ['0/0','0|0'] or f.at[i,'ALT'] in ['.']:
                f.at[i,'ALT'] = f.at[i,'REF']
            if f.at[i,nextelem].split(':')[0] in ['./.','.|.','.\.']:
                f = f.drop(i)
            elif re.match(".",f.at[i,nextelem].split(':')[0]):
                temp = f.at[i,nextelem].split(':')[0].replace('.','0')
                s = [str(i) for i in f.at[i,nextelem].split(':')[1:]] 
                res=[temp]+s
                f[nextelem][i] = ":".join(res)
    f = f.loc[:, :nextelem]
    return f

def cleanVCF(f):
    nextelem = 'sample1'
    Ignore=['POS','REF','ALT','FORMAT']
    df = f
    df.index = f.index
    for i in Ignore:
        f[i]=f[i].replace('.',np.NaN)    
        f[i]=f[i].replace('',np.NaN)    
        df=df[f[i].notnull()]

    f = df
    for key, value in f['INFO'].iteritems():
        if str(value)[:6] in "SVTYPE":
            f = f.drop(key)
        elif isinstance(value, float):
            f = f.drop(key)

    for key, value in f['REF'].iteritems():
        if not str(value).isalpha():
            f = f.drop(key)

    for key, value in f['FILTER'].iteritems():
        if not value in ["pass", "PASS", '.']:
            f = f.drop(key)

    for key, value in f['ALT'].iteritems():
            if not value in ['.']:
                if not re.match("^[a-zA-Z,]*[a-zA-Z]+(?:, [a-zA-Z,]*[a-zA-Z]+)*$",value):
                    f = f.drop(key)
    
    for i in f.index:
        if isinstance(f.at[i,'ID'], float):
            f = f.drop(i)
            continue
        if isinstance(f.at[i,'QUAL'], float):
            f = f.drop(i)
            continue
        if f.at[i,'FORMAT'].split(':')[0] == 'GT':
            if f.at[i,nextelem].split(':')[0] in ['0/0','0|0'] or f.at[i,'ALT'] in ['.'] or f.at[i,'ALT'] in ['.'] or f.at[i,nextelem].split(':')[0] == '0':
                f.at[i,'ALT'] = f.at[i,'REF']
            if f.at[i,nextelem].split(':')[0] in ['./.','.|.','.\.']:
                f = f.drop(i)
            elif re.match(".",f.at[i,nextelem].split(':')[0]):
                temp = f.at[i,nextelem].split(':')[0].replace('.','0')
                s = [str(i) for i in f.at[i,nextelem].split(':')[1:]] 
                res=[temp]+s
                f[nextelem][i] = ":".join(res)
        else:
            f = f.drop(i)
    f = f.loc[:, :nextelem]
    return f

def getNextElement(headers,elem):
    headers = list(headers)
    running = True
    licycle = cycle(headers)
    nextelem = next(licycle)
    while running:
        thiselem, nextelem = nextelem, next(licycle)
        if(thiselem==elem):
            break
    return nextelem
