## Introduction
In this example we are going to solve a simple FODO lattice.
## Define the elements
Define the geometrical parameters
```fortran
 quadrupoleLength=5;
 cellLength=100;
 
```
## Define the gradient
```fortran
 myK=2.8/cellLength/quadrupoleLength;

```
## Define the quadrupoles
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
