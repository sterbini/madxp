'''
A simple use augmented MADX syntax.
import madxp # do "pip install --user git+https://github.com/sterbini/madxp.git" to install
'''

# %%
import pandas as pd
import numpy as np
import sys

def madx2df(inputFile):
    with open(inputFile) as fid:
            mask_content = fid.read()
    # I am assuming that the start of the file is '! ## '
    assert(mask_content[0:5]=="! ## ")
    # We split the mask
    aux=mask_content.split("! ## ") 
    title=[]
    body=[]
    for i in aux:
        title.append(i.split('\n')[0])   
        aux="".join([a+'\n' for a in i.split('\n')[1:]])
        body.append(aux[0:-1]) 
    title=title[1:]
    body=body[1:]
    # built a pandas df
    aux=pd.DataFrame(body,index=title, columns=['Code string'])
    aux['Code subsections']=aux['Code string'].apply(splitCodeString)
    return aux

def splitCodeString(myString):
    ''' 
    It takes a string and return a list of tuples.
    '''
    subSectionBefore='none'
    codeSubSections=[]
    for line in myString.split('\n'):    
        if line.strip().startswith('!'):
            line=line.strip()[1:]
            if subSectionBefore=='markdown':
                codeSubSections[-1]['markdown']=codeSubSections[-1]['markdown']+'\n'+line
            else:
                codeSubSections.append({'markdown':line})
                subSectionBefore='markdown'
        elif line.strip().startswith('//'):
            line=line.strip()[3:]
            if subSectionBefore=='python':
                codeSubSections[-1]['python']=codeSubSections[-1]['python']+'\n'+line
            else:
                codeSubSections.append({'python':line})
                subSectionBefore='python'
        else:
            if subSectionBefore=='madx':
                codeSubSections[-1]['madx']=codeSubSections[-1]['madx']+'\n'+line
            else:
                codeSubSections.append({'madx':line})
                subSectionBefore='madx'
    return codeSubSections

def madx2md(inputFile, outputFile):
    df= madx2df(inputFile)
    myString=''
    for section in df.iterrows():   
        print(section[0])        
        myString=myString+'## ' +section[0]+ '\n'
        codeSubSections=section[1]['Code subsections']
        for code in codeSubSections:
            myType=list(code.keys())[0]
            if myType=='markdown':
                myString=myString+code['markdown']+ '\n'
            elif myType=='python':
                myString=myString+ '```python\n# python code\n' + code['python'] + '\n```\n'
            elif myType=='madx':
                if code['madx'][-1]=='\n':
                    myString=myString+ '```fortran\n' + code['madx'] + '```\n'
                else:
                    myString=myString+ '```fortran\n' + code['madx'] + '\n```\n'
            else:
                assert(0)
    with open(outputFile, 'w') as fid:
        fid.write(myString)

def df2madx(myDF):
    myString=''
    for block in myDF.iterrows():
        print(block[0])
        myString=myString+ '! ## ' +block[0]+ '\n' + block[1]['Code string']
    return myString

def df2run(myDF, command_log=None):
    import time
    from cpymad.madx import Madx
    if command_log==None:
        madx = Madx()
    else:
        madx = Madx(command_log=command_log)
    myGlobals=[]
    for section in myDF.iterrows():
        print(section[0])
        start_time = time.time()
        codeSubSections=section[1]['Code subsections']
        with madx.batch():
            for code in codeSubSections:
                myType=list(code.keys())[0]
                if myType=='markdown':
                    pass
                elif myType=='python':
                    exec(code['python'])
                elif myType=='madx':
                    madx.input(code['madx'])
                else:
                    assert(0)
        execution_time_s=time.time()-start_time
        myDict={}
        myDict=dict(madx.globals)
        myDict['execution time [s]']=execution_time_s
        myGlobals.append(myDict)
    profileDF=pd.DataFrame(myGlobals, index=myDF.index)
    return profileDF

def madxp(inputFile, outputDF=None): 
    aux=df2run(madx2df(inputFile))
    if outputDF!=None:
        aux.to_pickle(outputDF);
        print('Profiling DF saved.')
