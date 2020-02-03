# madxp
A simple package for *augmented* MADX syntax using python and markdown.

We propose an *augmented* MADX syntax with a three-fold objective:
1. to stay fully compatible with the standard MADX syntax and mask/macro file structure,
2. to produce agile documentation from MADX files using markdown approach, with the principle that the documentation is *in* the code (in doing so improving the maintanability of the documentation),
3. to run python within the MADX code to improving debugging capability (and scripting flexibility).

We will show how to install the package and a simple example to discuss the conventions adopted.


## Install the package
You can install the package, for instance on the SWAN terminal (www.swan.cern.ch), using:
```
pip install --user git+https://github.com/sterbini/madxp.git
```
or to upgrade it
```
pip install --upgrade --user git+https://github.com/sterbini/madxp.git
```
or to upgrade a branch of the project
```
pip install --upgrade --user git+https://github.com/sterbini/madxp.git@branch_name
```

## Simple example
Imagine to have the following code
```
!## Introduction
 !In this example we are going to solve a simple FODO lattice.

!## Define the elements
!Define the geometrical parameters
 quadrupoleLength=5;
 cellLength=100;

!## Define the gradient
 myK=2.8/cellLength/quadrupoleLength;

!## Define the quadrupoles
 QF: quadrupole, L=quadrupoleLength, K1=myK;
 QD: quadrupole, L=quadrupoleLength, K1=-myK;

!## Define the sequence
 myCell:sequence, refer=entry, L=cellLength;
 q1: QF, at=0;
 q2: QD, at=cellLength/2;
 endsequence;

!## Define the beam
 beam, particle=proton, energy=7000;

!## Twiss the sequence
 use, sequence=myCell;
 twiss, file="myFirstTwiss.txt";
 plot, haxis=s, vaxis=betx,bety,dx,colour=100, title="First plot";
 value, myK;

!## Python data extraction
 //pythonDictionary['twiss']=madx.table.twiss.dframe()

!## End
 stop;
```

We use MADX comments flexibility to introduce two **special comments**:
- with **!** we start a markdown line
- with **//** we start a python instruction (be careful with indentation)

The input file needs to start with '!##' and consists of sections (starting with '!##').

One can use markdown emoji as :construction:, :question:, :warning: to get easy-to-track information in the markdown file. Not to break compatibility with the codi/gitlab/git/mkdocs markdown dialects we suggest to keep only basic markdown features. Our priviledged markdown dialect is the one of mkdocs.

In the python environment you can use 
- the **madx** object to access the MADX variables (as in [cpymad](https://github.com/hibtc/cpymad)). 
- the **pythonDictionary** to store objects (e.g., twiss dataframes, etc...), that will be dumped in the **output.pkl** (see below).



# How to run

This package is quite a basic code built around [cpymad](https://github.com/hibtc/cpymad): you need to have [cpymad](https://github.com/hibtc/cpymad)  installed.

You can use the package from the command line. For example you can run from prompt 
```
python -c "import madxp; madxp.madxp('myMadxFile.madx')"
```

And you will get automatically
- **log.madx**: logging of the MADX input
- **stdout.madx**: logging of the MADX stdout
- **output.pkl**: logging of the MADX variable space together with the dictionary **pythonDictionary**. You can read this pickle in a pythonic postprocessing session and for all code sections you will get the MADX variables and the saved python variables.
E.g.,:
```python
import pandas as pd
myDF=pd.read_pickle('output.pkl')
myTwiss=myDF.loc['Python data extraction']['pythonDictionary']['twiss']
```
will give
``` 
#s            160.603655
q1            160.603655
drift_0[0]     34.217492
q2             34.217492
drift_1[0]    160.603655
#e            160.603655
```

With a similar approach we can also inspect the MADX variable in the different sections:
```python
myDF['myk']
```
will give
``` 
Introduction                 NaN
Define the elements       0.0056
Define the sequence       0.0056
Define the beam           0.0056
Twiss the sequence        0.0056
Python data extraction    0.0056
End                       0.0056
```

We strongly suggest to have different title for each sections and to separate python sections from pure MADX ones. The section will be executed as a MADX [batch](http://hibtc.github.io/cpymad/cpymad/madx.html#cpymad.madx.Madx.batch). 

:warning: At the moment we prevent you to have MADX and python code in the same section for the following reason (an exeption is raised if you try it).
If one could interleave a MADX and a python code in the same section, the MADX code would be executed as a batch at the end of the section whereas the python code would be executed sequentially. For example, the code

```
!## Twiss the sequence
 use, sequence=myCell;
 twiss, file="myFirstTwiss.txt";
 plot, haxis=s, vaxis=betx,bety,dx,colour=100, title="First plot";
 //pythonDictionary['twiss']=madx.table.twiss.dframe()

!## Other section
```
will result in a logic error since, since we would try to access the **twiss** table "before" the actual **twiss** command (remember that MADX code is executed in batch at the end of the section). The correct approach (the enforced one) is
```
!## Twiss the sequence
 use, sequence=myCell;
 twiss, file="myFirstTwiss.txt";
 plot, haxis=s, vaxis=betx,bety,dx,colour=100, title="First plot";

!## Other section
 //pythonDictionary['twiss']=madx.table.twiss.dframe()
```

## From MADX to markdown documentation

You can transform a madx file in markdown by
```
python -c "import madxp; madxp.madx2md('myMadxFile.madx','myMadxFile.md')"
```

As an example, in the following we print the myMadxFile.md

## Introduction
 In this example we are going to solve a simple FODO lattice.
## Define the elements
 Define the geometrical parameters
```fortran
quadrupoleLength=5;
cellLength=100;
```
 Define the gradient
```fortran
myK=2.8/cellLength/quadrupoleLength;
```
 Define the quadrupoles
```fortran
QF: quadrupole, L=quadrupoleLength, K1=myK;
QD: quadrupole, L=quadrupoleLength, K1=-myK;

```
## Define the sequence
```fortran
myCell:sequence, refer=entry, L=cellLength;
q1: QF, at=0;
q2: QD, at=cellLength/2;
endsequence;

```
## Define the beam
```fortran
beam, particle=proton, energy=7000;

```
## Twiss the sequence
```fortran
use, sequence=myCell;
twiss, file="myFirstTwiss.txt";
plot, haxis=s, vaxis=betx,bety,dx,colour=100, title="First plot";
value, myK;

```
## Python data extraction
```python
# python code
pythonDictionary['twiss']=madx.table.twiss.dframe()
```
## End
```fortran
stop;
```

