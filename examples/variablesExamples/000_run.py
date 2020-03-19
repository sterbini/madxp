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
mt.sequencesDF(mad)
# NB: there is only one  sequence and has not yet be USEd: 
# this implies that is not expanded (not drifts/checks). 
# Despite the fact the beam is defined to be attached to the sequence,
# no beam is attached to the sequence (one needs to USE the sequence to attach it).  
# %% Extracting the DF of the beams attached to the sequences
mt.beamsDF(mad)
# The beams DF is empty (see above).
# %% The constant and variables DFs
myVariableDict=mt.variablesDict(mad)
myVariableDict.keys()
# There are three DFs representing MAD-X global workspace
# %%
display(myVariableDict['constantDF'])
# NB: in addition to the MAD-X predefined constant, also 'i' (user defined constant) is present.
# %%
display(myVariableDict['independentVariableDF'])

# NB: 
# - 'g' is not explicitly declared, then is an independent variable (with 0 values)
# - despite 'h' is assigned via a deferred expression, it is an independent variables 
#   (trivial deferred expression)
# - the variable 'myk1' (in the definition of the 'my_quad' element) 
# is not present in the list of the independent variable (since the sequence is not used) 
# - the 'none' and 'twiss_tol' are MAD-X defined independent variables.
# %%
display(myVariableDict['dependentVariableDF'])

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
mt.sequenceDF(mad, 'my_sequence')
# NB:
# - for each element you have the 'parameters' and the 'knobs' columns.
# - you can see 'myk1' has knob

# %% One can easily check the knobs of a given sequence
mt.knobsDF(mt.sequenceDF(mad, 'my_sequence'))
# NB: one can do also 
# mt.knobsDF(myVariableDict['dependentVariableDF'])
# %% One can easily check the element of a sequence related to a specific knobs
mt.knobDF('myk1',mt.sequenceDF(mad, 'my_sequence'))
# NB: one can do also 
# mt.knobDF('f', myVariableDict['dependentVariableDF'])
# %% Let us use the sequence
mad.input('use, sequence=my_sequence;')
# %% then we have 
display(mt.sequencesDF(mad))
display(mt.beamsDF(mad))
# NB: now the sequence is expanded and the beamDF method returns a non-empty DF.
# %%
# To ease the visualization of a given element you can run
mt.showElement('q1', mt.sequenceDF(mad, 'my_sequence'))
# %%
myVariableDict=mt.variablesDict(mad)
myVariableDict['independentVariableDF']
# NB: now the 'myk1' appears in the pandas DF
# %% Let us twiss the sequence starting from an initial optics condition
mad.input('twiss, betx=1,bety=1;')
# %%
# We can list the tables of the MAD-X instance by using
list(mad.table)
# %% Then we can import the table by
mt.tableDF(mad.table.twiss)
# %% Interpolation 

mt.tableInterpolationDF(myS_List=[2.8], myTable=mt.tableDF(mad.table.twiss))

# %%
