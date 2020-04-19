# %%
# To install the package 
# pip install --upgrade --user git+https://github.com/sterbini/madxp.git
from madxp import cpymadTool as mt
from cpymad.madx import Madx
mad=Madx()
# %%
mad.input('''
! variables definition
a=1;
b:=c+3*a+sqrt(d)+pi;
c:=a+2+e; 
d:=2+f;
f=g;
h:=3;
const i=2;

! element definition
my_quad: quadrupole, l=1, k1:=(myk1+h+b)/1000;

! sequence definition
my_sequence: sequence,l=10, refer=exit;
q1: my_quad, at=3;
endsequence;

! beam defintion
beam, sequence=my_sequence;
''')
# %% Extracting the DF of all the sequences in MAD-X global workspace
mt.sequences_df(mad)
# NB: there is only one  sequence and has not yet be USEd: 
# this implies that is not expanded (not drifts/checks). 
# Despite the fact the beam is defined to be attached to the sequence,
# no beam is attached to the sequence (one needs to USE the sequence to attach it).  
# %% Extracting the DF of the beams attached to the sequences
mt.beams_df(mad)
# The beams DF is empty (see above).
# %% The constant and variables DFs
my_variable_dict=mt.variables_dict(mad)
my_variable_dict.keys()
# There are three DFs representing MAD-X global workspace
# %%
my_variable_dict['constant_df']
# NB: in addition to the MAD-X predefined constant, also 'i' (user defined constant) is present.
# %%
my_variable_dict['independent_variable_df']

# NB: 
# - 'g' is not explicitly declared, then is an independent variable (with 0 values)
# - despite 'h' is assigned via a deferred expression, it is an independent variables 
#   (trivial deferred expression)
# - the variable 'myk1' (in the definition of the 'my_quad' element) 
# is not present in the list of the independent variable (since the sequence is not used) 
# - the 'none' and 'twiss_tol' are MAD-X defined independent variables.
# %%
my_variable_dict['dependent_variable_df']

# the dependent variable DF contains the numerical values, the expression, 
# the parameters and the knobs for each dependent variables. 
# The knobs of a given dependent variables, myVariable, are a set of 
# independent variables that control the value of myVariable. 
# NB: 
# - for 'b', 'pi' is not a knobs (since it is a constant). The same argument holds for 'c' 
# and its parameter 'e' (Euler number),
# - to determine the knobs, all parameters that are dependent variables (e.g., 'c' as parameter of 'b') 
# are 'decomposed' in their independent variables.

# %% Now we can import the sequence DF 
# ('sequenceDF' method has not to be confused 'sequencesDF' method)
mt.sequence_df(mad, 'my_sequence')
# NB:
# - for each element you have the 'parameters' and the 'knobs' columns.
# - you can see 'myk1' has knob

# %% One can easily check the knobs of a given sequence
mt.knobs_df(mt.sequence_df(mad, 'my_sequence'))
# NB: one can do also 
# mt.knobsDF(myVariableDict['dependentVariableDF'])
# %% One can easily check the element of a sequence related to a specific knobs
mt.knob_df('myk1',mt.sequence_df(mad, 'my_sequence'))
# NB: one can do also 
# mt.knobDF('f', myVariableDict['dependentVariableDF'])
# %% Let us use the sequence
mad.input('use, sequence=my_sequence;')
# %% then we have 
mt.sequences_df(mad)
# %%
mt.beams_df(mad)
# NB: now the sequence is expanded and the beamDF method returns a non-empty DF.
# %%
# To ease the visualization of a given element you can run
mt.show_element('q1', mt.sequence_df(mad, 'my_sequence'))
# %%
my_variable_dict=mt.variables_dict(mad)
my_variable_dict['independent_variable_df']
# NB: now the 'myk1' appears in the pandas DF
# %% Let us twiss the sequence starting from an initial optics condition
mad.input('twiss, betx=1,bety=1;')
# %%
# We can list the tables of the MAD-X instance by using
list(mad.table)
# %% Then we can import the table by
mt.table_df(mad.table.twiss)
# %% Summary table
mt.summ_df(mad.table.summ)
# %% Interpolation 
import numpy as np
mt.table_interpolation_df(my_s_list=np.linspace(2,3,11), my_table=mt.table_df(mad.table.twiss))
# %%
mad.input('''
select, flag=interpolate, clear;
select, flag=interpolate, sequence=my_sequence,class=quadrupole, slice=10;
! more on 
twiss, betx=1,bety=1,table='with_interpolation';
''')
# %%
mt.table_df(mad.table.with_interpolation)
# %%
