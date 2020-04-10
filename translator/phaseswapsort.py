import pandas as pd
from collections import OrderedDict
import numpy as np
import re
from itertools import cycle
import logging
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s -%(message)s', datefmt='%d-%b-%y %H:%M')


def getSequenceRelation(f,nextelem):
    RelationTable= pd.DataFrame(columns=['POS1','POS2','Relation'])

    GTPSMapping = f.apply(lambda x: OrderedDict(zip(x['FORMAT'].split(':'), x[nextelem].split(':'))), 1).values.tolist()
    GTPSdf = pd.DataFrame(GTPSMapping)
    GTPSdf.index = f.index
    POS=list(f['POS'])
    GTPSdf['POS'] = POS
    GTPSdf = GTPSdf[GTPSdf['GT'].notnull()]
    for i in GTPSdf.index:
        if len(GTPSdf.at[i,'GT'].split('|')) < 2:
            GTPSdf = GTPSdf.drop(i)
    #New dataframe for collection of repeated POS values
    samePOS=GTPSdf[GTPSdf.duplicated('PS', keep=False)]

    # Drop records with absent PS values
    try:
        samePOS['PS']=samePOS['PS'].replace('.',np.NaN)
        samePOS=samePOS[samePOS.PS.notnull()]
    except Exception as e:
        logging.error(e)

    # Replace '.' with 0 for GT values
    samePOS['GT']=samePOS['GT'].str.replace('.','0')
    try:
        row_iterator = samePOS.iterrows()
        _, last = next(row_iterator)
    except:
        pass #no sequence relations found
    for i, row in row_iterator:
        if row['PS'] == last['PS'] :
            if row['GT']==last['GT']:
                # Cis type relation
                RelationTable = RelationTable.append({'POS1': last['POS'], 'POS2': row['POS'], 'Relation': 'Cis'}, ignore_index=True)
            else:
                # Trans type relation
                RelationTable = RelationTable.append({'POS1': last['POS'], 'POS2': row['POS'], 'Relation': 'Trans'}, ignore_index=True)

        last = row
    return RelationTable 