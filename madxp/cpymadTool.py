import pandas as pd
import numpy as np
import cpymad
from cpymad.madx import Madx
import itertools
import gc

def sequences_df(mad):
    '''
    Extract the pandas DF with the list of the sequences defined in the MAD-X handle.
    
    Args:
        mad: The handle to MAD-X
    
    Returns:
        The pandas DF of the sequences. It can be and empty DF.
    
    See madxp/examples/variablesExamples/000_run.py

    '''
    sequences = mad.sequence
    seq_dict = {}
    for ii in sequences:
        seq_dict[ii] = {}
        if sequences[ii].has_beam:
            seq_dict[ii]['beam'] = True
        else:
            seq_dict[ii]['beam'] = False
        if sequences[ii].is_expanded:
            seq_dict[ii]['expanded'] = True
        else:
            seq_dict[ii]['expanded'] = False
    return pd.DataFrame(seq_dict).transpose()

def beams_df(mad):
    '''
    Extract the pandas DF with the beams associated to the sequences defined in the MAD-X handle.
    
    Args:
        mad: The handle to MAD-X
    
    Returns:
        The pandas DF of the beams. It can be and empty DF.

    See madxp/examples/variablesExamples/000_run.py
    '''
    df_list = []
    sequences = mad.sequence
    for ii in sequences:
        try:
            df_list.append(pd.DataFrame([dict(sequences[ii].beam)], index=[ii]))
        except:
            print(f'The sequence {ii} has no beam attached.')
    if len(df_list) > 0:
        return pd.concat(df_list)
    else:
        return pd.DataFrame()

def _extract_parameters(my_string):
    '''
    Extract all the parameters of a MAD-X expression.

    Args:
        my_string: The string of the MAD-X expression to parse.
    
    Returns:
        The list of the parameters present in the MAD-X expression.

    '''
    if type(my_string)=='NoneType' or my_string==None or my_string=='None' or my_string=='[None]':
        return []
    else:
        for i in [
        '*','-','/','+','(',')','[', ']',',','\'','None']:
            my_string=my_string.replace(i,' ')
        my_list=my_string.split(' ')
        my_list=list(np.unique(my_list))
        if '' in my_list:
            my_list.remove('')
        if type(my_list)=='NoneType':
            my_list=[]
        for i in my_list.copy():
            if i.isdigit() or i[0].isdigit():
                my_list.remove(i)
        my_list=list(set(my_list)-
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
        return my_list 

def variables_dict(mad):
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
    my_dict={}
    aux=_independent_variables_df(mad)
    import numpy as np
    independentVariablesDF=aux[np.logical_not(aux['constant'])].copy()
    del independentVariablesDF['constant']
    constantDF=aux[aux['constant']].copy()
    del constantDF['constant']
    my_dict['constantDF']=constantDF
    my_dict['independentVariableDF']=independentVariablesDF
    my_dict['dependentVariableDF']=_dependent_variables_df(mad)
    
    return my_dict

def _dependent_variables_df(mad):
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
    my_dict={}
    for i in list(mad.globals):
        aux=_extract_parameters(str(mad._libmadx.get_var(i)))
        if aux!=[]:
            my_dict[i]={}
            my_dict[i]['parameters']=list(np.unique(aux))
    
    myhash=hash(str(my_dict))
    while True:
        for i in my_dict:
            aux=[]
            for j in my_dict[i]['parameters']:
                try:
                    aux=aux+my_dict[j]['parameters']
                except:
                    aux=aux+[j]
            my_dict[i]['knobs']=list(np.unique(aux))
        if myhash==hash(str(my_dict)):
            break
        else:
            myhash=hash(str(my_dict))
    
    for i in my_dict:
        for j in my_dict[i]['knobs'].copy():
            if mad._libmadx.get_var_type(j)==0:
                my_dict[i]['knobs'].remove(j)
        my_dict[i]['expression']=mad._libmadx.get_var(i)
        my_dict[i]['value']=mad.globals[i]
    
    if len(my_dict)>0:
        return pd.DataFrame(my_dict).transpose()[['value','expression','parameters','knobs']].sort_index()
    else:
        return pd.DataFrame()

def _independent_variables_df(mad):
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

    dep_df=_dependent_variables_df(mad)
    #if len(dep_df)>0:
    #    aux=list(dep_df['knobs'].values)
    #    aux=list(itertools.chain.from_iterable(aux))
    #fundamentalSet=set(np.unique(aux))
    independent_variable_set=set(mad.globals)-set(dep_df.index)
    my_dict={}
    for i in independent_variable_set:
        my_dict[i]={}
        if mad._libmadx.get_var_type(i)==0:
            my_dict[i]['constant']=True
            # my_dict[i]['knob']=False
        else:
            my_dict[i]['constant']=False
            # if i in fundamentalSet:
            #    my_dict[i]['knob']=True
            # else:
            #    my_dict[i]['knob']=False
        my_dict[i]['value']=mad.globals[i]
    
    return pd.DataFrame(my_dict).transpose()[['value','constant']].sort_index()

def _knobs_from_parameters(parameters, indep_df, dep_df):
    '''
    Extract the list of knobs from a list of parameters.
    
    Args:
        parameters: list of parameters
        indep_df: independent variable DF
        dep_df: dependent variable DF

    Returns:
        The list of knobs corresponding to the list of parameters.
    
    See madxp/examples/variablesExamples/000_run.py
    '''
    my_knobs=[]
    for i in parameters:
        if i in indep_df.index:
            if not indep_df.loc[i]['constant']:
                my_knobs.append([i])
        else:
            try:
                my_knobs.append(dep_df.loc[i]['knobs'])
            except:
                print(f'Variable {i} not defined! Cosidered as a knob.')
                my_knobs.append([i])
    return list(itertools.chain.from_iterable(my_knobs))

def sequence_df(mad,sequenceName):
    '''
    Extract a pandas DF of the list of the elements and all their attributes for a given sequence.
    
    Args:
        mad: the MAD-X handle
        sequenceName: the sequence name

    Returns:
        The list of knobs corresponding to the list of parameters.
    
    See madxp/examples/variablesExamples/000_run.py
    '''
    my_list=[]
    sequences=mad.sequence
    my_sequence=sequences[sequenceName]
    indep_df=_independent_variables_df(mad)
    dep_df=_dependent_variables_df(mad)

    for my_index, _ in enumerate(my_sequence.elements):
        aux=mad._libmadx.get_element(sequenceName,my_index)
        my_dict={}
        my_dict['parameters']=[]
        for i in aux:
            my_dict[i]=aux[i]
        del my_dict['data']

        for i in aux['data']:
            my_dict[i]=str(aux['data'][i])
            if isinstance(aux['data'][i], cpymad.types.Parameter):
                my_dict[i+' value']=aux['data'][i].value
                my_dict['parameters']+=_extract_parameters(str(aux['data'][i].expr))
        my_dict['parameters']=np.unique(my_dict['parameters'])
        my_list.append(my_dict)
    my_df=pd.DataFrame(my_list)
    my_df=my_df.set_index('name')
    my_df.index.name=''
    my_df['knobs']=my_df['parameters'].apply(lambda x: _knobs_from_parameters(x,indep_df,dep_df))
    first_columns=['position','parent','base_type','length','parameters','knobs']
    last_columns=list(set(my_df.columns)-set(first_columns))
    last_columns.sort()
    return my_df[first_columns+last_columns]

def knobs_df(my_df):
    '''
    Extract the knob list of a pandas DF (it assumes that DF has a column called "knobs")
    and contanting lists
    
    Args:
        my_df: a pandas DF (it assumes that DF has a column called "knobs").

    Returns:
        A data frame of knobs.
    
    See madxp/examples/variablesExamples/000_run.py

    '''
    import itertools
    import numpy as np
    aux= list(my_df['knobs'].values)
    aux= list(np.unique(list(itertools.chain.from_iterable(aux))))
    my_dict={}
    for i in aux:
        my_dict[i]={}
        filter_df=knob_df(i, my_df)
        my_dict[i]['multeplicity']=len(filter_df)
        my_dict[i]['dependences']=list(filter_df.index)
    return pd.DataFrame(my_dict).transpose().sort_values('multeplicity', ascending=False)


def knob_df(my_knob,my_df):
    '''
    Filter the pandas DF, 'my_df', returning only the rows that depend on the selected knob, 'my_knob'.
    
    Args:
        my_knob: the name of the knob to filter.
        my_df: a pandas DF (it assumes that DF has a column called "knobs").

    Returns:
        The filter pandas DF showing the rows that depend on the selected knob, 'my_knob'.
    
    See madxp/examples/variablesExamples/000_run.py

    '''
    return my_df[my_df['knobs'].apply(lambda x: my_knob in x)]

def table_df(table):
    '''
    Extract the pandas DF of a MAD-X table.
    
    Args:
        table: the MAD-X table handle 

    Returns:
        The pandas DF of a MAD-X table.
    
    See madxp/examples/variablesExamples/000_run.py
    '''
    my_df=pd.DataFrame(dict(table))
    my_df=my_df.set_index('name', drop = False)
    my_df.index.name=''
    return my_df

def twiss_df(table):
    '''
    Extract the pandas DF of a MAD-X twiss table.
    
    Args:
        table: the MAD-X table handle 

    Returns:
        The pandas DF of a MAD-X table.
    
    See madxp/examples/variablesExamples/000_run.py
    '''
    my_df=pd.DataFrame(dict(table))
    my_df=my_df.set_index('name', drop = False)
    my_df.index.name=''
    return my_df

def summ_df(table):
    '''
    Extract the pandas DF of a MAD-X summary table.
    
    Args:
        table: the MAD-X table handle 

    Returns:
        The pandas DF of a MAD-X table.
    
    See madxp/examples/variablesExamples/000_run.py
    '''
    my_df=pd.DataFrame(dict(table))
    my_df.index=[table._name]
    return my_df

def show_element(element_name, sequence_df):
    '''
    Print and return the row of the 'sequence_df' corresponding to a given 'element_name'.
    
    Args:
        element_name: the name

    Returns:
        A single-row DF corresponding to the 'element_name' of 'sequence_df'.
    
    See madxp/examples/variablesExamples/000_run.py
    '''
    aux=sequence_df.loc[[element_name]].dropna(axis=1)
    print(aux.transpose().to_string())
    return(aux)


# %% Interpolation 

def table_interpolation_df(my_s_list, my_table):
    '''
    Thanks to H. Bartosik for sharing his code and for the discussion.
    
    This function will interpolate in a list of s-positions the MAD-X table passed as argument.
    This table has to be a full MAD-X twiss table (e.g., 'e1', 'fint',... columns have to be present).
    For each element in my_s_list there will be a twiss-command of a short sequence. 
    This can be time consuming for long lists. It this case please look to MAD-X interpolate command at
    http://mad.web.cern.ch/mad/webguide/manual.html#Ch19.S10.

    The rationale is to make a new instance of MAD-X in the body of the funciton and to build-and-twiss mini sequences.
    The twiss will be performed with given initial values http://mad.web.cern.ch/mad/webguide/manual.html#Ch19.S3.

    Args:
        my_s_list: list of s-position to be evaluated
        my_table: a MAD-X twiss table.

    Returns:
        The pandas DF with the interpolated values. 
    
    See madxp/examples/variablesExamples/000_run.py

    '''
    # my_s_list=[2.8], my_table=mt.table_df(mad.table.twiss)
    my_list=[]
    madx=Madx(stdout=False)

    for my_s in my_s_list:
        try:
            start_condition=my_table[my_table['s']<my_s].index[-1]
        except:
            start_condition=my_table.index[0]
        try:
            my_element=my_table[my_table['s']>=my_s].index[0]
        except:
            my_element=my_table.index[-1]
        
        my_element_row= my_table.loc[my_element]
        start_condition_row= my_table.loc[start_condition]
        if my_element_row.s==my_s:
            interpolation=pd.DataFrame(my_element_row).transpose()
        else:
            assert my_element_row.l>0 # The elements need to be thick
            if my_element_row.keyword in ['quadrupole',
                                        'drift', 
                                        'sextupole', 
                                        'octupole', 
                                        'placeholder',
                                        'hmonitor',
                                        'vmonitor',
                                        'monitor',
                                        ]:
                my_string=f'''
                    my_special_element: quadrupole,
                    l= {my_s-start_condition_row.s},
                    k1={my_element_row.k1l/my_element_row.l}, 
                    k1s={my_element_row.k1sl/my_element_row.l},
                    tilt={my_element_row.tilt};
                '''
            elif my_element_row.keyword in ['sbend']:
                # 
                my_string=f'''
                    my_special_element: sbend,
                    l={my_s-start_condition_row.s},
                    angle={my_element_row.angle/my_element_row.l*{my_s-start_condition_row.s}},
                    tilt={my_element_row.tilt},
                    k1={my_element_row.k1l/my_element_row.l},
                    e1={my_element_row.e1},
                    fint={my_element_row.fint},
                    fintx=0,
                    hgap={my_element_row.hgap},
                    k1s={my_element_row.k1sl/my_element_row.l},
                    h1={my_element_row.h1},
                    h2=0,
                    kill_exi_fringe=0;
                '''
            elif my_element_row.keyword in ['rbend']:
                my_string=f'''
                    option, rbarc=false;
                    my_special_element: rbend,
                    l= {my_s-start_condition_row.s},
                    angle={my_element_row.angle/my_element_row.l*{my_s-start_condition_row.s}},
                    k1={my_element_row.k1l/my_element_row.l},
                    e1={my_element_row.e1},
                    fint={my_element_row.fint},
                    fintx=0,
                    hgap={my_element_row.hgap},
                    k1s={my_element_row.k1sl/my_element_row.l},
                    h1={my_element_row.h1},
                    h2=0,
                    kill_exi_fringe=0;
                '''
            elif my_element_row.keyword in ['matrix', 
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
                print(f'The element keyword {my_element_row.keyword} has not been implemented.')
                print(f'Consider to remove the interpolating position at {my_s} m.')
                return

            my_string =  my_string + f''' 
                my_special_sequence: sequence, l={my_s-start_condition_row.s}, refer=entry;
                at_{my_s:}:my_special_element, at=0;
                endsequence;
                
                beam, sequence=my_special_sequence; ! we assume normalized elements
                use, sequence=my_special_sequence;
                
                twiss, 
                betx  = {start_condition_row.betx}, 
                alfx  = {start_condition_row.alfx}, 
                mux   = {start_condition_row.mux}, 
                bety  = {start_condition_row.bety}, 
                alfy  = {start_condition_row.alfy},
                muy   = {start_condition_row.muy}, 
                dx    = {start_condition_row.dx},
                dpx   = {start_condition_row.dpx},
                dy    = {start_condition_row.dy},
                dpy   = {start_condition_row.dpy},
                x     = {start_condition_row.x},
                px    = {start_condition_row.px},
                y     = {start_condition_row.y},
                py    = {start_condition_row.py},
                t     = {start_condition_row.t},
                pt    = {start_condition_row.pt},
                wx    = {start_condition_row.wx},
                phix  = {start_condition_row.phix},
                dmux  = {start_condition_row.dmux},
                wy    = {start_condition_row.wy},
                phiy  = {start_condition_row.phiy},
                dmuy  = {start_condition_row.dmuy},
                ddx   = {start_condition_row.ddx},
                ddy   = {start_condition_row.ddy},
                ddpx  = {start_condition_row.ddpx},
                ddpy  = {start_condition_row.ddpy},
                r11   = {start_condition_row.r11},
                r12   = {start_condition_row.r12},
                r21   = {start_condition_row.r21},
                r22   = {start_condition_row.r22},
                table=special_twiss;
                '''
            madx.input(my_string)
            madx.input('delete, sequence=my_special_sequence;my_special_element=0;')
            interpolation=table_df(madx.table.special_twiss).iloc[[1]]
            interpolation.keyword='interpolation'
            interpolation.s=my_s
        my_list.append(interpolation)
        gc.collect()
    return pd.concat(my_list)

def python_data_to_mad(mad, python_data, verbose=False):
    '''
    It assigns a dictionary to a MAD-X handle.
    '''
    for i in python_data:
        if i[0]!='_': 
            if isinstance(python_data[i],float) or isinstance(python_data[i],int):
                mad.input(f'{i}={python_data[i]};')
            else:
                if verbose:
                    print(f'{i} was not assigned to the MAD-X instance.')
        else:
            if verbose:
                print(f'{i} was not assigned to the MAD-X instance.')


def mad_to_python_data(mad, python_data, verbose=False):
    '''
    It assigns the variables present in python_data from the values of the
    MAD-X workspace.
    '''
    for i in python_data:
        try:
            a=mad.globals[i]
            python_data[i]=a
        except:
            if verbose:
                print(f'{i} not found in MAD-X instance.')