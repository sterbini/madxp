# %% Run it
import madxp; 
try: 
    madxp.madxp('mask.madx', verbose=False)
except :
    import os
    os.chdir('/afs/cern.ch/work/s/sterbini/madxp/examples/maskExample')# %% Read the output.pkl
    madxp.madxp('mask.madx', verbose=False)

# %%
import pandas as pd
myDF=pd.read_pickle('output.pkl')
myDF

# %% Make markdown
madxp.madx2md('mask.madx','mask.md')

# %%
