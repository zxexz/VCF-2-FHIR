import pandas as pd

def getAllelicState(f,nextelem,gender):
    allelicStates = []
    allelicCodes = []
    allelicState = ''
    allelicCode = ''
    for i in f.index:
        formatVal = f.at[i,'FORMAT']
        formats = formatVal.split(':')
        index = formats.index('GT')
        sampleVal = f.at[i,nextelem]
        samples = sampleVal.split(':')
        allele = samples[index].split('/')
        allelePipe = samples[index].split('|')
        if len(allelePipe) == 2:
            x = allelePipe[0]
            y = allelePipe[1]
        if len(allele) == 2:
            x = allele[0]
            y = allele[1]
        else:
            if gender == 'M' and f.at[i,'#CHROM'] == 'MT':
                allelicState = 'Homoplasmic'
                allelicCode = 'LA6704-6'


        if gender == 'F':
            if f.at[i,'#CHROM'] != 'Y' and f.at[i,'#CHROM'] != 'MT' :
                if x != y:
                    allelicState = 'heterozygous'
                    allelicCode = 'LA6706-1'
                else:
                    allelicState = 'homozygous'
                    allelicCode = 'LA6705-3'
        elif gender == 'M':
            if f.at[i,'#CHROM'] == 'Y' or f.at[i,'#CHROM'] == 'X':
                allelicState = 'hemizygous'
                allelicCode = 'LA6707-9'
            elif f.at[i,'#CHROM'] == 'MT':
                if x != y:
                    allelicState = 'heteroplasmic'
                    allelicCode = 'LA6703-8'
                    
                #elif formatVal['GT'] in ["0","1"]:
                    #allelicState = 'Homoplasmic'
                    #allelicCode = 'LA6704-6'
                else:
                    allelicState = 'homoplasmic'
                    allelicCode = 'LA6704-6'
            else:
                if x != y:
                    allelicState = 'heterozygous'
                    allelicCode = 'LA6706-1'
                else:
                    allelicState = 'homozygous'
                    allelicCode = 'LA6705-3'
                
                

        allelicStates.append(allelicState)
        allelicCodes.append(allelicCode)
    f['ALLELE'] = allelicStates
    f['CODE'] = allelicCodes
    return f


