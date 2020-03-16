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
# %% The constant and variables DFs

myVariableDict=mt.variablesDict(mad)
myVariableDict.keys()

# %%
display(myVariableDict['constantDF'])

# %%
display(myVariableDict['independentVariableDF'])

# NB: 
# - the variable 'myk1' (in the definition of the 'my_quad' element) 
# is not present in the list of the independent variable 
# (since the sequence is not used) 
# - 'i' appears as a constantI think
# %%
display(myVariableDict['dependentVariableDF'])

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


# %% Now we can import the sequence DF 
# ('sequenceDF' has not to be confused 'sequencesDF')
mt.sequenceDF(mad, 'my_sequence')
# NB:
# - for each element you have the 'parameters' and the 'knobs' columns.
# - you can see 'myk1' has knob

# %%
listOfKnobs(mt.sequenceDF(mad, 'my_sequence'))

# %%
selectKnobsDepedences('myk1',mt.sequenceDF(mad, 'my_sequence'))

# %%
mad.input('use, sequence=my_sequence;')
# %%
mt.beamsDF(mad)

# %%
myVariableDict=mt.variablesDict(mad)
myVariableDict['independentVariableDF']
# %%
mad.input('twiss, betx=1,bety=1;')
# %%
myVariableDict=mt.variablesDict(mad)
myVariableDict['independentVariableDF']
