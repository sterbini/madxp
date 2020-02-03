# %% Make markdown
import madxp
try:
    madxp.madx2md('macros_bb.madx','macros_bb.md')
except FileNotFoundError:
    import os
    os.chdir('/afs/cern.ch/work/s/sterbini/madxp/examples/macros_bb')
    madxp.madx2md('macros_bb.madx','macros_bb.md')
# %%
