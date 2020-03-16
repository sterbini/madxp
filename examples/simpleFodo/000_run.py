# %% Run it
import madxp;
try:
    madxp.madxp('input.madx')
except FileNotFoundError:
    import os
    os.chdir('/afs/cern.ch/work/s/sterbini/madxp/examples/simpleFodo')
    madxp.madxp('input.madx')


# %% Read the output.pkl
import pandas as pd
myDF=pd.read_pickle('output.pkl')
myDF

# %% Make markdown
madxp.madx2md('input.madx','input.md')


# %%
