## Simple make thin of Run3
The purpose of this file is make an example of python scripting in a mask.

## Contributors
**S. Fartoukh**
## Prepare the links
```fortran
option, -echo, -info, -warn;
system,"ln -fns /afs/cern.ch/eng/lhc/optics/runII/2018 db2018";
system,"ln -fns /afs/cern.ch/eng/lhc/optics/runIII/RunIII_dev dbrun3";

```
## Call the sequence     
```fortran
call,file="db2018/lhc_as-built.seq";
call,file="dbrun3/IR7-Run3seqedit.madx";

```
## Call optics file
```fortran
call,file="dbrun3/2021/PROTON/opticsfile.28";

epsxn=2.2e-6;
epsyn=2.2e-6;
beam,particle=proton,sequence=lhcb1,energy=NRJ,NPART=1.15E11,sige=4.5e-4,exn=epsxn,eyn=epsyn;
beam,particle=proton,sequence=lhcb2,energy=NRJ,NPART=1.15E11,sige=4.5e-4,exn=epsxn,eyn=epsyn,bv = -1;

use, sequence=lhcb1; twiss;
use, sequence=lhcb2; twiss;

slicefactor=4;
option rbarc=true;
makedipedgevalue=0;

```
## Python: settings
```python
# python code
if 1:
  madx.input(f'''
  slicefactor={pythonData["slicefactor"]};
  option rbarc={pythonData["rbarc"]};
  makedipedgevalue={pythonData["makedipedgevalue"]};''')
```
## Make B1 thin
```fortran
call, file = "db2018/toolkit/myslice.madx";
use,sequence=lhcb1;
if (makedipedgevalue==1){
makethin, sequence=lhcb1, style=teapot, makedipedge=true;
}
else{
makethin, sequence=lhcb1, style=teapot, makedipedge=false;
}
use,sequence=lhcb1;
twiss;


```
## Python: Test B1
```python
# python code
pythonData['B1summ']=madx.table.summ.dframe()
```
## Make B2 thin
```fortran
use,sequence=lhcb2;
if (makedipedgevalue==1){
makethin, sequence=lhcb2, style=teapot, makedipedge=true;
}
else{
makethin, sequence=lhcb2, style=teapot, makedipedge=false;
}
use,sequence=lhcb2;
twiss;

```
## Python: Test B2
```python
# python code
pythonData['B2summ']=madx.table.summ.dframe()
```
