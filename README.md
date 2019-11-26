# madxp
A simple package for augmented MADX syntax using python and markdown

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

## Main motivation

We propose an augmented MADX syntax.

The main idea is three-fold:
1. Stay fully compatible with the standard MADX syntax.
2. to produce agile documentation from MADX files (main configuration or macros files) using markdown approach.
3. to run python during the MADX execution to improving debugging capability (and scripting flexibility)

We will show a simple example to discuss the conventions used in the augmented MADX syntax.

## Simple example
Imagine to have the following code
```
! # Introduction
! In this example we are going to solve a simple FODO lattice.

! # Define the elements
! Define the geometrical parameters
quadrupoleLength=5;
cellLength=100;

! Define the gradient
myK=2.8/cellLength/quadrupoleLength;

! Define the quadrupoles
QF: quadrupole, L=quadrupoleLength, K1=myK;
QD: quadrupole, L=quadrupoleLength, K1=-myK;

! # Define the sequence
myCell:sequence, refer=entry, L=cellLength;
q1: QF, at=0;
q2: QD, at=cellLength/2;
endsequence;

! # Define the beam
beam, particle=proton, energy=7000;

! # Twiss the sequence
use, sequence=myCell;
twiss, file="myFirstTwiss.txt";
plot, haxis=s, vaxis=betx,bety,dx,colour=100, title="First plot";
value, myK;

! # Python data extraction
// pythonDictionary['twiss']=madx.table.twiss.dframe()

! # End
stop;
```

Each line starting with "!" will be interpreted as a markdown input.

In order to comment MADX code w/o printing it as as markdown one can use '//' for commenting.

One can use :construction:, :question:, :warning: to get easy-to-track information in the markdown file. Not to break compatibility with the codi/gitlab/git/mkdocs markdown dialect I suggest to keep only basic markdown features.


You can use the package from the command line. For you can run an 
```
python -c "import madxp; madxp.madxp('myMadxFile.madx')"
```
And you will get automatically
- log.madx: logging all the MADX input
- stdout.madx: logging all the MADX stdout
- output.pkl: logging the MADX variable space in MADX together with the dictionary **pythonDictionary**.

Or you can transform a madx file in markdown by
```
python -c "import madxp; madxp.madx2md('myMadxFile.madx','myMadxFile.md')"
```
