import pandas as pd
import numpy as np
import cpymad
from cpymad.madx import Madx
import itertools
import gc

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

def knobsDF(myDF):
    '''
    Extract the knob list of a pandas DF (it assumes that DF has a column called "knobs")
    and contanting lists
    
    Args:
        myDF: a pandas DF (it assumes that DF has a column called "knobs").

    Returns:
        A data frame of knobs.
    
    See madxp/examples/variablesExamples/000_run.py

    '''
    import itertools
    import numpy as np
    aux= list(myDF['knobs'].values)
    aux= list(np.unique(list(itertools.chain.from_iterable(aux))))
    myDict={}
    for i in aux:
        myDict[i]={}
        filterDF=knobDF(i, myDF)
        myDict[i]['multeplicity']=len(filterDF)
        myDict[i]['dependences']=list(filterDF.index)
    return pd.DataFrame(myDict).transpose().sort_values('multeplicity', ascending=False)


def knobDF(myKnob,myDF):
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

def showElement(elementName, sequenceDF):
    '''
    Print and return the row of the 'sequenceDF' corresponding to a given 'elementName'.
    
    Args:
        elementName: the name

    Returns:
        A single-row DF corresponding to the 'elementName' of 'sequenceDF'.
    
    See madxp/examples/variablesExamples/000_run.py
    '''
    aux=sequenceDF.loc[[elementName]].dropna(axis=1)
    print(aux.transpose().to_string())
    return(aux)


# %% Interpolation 

def tableInterpolationDF(myS_List, myTable):
    '''
    Thanks to H. Bartosik for sharing his code and for the discussion.
    This funcntion will interpolate in a list of s-positions the MAD-X table passed as argument.
    This table has to be a full MAD-X twiss table (e.g., 'e1', 'fint',... columns have to be present).
    For each element in myS_List there will be a twiss-command (of a short sequence). 
    This can be time consuming for long list. It this case please look to MAD-X interpolate command at
    http://mad.web.cern.ch/mad/webguide/manual.html#Ch19.S10.

    The rationale is to make a new instance of MAD-X in the body of the funciton and to build-and-twiss mini sequences.
    The twiss will be performed with given initial values http://mad.web.cern.ch/mad/webguide/manual.html#Ch19.S10.

    Args:
        myS_List: list of s-position to be evaluated
        myTable: a MAD-X twiss table.

    Returns:
        The pandas DF with the interpolated values. 
    
    See madxp/examples/variablesExamples/000_run.py

    '''
    # myS_List=[2.8], myTable=mt.tableDF(mad.table.twiss)
    myList=[]
    madx=Madx(stdout=False)

    for myS in myS_List:
        try:
            startCondition=myTable[myTable['s']<myS].index[-1]
        except:
            startCondition=myTable.index[0]
        try:
            myElement=myTable[myTable['s']>=myS].index[0]
        except:
            myElement=myTable.index[-1]
        
        myStruct={}
        myElementRow= myTable.loc[myElement]
        startConditionRow= myTable.loc[startCondition]
        if myElementRow.s==myS:
            interpolation=pd.DataFrame(myElementRow).transpose()
        else:
            assert myElementRow.l>0 # The elements need to be thick
            if myElementRow.keyword in ['quadrupole',
                                        'drift', 
                                        'sextupole', 
                                        'octupole', 
                                        'placeholder',
                                        'hmonitor',
                                        'vmonitor',
                                        'monitor',
                                        ]:
                myString=f'''
                    my_special_element: quadrupole,
                    l= {myS-startConditionRow.s},
                    k1={myElementRow.k1l/myElementRow.l}, 
                    k1s={myElementRow.k1sl/myElementRow.l},
                    tilt={myElementRow.tilt};
                '''
            elif myElementRow.keyword in ['sbend']:
                # 
                myString=f'''
                    my_special_element: sbend,
                    l={myS-startConditionRow.s},
                    angle={myElementRow.angle/myElementRow.l*{myS-startConditionRow.s}},
                    tilt={myElementRow.tilt},
                    k1={myElementRow.k1l/myElementRow.l},
                    e1={myElementRow.e1},
                    fint={myElementRow.fint},
                    fintx=0,
                    hgap={myElementRow.hgap},
                    k1s={myElementRow.k1sl/myElementRow.l},
                    h1={myElementRow.h1},
                    h2=0,
                    kill_exi_fringe=0;
                '''
            elif myElementRow.keyword in ['rbend']:
                myString=f'''
                    option, rbarc=false;
                    my_special_element: rbend,
                    l= {myS-startConditionRow.s},
                    angle={myElementRow.angle/myElementRow.l*{myS-startConditionRow.s}},
                    k1={myElementRow.k1l/myElementRow.l},
                    e1={myElementRow.e1},
                    fint={myElementRow.fint},
                    fintx=0,
                    hgap={myElementRow.hgap},
                    k1s={myElementRow.k1sl/myElementRow.l},
                    h1={myElementRow.h1},
                    h2=0,
                    kill_exi_fringe=0;
                '''
            elif myElementRow.keyword in ['matrix', 
                                          'collimator',
                                          'elseparator',
                                          'hacdipole',
                                          'vacdipole',
                                          'twcavity',
                                          'tkicker',
                                          'hkicker',
                                          'vkicker',
                                          'kicker',
                                          'solenoid'
                                          'rfcavity']:
                print(f'The element keyword {myElementRow.keyword} has not been implemented.')
                print(f'Consider to remove the interpolating position at {myS} m.')
                return

            myString =  myString + f''' 
                my_special_sequence: sequence, l={myS-startConditionRow.s}, refer=entry;
                at_{myS:}:my_special_element, at=0;
                endsequence;
                
                beam, sequence=my_special_sequence; ! we assume normalized elements
                use, sequence=my_special_sequence;
                
                twiss, 
                betx  = {startConditionRow.betx}, 
                alfx  = {startConditionRow.alfx}, 
                mux   = {startConditionRow.mux}, 
                bety  = {startConditionRow.bety}, 
                alfy  = {startConditionRow.alfy},
                muy   = {startConditionRow.muy}, 
                dx    = {startConditionRow.dx},
                dpx   = {startConditionRow.dpx},
                dy    = {startConditionRow.dy},
                dpy   = {startConditionRow.dpy},
                x     = {startConditionRow.x},
                px    = {startConditionRow.px},
                y     = {startConditionRow.y},
                py    = {startConditionRow.py},
                t     = {startConditionRow.t},
                pt    = {startConditionRow.pt},
                wx    = {startConditionRow.wx},
                phix  = {startConditionRow.phix},
                dmux  = {startConditionRow.dmux},
                wy    = {startConditionRow.wy},
                phiy  = {startConditionRow.phiy},
                dmuy  = {startConditionRow.dmuy},
                ddx   = {startConditionRow.ddx},
                ddy   = {startConditionRow.ddy},
                ddpx  = {startConditionRow.ddpx},
                ddpy  = {startConditionRow.ddpy},
                r11   = {startConditionRow.r11},
                r12   = {startConditionRow.r12},
                r21   = {startConditionRow.r21},
                r22   = {startConditionRow.r22},
                table=special_twiss;
                '''
            madx.input(myString)
            madx.input('delete, sequence=my_special_sequence;my_special_element=0;')
            interpolation=tableDF(madx.table.special_twiss).iloc[[1]]
            interpolation.keyword='interpolation'
            interpolation.s=myS
        myList.append(interpolation)
        gc.collect()
    return pd.concat(myList)