import pandas as pd
import numpy as np
import cpymad
import itertools

def sequencesDF(madHandle):
    sequences=madHandle.sequence
    seqDict={}
    for ii in sequences:
        seqDict[ii]={}
        if sequences[ii].has_beam:
            seqDict[ii]['beam']= True
        else:
            seqDict[ii]['beam']=False
        if sequences[ii].is_expanded:
            seqDict[ii]['expanded']=True
        else:
            seqDict[ii]['expanded']=False
    return pd.DataFrame(seqDict).transpose()

def beamsDF(madHandle):
    dfList=[]
    sequences=madHandle.sequence
    for ii in sequences:
        dfList.append(pd.DataFrame([dict(sequences[ii].beam)], index=[ii]))
    if len(dfList)>0:
        return pd.concat(dfList)
    else:
        return pd.DataFrame()

def _extractParameters(mystring):
    if type(mystring)=='NoneType' or mystring==None or mystring=='None' or mystring=='[None]':
        return []
    else:
        for i in [
        '*','-','/','+','(',')','[', ']',',','\'','None']:
            mystring=mystring.replace(i,' ')
        myList=mystring.split(' ')
        myList=list(np.unique(myList))
        if '' in myList:
            myList.remove('')
        if type(myList)=='NoneType':
            myList=[]
        for i in myList.copy():
            if i.isdigit() or i[0].isdigit():
                myList.remove(i)
        myList=list(set(myList)-
        set([
            'sqrt',
            'log',
            'log10',
            'exp',
            'sin',
            'cos',
            'tan',
            'asin',
            'acos',
            'atan',
            'sinh',
            'cosh',
            'tanh',
            'sinc',
            'abs',
            'erf',
            'erfc',
            'floor',
            'ceil',
            'round',
            'frac',
            'ranf',
            'gauss',
            'tgauss']))
        return myList 

def dependentVariablesDF(madHandle):
    myDict={}
    for i in list(madHandle.globals):
        aux=_extractParameters(str(madHandle._libmadx.get_var(i)))
        if aux!=[]:
            myDict[i]={}
            myDict[i]['parameters']=list(np.unique(aux))
    
    myhash=hash(str(myDict))
    for n in range(100):
        for i in myDict:
            aux=[]
            for j in myDict[i]['parameters']:
                try:
                    aux=aux+myDict[j]['parameters']
                except:
                    aux=aux+[j]
            myDict[i]['knobs']=list(np.unique(aux))
        if myhash==hash(str(myDict)):
            break
        else:
            myhash=hash(str(myDict))
    
    for i in myDict:
        for j in myDict[i]['knobs'].copy():
            if madHandle._libmadx.get_var_type(j)==0:
                myDict[i]['knobs'].remove(j)
        myDict[i]['expression']=madHandle._libmadx.get_var(i)
        myDict[i]['value']=madHandle.globals[i]
    
    return pd.DataFrame(myDict).transpose()[['value','expression','parameters','knobs']].sort_index()

def independentVariablesDF(mad):
    depDF=dependentVariablesDF(mad)
    aux=list(depDF['knobs'].values)
    aux=list(itertools.chain.from_iterable(aux))
    fundamentalSet=set(np.unique(aux))
    independentVariableSet=set(mad.globals)-set(depDF.index)
    myDict={}
    for i in independentVariableSet:
        myDict[i]={}
        if mad._libmadx.get_var_type(i)==0:
            myDict[i]['constant']=True
            myDict[i]['knob']=False
        else:
            myDict[i]['constant']=False
            if i in fundamentalSet:
                myDict[i]['knob']=True
            else:
                myDict[i]['knob']=False
        myDict[i]['value']=mad.globals[i]
    
    return pd.DataFrame(myDict).transpose()[['value','constant','knob']].sort_index()

def _knobsFromParameters(parameters, indepDF, depDF):
    myKnobs=[]
    for i in parameters:
        if i in indepDF.index:
            if not indepDF.loc[i]['constant']:
                myKnobs.append([i])
        else:
            try:
                myKnobs.append(depDF.loc[i]['knobs'])
            except:
                print(f'Variable {i} not defined! Cosidered as a knob.')
                myKnobs.append([i])
    return list(itertools.chain.from_iterable(myKnobs))

def sequenceDF(mad,sequenceName):
    myList=[]
    sequences=mad.sequence
    mySequence=sequences[sequenceName]
    indepDF=independentVariablesDF(mad)
    depDF=dependentVariablesDF(mad)

    for myIndex, element in enumerate(mySequence.elements):
        aux=mad._libmadx.get_element(sequenceName,myIndex)
        myDict={}
        myDict['parameters']=[]
        for i in aux:
            myDict[i]=aux[i]
        del myDict['data']

        for i in aux['data']:
            myDict[i]=str(aux['data'][i])
            if isinstance(aux['data'][i], cpymad.types.Parameter):
                myDict[i+' value']=aux['data'][i].value
                myDict['parameters']+=_extractParameters(str(aux['data'][i].expr))
        myDict['parameters']=np.unique(myDict['parameters'])
        myList.append(myDict)
    myDF=pd.DataFrame(myList)
    myDF=myDF.set_index('name')
    myDF.index.name=''
    myDF['knobs']=myDF['parameters'].apply(lambda x: _knobsFromParameters(x,indepDF,depDF))
    firstColumns=['position','parent','base_type','length','parameters','knobs']
    lastColumns=list(set(myDF.columns)-set(firstColumns))
    lastColumns.sort()
    return myDF[firstColumns+lastColumns]

def tableDF(table):
    myDF=pd.DataFrame(dict(table))
    myDF=myDF.set_index('name')
    myDF.index.name=''
    return myDF