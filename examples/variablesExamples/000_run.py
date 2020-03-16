# %%
from madxp import cpymadTool as mt
# %%
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
my_quad: quadrupole, l=1, k1:=myk1+h+b;

! sequence definition
my_sequence: sequence,l=10;
q1: my_quad, at=2;
endsequence;

! beam defintion
beam, sequence=my_sequence;
''')
# %% Extracting the DF of all the sequences
mt.sequencesDF(mad)
# NB: from the sequence DF, the sequence is not yet USED: 
# this implies that is not expanded (not drifts/checks). 
# Despite the fact the beam is defined to be attached to the sequence,
# no beam is attached to the sequence.  
# %% Extracting the DF of the beams attached to the sequences
mt.beamsDF(mad)
# The beams DF is empty
# %% The dependent variables DF
depDF=mt.dependentVariablesDF(mad)
depDF
# the dependent variable DF contains the numerical values, the expression, 
# the parameters and the knobs for each dependet variables. 
# The knobs of a given dependent variables, myVariable, are a set of 
# independent non-constant variables that control the value of myVariable. 
# NB: 
# - for 'b', 'pi' is not a knobs (since it is a constant). The same argument holds for 'c' 
# and its parameter 'e' (Euler number),
# - to determine the knobs, all parameters that are dependent variables (e.g., 'c' as parameter of 'b') 
# are 'resolved' in their independent variables.
# - despite 'h' is assigned via a deferred expression, it is not a dependent variables.
# - 'g' is not explicitly declared, then is an independent variable (with 0 values).
# - 'i' is declared as a constant, therefore is an independent variables.
# %% The independent variables DF
indepDF=mt.independentVariablesDF(mad)
indepDF
# As a complement to the dependent variable DF, there is an independent variable DF
# %% Constant variables
indepDF[indepDF['constant']]

# %%

mt.sequenceDF(mad, 'my_sequence')


# %%
import numpy as np
indepDF[np.logical_not(indepDF['constant'])]

# %%
mad.input('use, sequence=my_sequence;')
# %%
mt.beamsDF(mad)

# %%
indepDF=mt.independentVariablesDF(mad)
indepDF
# %%
mad.input('twiss, betx=1,bety=1;')
# %%
indepDF=mt.independentVariablesDF(mad)
indepDF

# %%
mt.sequenceDF(mad, 'my_sequence')

# %%
