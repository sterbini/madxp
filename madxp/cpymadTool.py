import pandas as pd
import numpy as np
import cpymad
import itertools

def sequencesDF(mad):
    '''
    Extract the pandas DF with the list of the sequences defined in the MAD-X handle.
    
    Args:
        mad: The handle to MAD-X
    
    Returns:
        The pandas DF of the sequences. It can be and empty DF.
    
    See madxp/examples/variablesExamples/000_run.py

    '''
    sequences=mad.sequence
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

def beamsDF(mad):
    '''
    Extract the pandas DF with the beams associated to the sequences defined in the MAD-X handle.
    
    Args:
        mad: The handle to MAD-X
    
    Returns:
        The pandas DF of the beams. It can be and empty DF.

    See madxp/examples/variablesExamples/000_run.py
    '''
    dfList=[]
    sequences=mad.sequence
    for ii in sequences:
        try:
            dfList.append(pd.DataFrame([dict(sequences[ii].beam)], index=[ii]))
        except:
            print(f'The sequence {ii} has no beam attached.')
    if len(dfList)>0:
        return pd.concat(dfList)
    else:
        return pd.DataFrame()

def _extractParameters(mystring):
    '''
    Extract all the parameters of a MAD-X expression.

    Args:
        mystring: The string of the MAD-X expression to parse.
    
    Returns:
        The list of the parameters present in the MAD-X expression.

    '''
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

def variablesDict(mad):
    '''

    Extract the dictionary of the variables and constant pandas DF of the MAD-X global workspace.

    Args:
        mad: The MAD-X handle.
    
    Returns:
        The a dictionary containing:
        - constantDF: the pandas DF with the constants
        - independentVariableDF: the pandas DF with the independent variables
        - dependentVariableDF: the pandas DF with the dependent variables
    All the three DFs have a columns 'value' with the numerical values of the costants/variables.
    The dependentVariableDF, in addition to 'value' has the following columns:
        - 'expression': the string corrensponding to the MAD-X expression
        - 'parameters': the list of parameters used in the expression
        - 'knobs': the list of the independent variables that control 
          the dependent variables. Note tha the parameters can be constants and/or dependent variables,
          whereas the 'knobs' are only independent variables.
    '''
    myDict={}
    aux=_independentVariablesDF(mad)
    import numpy as np
    independentVariablesDF=aux[np.logical_not(aux['constant'])].copy()
    del independentVariablesDF['constant']
    constantDF=aux[aux['constant']].copy()
    del constantDF['constant']
    myDict['constantDF']=constantDF
    myDict['independentVariableDF']=independentVariablesDF
    myDict['dependentVariableDF']=_dependentVariablesDF(mad)
    
    return myDict

def _dependentVariablesDF(mad):
    '''
    Extract the pandas DF with the dependent variables of the MAD-X handle.
    
    Args:
        mad: The handle to MAD-X
    
    Returns:
        The pandas DF of the dependent variables. The columns of the DF correspond to the 
        - the numerical value of the dependent variable (value)
        - the string corrensponding to the MAD-X expression (expression)
        - the list of parameters used in the expression (parameters)
        - the list of the fundamental independent variables. 
          These are independent variables that control numerical values of the variable (knobs).
    
    See madxp/examples/variablesExamples/000_run.py
    '''
    myDict={}
    for i in list(mad.globals):
        aux=_extractParameters(str(mad._libmadx.get_var(i)))
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
            if mad._libmadx.get_var_type(j)==0:
                myDict[i]['knobs'].remove(j)
        myDict[i]['expression']=mad._libmadx.get_var(i)
        myDict[i]['value']=mad.globals[i]
    
    return pd.DataFrame(myDict).transpose()[['value','expression','parameters','knobs']].sort_index()

def _independentVariablesDF(mad):
    '''
    Extract the pandas DF with the independent variables of the MAD-X handle.
    
    Args:
        mad: The handle to MAD-X
    
    Returns:
        The pandas DF of the independent variables. The columns of the DF correspond to the 
        - the numerical value of the independent variable (value)
        - a boolean value to know it the variable is constant or not (constant)
   
    See madxp/examples/variablesExamples/000_run.py
    '''

    depDF=_dependentVariablesDF(mad)
    aux=list(depDF['knobs'].values)
    aux=list(itertools.chain.from_iterable(aux))
    #fundamentalSet=set(np.unique(aux))
    independentVariableSet=set(mad.globals)-set(depDF.index)
    myDict={}
    for i in independentVariableSet:
        myDict[i]={}
        if mad._libmadx.get_var_type(i)==0:
            myDict[i]['constant']=True
            # myDict[i]['knob']=False
        else:
            myDict[i]['constant']=False
            # if i in fundamentalSet:
            #    myDict[i]['knob']=True
            # else:
            #    myDict[i]['knob']=False
        myDict[i]['value']=mad.globals[i]
    
    return pd.DataFrame(myDict).transpose()[['value','constant']].sort_index()

def _knobsFromParameters(parameters, indepDF, depDF):
    '''
    Extract the list of knobs from a list of parameters.
    
    Args:
        parameters: list of parameters
        indepDF: independent variable DF
        depDF: dependent variable DF

    Returns:
        The list of knobs corresponding to the list of parameters.
    
    See madxp/examples/variablesExamples/000_run.py
    '''
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
    '''
    Extract a pandas DF of the list of the elements and all their attributes for a given sequence.
    
    Args:
        mad: the MAD-X handle
        sequenceName: the sequence name

    Returns:
        The list of knobs corresponding to the list of parameters.
    
    See madxp/examples/variablesExamples/000_run.py
    '''
    myList=[]
    sequences=mad.sequence
    mySequence=sequences[sequenceName]
    indepDF=_independentVariablesDF(mad)
    depDF=_dependentVariablesDF(mad)

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

def knobsList(myDF):
    '''
    Extract the knob list of a pandas DF (it assumes that DF has a column called "knobs")
    and contanting lists
    
    Args:
        myDF: a pandas DF (it assumes that DF has a column called "knobs").

    Returns:
        The list of knobs.
    
    See madxp/examples/variablesExamples/000_run.py

    '''
    import itertools
    import numpy as np
    aux= list(myDF['knobs'].values)
    return list(np.unique(list(itertools.chain.from_iterable(aux))))

def filterKnobDepedences(myKnob,myDF):
    '''
    Filter the pandas DF, 'myDF', returning only the rows that depend on the selected knob, 'myKnob'.
    
    Args:
        myKnob: the name of the knob to filter.
        myDF: a pandas DF (it assumes that DF has a column called "knobs").

    Returns:
        The filter pandas DF showing the rows that depend on the selected knob, 'myKnob'.
    
    See madxp/examples/variablesExamples/000_run.py

    '''
    return myDF[myDF['knobs'].apply(lambda x: myKnob in x)]

def tableDF(table):
    '''
    Extract the pandas DF of a MAD-X table.
    
    Args:
        table: the MAD-X table handle 

    Returns:
        The pandas DF of a MAD-X table.
    
    See madxp/examples/variablesExamples/000_run.py
    '''
    myDF=pd.DataFrame(dict(table))
    myDF=myDF.set_index('name')
    myDF.index.name=''
    return myDF