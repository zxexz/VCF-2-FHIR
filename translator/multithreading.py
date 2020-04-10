import os
import re
import pandas as pd
from itertools import cycle
from functools import partial
from multiprocessing import Pool, cpu_count, Manager
from .filecleaner import cleanVCF, getNextElement
from .xmlGenerator import getFhirXML, getEmptyFhirXML
from .jsonGenerator import getFhirJSON,getEmptyFhirJSON

import logging
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s -%(message)s', datefmt='%d-%b-%y %H:%M')

pd.options.mode.chained_assignment = None


def translate(VCF_FILE,patientID,refSeq,noCall=False,gender="M"):
    logging.info("[Cleaning VCF records]")
    pool = Pool(processes=4)    
    headers = ['#CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'FORMAT', 'sample1']
    result = pool.apply_async(getNextElement,[headers,'FORMAT'])
    nextelem = result.get()
    df_chunk = pd.read_csv(VCF_FILE,sep='\t',chunksize=10, names=headers)
    chunk_list = []
    clean = pool.map(cleanVCF,df_chunk)
    cleanVcf = pd.concat(clean)


    try:
        logging.info(cleanVcf)

        fhirResponse = getFhirJSON(cleanVcf,nextelem,patientID,refSeq,noCall=False,gender="M")

    except:
        logging.info("* No valid VCF records found")
        fhirResponse = getEmptyFhirJSON(patientID,refSeq,noCall)

    finally:
        pool.terminate()
        pool.join()
        return fhirResponse
        