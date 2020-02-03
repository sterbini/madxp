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
myDF=pd.read_pickle('/afs/cern.ch/work/s/sterbini/madxp/examples/maskExample/output.pkl')
myDF



# %% Make markdown
madxp.madx2md('mask.madx','mask.md')

# %%
plt.figure(figsize=[20,10])
plt.plot(myDF['on_x1'])
plt.xticks(rotation='vertical');
plt.ylabel('on_x1')
# %%
plt.figure(figsize=[20,10])
plt.semilogy(myDF['execution time [s]'])
plt.xticks(rotation='vertical');
plt.ylabel('execution time [s]')

# %%
