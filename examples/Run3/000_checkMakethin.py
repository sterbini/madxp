# %%
import madxp
import cl2pd
import pandas as pd
import numpy as np
import copy # deepcopy of dictionaries
import gc  # garbage collector to force to free memory

import matplotlib.pyplot as plt
%matplotlib inline
# %%
myList=[]
pythonData={}
slicefactorRange=np.arange(2,9,2)

pythonData['rbarc']='true'
for makedipedgevalue in [0,1]:
    pythonData['makedipedgevalue']=makedipedgevalue
    for slicefactor in slicefactorRange:
        print(slicefactor)
        pythonData['slicefactor']=slicefactor
        try:
            madxp.madxp('input_thin.madx', pythonData=pythonData)
        except FileNotFoundError:
            import os
            os.chdir('/afs/cern.ch/work/s/sterbini/madxp/examples/Run3')
            madxp.madxp('input_thin.madx', pythonData=pythonData)
        myList.append(copy.deepcopy(pythonData)) # to append the pythonData dictionary
        gc.collect() # to free memory
# %%
myDF=pd.DataFrame(myList)
myDF['q1 of B1']=myDF['B1summ'].apply(lambda x: x['q1'].values[0])
myDF['q2 of B1']=myDF['B1summ'].apply(lambda x: x['q2'].values[0])
myDF['q1 of B2']=myDF['B2summ'].apply(lambda x: x['q1'].values[0])
myDF['q2 of B2']=myDF['B2summ'].apply(lambda x: x['q2'].values[0])

# %%
aux=myDF[myDF['makedipedgevalue']==0]
plt.plot(aux['slicefactor'], aux['q1 of B1']-62, 'o-b', label='Q1, makedipedge=False')
plt.plot(aux['slicefactor'], aux['q2 of B1']-60, 's-r', label='Q2, makedipedge=False')
aux=myDF[myDF['makedipedgevalue']==1]
plt.plot(aux['slicefactor'], aux['q1 of B1']-62, 'o:b', label='Q1, makedipedge=True')
plt.plot(aux['slicefactor'], aux['q2 of B1']-60, 's:r', label='Q2, makedipedge=True')
plt.plot(aux['slicefactor'],.31+0*aux['slicefactor'],'b-.', label='Q1 reference')
plt.plot(aux['slicefactor'],.32+0*aux['slicefactor'],'r-.', label='Q2 reference')
plt.xlabel('slicefactor')
plt.ylabel('fractional tunes')
plt.grid(True)
plt.legend(loc='best')
# %%
madxp.madx2md('input_thin.madx','input_thin.md')
# %%
