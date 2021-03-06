## Beam-beam macros
This file contains the macros to study the beam-beam (BB) effect in [MADX](http://madx.web.cern.ch/madx/) and to prepare its input for [SixTrack](https://sixtrack.web.cern.ch/SixTrack/).
It is important to note that the conventions (units and reference frames) for describing the beam-beam are different in MADX and SixTrack.
These BB macros deals with head-on (HO) and long-range (LR) encounters.

:construction: Describe the typical workflow.
:construction: In MADX the strong beam position is relative to the reference orbit of the weak beam.
:construction: In SixTrack the strong beam defines the origin of the frame and the metric of the beam-beam force is established by describing the position of the weak beam with respect to the strong beam.
## Main contributors

- **S. Fartoukh**, 2011/11/16 from SLHCV3.0/beambeam
- **S. Fartoukh**, June 2012 modification to install an arbirtrary number of ho slices and crab the strong beam
- **D. Pellegrini**, macro for levelling with parallel separation, July 2016
- **S. Fartoukh**, feature corrected for twisscrab table creation (checking that all IP knob are off), July 2016
- **D. Pellegrini**, reverted to full path for the foot command, 15 July 2016
- **D. Pellegrini**, added macros to print the lenses in the sixtrack expert format, May 2017
- **D. Pellegrini**, added macros to remove BB lenses to simulate beams such as 8b4e, Set 2017
## Introduction
We will present some important variables used in the macros.

:warning: In MADX all variables have a global scope and have not to be initialized to be used: one has to be careful in not overwriting existing variables.
For this reason, each time a variable is redefined, a warning is issued to the user.
For the same reason, when introducing a new variables one should pick a self-explanatory and peculiar name.

**mylhcbeam** is the variable used to define the weak [beam](http://mad.web.cern.ch/mad/webguide/manual.html#Ch7.S1), that is the beam to track.

Given the weak beam, the strong beam follows. In the (HL-)LHC there are (presently) 3 beam definitions associated to three beam sequences

- mylhcbeam=1 (aka madB1): this represent the physical B1. Its **bv** flag is 1.
- mylhcbeam=2 (aka madB2): this is the "B2" as represented in MADX, rotating clockwise as B1  (that is madB2 travels from IP1 to IP2, in reality is the opposite) but correctly taking into account the magnetic polarity as seen by the B2. Its **bv** flag is -1.
- mylhcbeam=4 (aka madB4): this is the physical "B2", that is a new sequence is created such that the madB4
travels in the machine as the B2. Its **bv** flag is 1.

:construction: One can prove that the periodic solution of a lattice K(s) is related ot the one of a lattice K(-s) (See https://codimd.web.cern.ch/s/BkHpKRk3S).
In other words, from linear optics of the madB2 one can easily retrieve the one of the madB4.

:construction: One can define the mylhcbeam=3 (aka madB3), as the madB4 but with **bv** flag equal to -1.

If the weak beam (WB) is madB1[4] then the corresponding strong beam (SB) is madB4[1].
Due to the fact, that the relevant aspects of the strong beam considered in MADX are the strong beam sizes and positions, one can replace the strong madB4 with madB2 (the linear optics is equivalent).
De facto we have, if the weak beam is madB1[4], that the corresponding strong beam is madB2[1]. For that reason the madB3 is not (yet) considered.

**fraction_crab** is the fraction of the crabbing angle. If fraction_crab=1 the crossing angle is fully compensated by the CC.
## DEFINE_BB_PARAM
This macro computes

- the SB emittances (**beamx**,**beamy**) :warning: Please note that the meaning of these variables is not self-explanatory.
- the bunch length and relative energy spread of the the WB (**sigz**, **sige**)
- the charge of the HOs (the HO is split in several slices) and LRs (**ho_charge**, **lr_charge**).
These variables correspond to 1 if the charge of the SB bunch corresponds to the WB bunch.

- the distance between the between the LRs (**b_h_dist**)
- a file containing the s-positions and relative charges of the HOs (**temp/sliceho.madx**)

The assumed input variables are

- the beams associated with the **lhcb1** and **lhcb2** sequences.
- the number of the HO slices in the 4 IPs (**nho_IR1/2/5/8**)
- the LHC length (**LHCLENGTH**)
- the harmonic of the 400 MHz RF (**HRF400**). It is hardcoded that the bunches at '25' ns are separated by 10 buckets.
- the 'crude' bunch spacing, e.g., 25,50,...100 ns (**b_t_dist**). This is just a scaling factor to compute the real bucket separations.
- to compute the HO position it assume to have an executable **headonslice**.
:question: Should we consider a more general approach to define explicitly the bucket separation?
```fortran
DEFINE_BB_PARAM : macro = {
 
   if(mylhcbeam==1)
  {
  beamx = beam%lhcb2->ex;
  beamy = beam%lhcb2->ey;
  sigz  = beam%lhcb1->sigt;
  sige  = beam%lhcb1->sige;
  };
  if(mylhcbeam==2)
  {
  beamx = beam%lhcb1->ex;
  beamy = beam%lhcb1->ey;
  sigz  = beam%lhcb2->sigt;
  sige  = beam%lhcb2->sige;
  };
```
:question: Why do we use deferred expression?
```fortran
  ho_charge := 1.0d0;
  lr_charge := 1.0d0;
```
Here we define the splitting of the HO BB lens.
We print first in the file temp/sliceho.res the nho_IR1.
We reformat temp/sliceho.res on temp/sliceho.input just taking the numerical values of the slice.
This file will be the input of the fortran code *headonslice* that will produce the temp/sliceho.madx.
After we call the temp/sliceho.madx.

:question: Should we simplify it?

:warning: we should document the **headonslice**.
```fortran
  system, "rm -f temp/sliceho.res";
  system, "rm -f temp/sliceho.input";
  option, -echo, -info ;
  assign, echo=temp/sliceho.res;
  value, nho_IR1,nho_IR2,nho_IR5,nho_IR8;
  assign, echo=terminal ;
  system, "awk  '{print $3}'  temp/sliceho.res >  temp/sliceho.input";
  system, "/afs/cern.ch/eng/lhc/optics/beambeam_macros/headonslice";
  call, file="temp/sliceho.madx";
```
We define the spacing between parasitic encounters.
```fortran
  b_h_dist := LHCLENGTH/HRF400 * 10./2. * b_t_dist / 25.;
```
Print all output (but the file **temp/sliceho.madx**)
```fortran
  value, beamx, beamy, sigz, sige;
  value, ho_charge;
  value, lr_charge,b_h_dist;
};

```
## CALCULATE_XSCHEME
This macro computes

- the separation of the beam in the orthogonal plane of the crossing (**on_sep1,2,5,8**)

The assumed input variables are

- the halo separation in sigmas in the 4 IPs (**halo1,2,5,8**). Here the sigma are the one of SB (assuming madB1 as WB).
:construction: In most of the cases the beam are rounds (equal emittances and beta-functions) and the code is working smootly. It has to be imporved for flat optics.

- the initial separation of the beam (**on_sep1,2,5,8**)
- the **lhcb1** ad **lhcb2** sequences
```fortran
CALCULATE_XSCHEME(halo1,halo2,halo5,halo8) : macro = {
```
After deleting the twiss table it recompute it.

:question: Do we need to copy the table in a file (that will be overwritte in the macro itself) and then load the table from the file?

:warning: This macro is twissing. :question: is it the correct approach? should we move all TWISS commands on the mask?
```fortran
  
  delete,table=twissb1;
  delete,table=twissb2;
  
  select,flag=twiss,clear;
  select,flag=twiss,pattern=IP1,column=name,x,y,px,py,betx,bety;
  select,flag=twiss,pattern=IP2,column=name,x,y,px,py,betx,bety;
  select,flag=twiss,pattern=IP5,column=name,x,y,px,py,betx,bety;
  select,flag=twiss,pattern=IP8,column=name,x,y,px,py,betx,bety;
  use,sequence=lhcb1;twiss,file="temp/twiss.tfs";
  readmytable,file="temp/twiss.tfs",table=twissb1;
  use,sequence=lhcb2;twiss,file="temp/twiss.tfs";
  readmytable,file="temp/twiss.tfs",table=twissb2;
```
Calculate the initial separation in SB sigma as quadratic sum of the x and y separation.
The quadratic sum is done for convenience of the coding but the separation is always assumed to be in the orthogonal plane of the crossing (aka, non-xing plane).

:warning: This approach assumes that the $\beta$ of the SB is the one of the madB2.
```fortran
  sepx1 = (table(twissb1,ip1,x)-table(twissb2,ip1,x))/sqrt(beamx * table(twissb2,ip1,betx));
  sepy1 = (table(twissb1,ip1,y)-table(twissb2,ip1,y))/sqrt(beamy * table(twissb2,ip1,bety));
  sepr1 = sqrt(sepx1^2+sepy1^2);
  sepx2 = (table(twissb1,ip2,x)-table(twissb2,ip2,x))/sqrt(beamx * table(twissb2,ip2,betx));
  sepy2 = (table(twissb1,ip2,y)-table(twissb2,ip2,y))/sqrt(beamy * table(twissb2,ip2,bety));
  sepr2 = sqrt(sepx2^2+sepy2^2);
  sepx5 = (table(twissb1,ip5,x)-table(twissb2,ip5,x))/sqrt(beamx * table(twissb2,ip5,betx));
  sepy5 = (table(twissb1,ip5,y)-table(twissb2,ip5,y))/sqrt(beamy * table(twissb2,ip5,bety));
  sepr5 = sqrt(sepx5^2+sepy5^2);
  sepx8 = (table(twissb1,ip8,x)-table(twissb2,ip8,x))/sqrt(beamx * table(twissb2,ip8,betx));
  sepy8 = (table(twissb1,ip8,y)-table(twissb2,ip8,y))/sqrt(beamy * table(twissb2,ip8,bety));
  sepr8 = sqrt(sepx8^2+sepy8^2);
  value,sepr1, sepr2, sepr5, sepr8;
```
We calculate new on_sep to warrant halo collision in the non-xing plane by rescaling the present one.
```fortran

  on_sep1 = halo1/sepr1 * on_sep1;
  on_sep2 = halo2/sepr2 * on_sep2;
  on_sep5 = halo5/sepr5 * on_sep5;
  on_sep8 = halo8/sepr8 * on_sep8;

  value, on_x1, on_x2, on_x5, on_x8;
  value, on_sep1, on_sep2, on_sep5, on_sep8;
  value, on_alice, on_lhcb;
};

```
## INSTALL_SINGLE_BB_MARK
This macro will be used to modify the sequence in a SEQEDIT block by installaling a BB marker.

The assumed input variables are

- the label of the marker (**label**)
- the beam tag (**BIM**)
- the number tag of the encounter (**nn**).
- the relative position of the installation (**where**)
- the reference position of the installation (**origin**)

The marker name will correspond to a concatenation of **bbmk_labelBIM_nn**.

:warning: the **bbmarker** class should have been already instantiated.
```fortran
INSTALL_SINGLE_BB_MARK(label,BIM,nn,where,origin) : macro = {
  install,element=bbmk_labelBIM_nn,class=bbmarker,at=where,from=origin;
};

```
## HOLOC
This macro will define two auxiliary variables. In particular

- the name of the HO slices with $s-s_{IP} >0$ (*p*ositve, **wherep**)
- the name of the HO slices with $s-s_{IP} <0$ (*n*egative, **wheren**)
The assumed input variables are

- the IR number (**NIR**)
- the HO slice number (**NHO**)
```fortran
HOLOC(NIR,NHO) : macro = {
```
Auxiliary variable difining HO slices location
```fortran
  wherep= long_irNIR_NHO;
  wherem=-long_irNIR_NHO;
};

```
## INSTALL_BB_MARK
It install the HO and LR markers.

The assumed input variable is

- the name of the beam (**BIM**)
```fortran
INSTALL_BB_MARK(BIM) : macro = {
```
option,warn,info;
```fortran
  bbmarker: marker;
```
Install all ho and parasitic beam-beam marker within +/-170 m from IP1/2/5/8 for a given beam.
:question: Should we move the variable Linteraux in the mask file?
```fortran
  Linteraux:=170.;
```
Number of parasitic encounters
```fortran
  nparasitic:=Linteraux/b_h_dist;

  seqedit,sequence=lhcBIM;
```
Head-on in IR1
```fortran
  where = 1.e-9;
  exec INSTALL_SINGLE_BB_MARK(ho1,BIM,0,where,IP1);
  n=1; while ( n <= (nho_IR1/2)) {
    exec HOLOC(1,$n);
    exec INSTALL_SINGLE_BB_MARK(ho.L1,BIM,$n,wherem,IP1.L1);
    exec INSTALL_SINGLE_BB_MARK(ho.R1,BIM,$n,wherep,IP1);
  n=n+1;};
```
Head-on in IR2
```fortran
  where=1.e-9;
  exec INSTALL_SINGLE_BB_MARK(ho2,BIM,0,where,IP2);
  n=1;while ( n <= (nho_IR2/2)) {
    exec HOLOC(2,$n);
    exec INSTALL_SINGLE_BB_MARK(ho.L2,BIM,$n,wherem,IP2);
    exec INSTALL_SINGLE_BB_MARK(ho.R2,BIM,$n,wherep,IP2);
  n=n+1;};
```
Head-on in IR5
```fortran
  where=1.e-9;
  exec INSTALL_SINGLE_BB_MARK(ho5,BIM,0,where,IP5);
  n=1;while ( n <= (nho_IR5/2)) {
    exec HOLOC(5,$n);
    exec INSTALL_SINGLE_BB_MARK(ho.L5,BIM,$n,wherem,IP5);
    exec INSTALL_SINGLE_BB_MARK(ho.R5,BIM,$n,wherep,IP5);
  n=n+1;};
```
Head-on in IR8
```fortran
  where=1.e-9;
  exec INSTALL_SINGLE_BB_MARK(ho8,BIM,0,where,IP8);
  n=1;while ( n <= (nho_IR8/2)) {
    exec HOLOC(8,$n);
    exec INSTALL_SINGLE_BB_MARK(ho.L8,BIM,$n,wherem,IP8);
    exec INSTALL_SINGLE_BB_MARK(ho.R8,BIM,$n,wherep,IP8);
  n=n+1;};

```
Long-range in all IRs
:question: Should we consider to make a single loop?
```fortran
  n=1;while ( n <= nparasitic) {where=-n*b_h_dist;exec INSTALL_SINGLE_BB_MARK(par.L1,BIM,$n,where,IP1.L1);n=n+1;};
  n=1;while ( n <= nparasitic) {where= n*b_h_dist;exec INSTALL_SINGLE_BB_MARK(par.R1,BIM,$n,where,IP1)   ;n=n+1;};
  n=1;while ( n <= nparasitic) {where=-n*b_h_dist;exec INSTALL_SINGLE_BB_MARK(par.L2,BIM,$n,where,IP2)   ;n=n+1;};
  n=1;while ( n <= nparasitic) {where= n*b_h_dist;exec INSTALL_SINGLE_BB_MARK(par.R2,BIM,$n,where,IP2)   ;n=n+1;};
  n=1;while ( n <= nparasitic) {where=-n*b_h_dist;exec INSTALL_SINGLE_BB_MARK(par.L5,BIM,$n,where,IP5)   ;n=n+1;};
  n=1;while ( n <= nparasitic) {where= n*b_h_dist;exec INSTALL_SINGLE_BB_MARK(par.R5,BIM,$n,where,IP5)   ;n=n+1;};
  n=1;while ( n <= nparasitic) {where=-n*b_h_dist;exec INSTALL_SINGLE_BB_MARK(par.L8,BIM,$n,where,IP8)   ;n=n+1;};
  n=1;while ( n <= nparasitic) {where= n*b_h_dist;exec INSTALL_SINGLE_BB_MARK(par.R8,BIM,$n,where,IP8)   ;n=n+1;};

  endedit;
};

```
## REMOVE_BB_MARKER
It removes the class **bbmarker** in **lhcb1** and **lhcb1**.
:warning: It is not defined for **lhcb4**.
```fortran

REMOVE_BB_MARKER : macro = {
  option,warn,info;

  seqedit,sequence=lhcb1;
  select,flag=seqedit,clear;
  select,flag=seqedit,class=bbmarker;
  remove,element=SELECTED;
  endedit;

  seqedit,sequence=lhcb2;
  select,flag=seqedit,clear;
  select,flag=seqedit,class=bbmarker;
  remove,element=SELECTED;
  endedit;

  option,-warn,-info;
};

```
## CALCULATE_BB_LENS
This macro defines the reference tables to define the BB lens. Namely

- all the IR's surveys
- the madB1/2 twiss tables with crossing ON and crab OFF
- the madB1/2 twiss tables with crossing OFF and crab ON

It also compute the number of LR before D1 (where therfore the reference orbit is common to the two beams).
```fortran

CALCULATE_BB_LENS: macro = {
```

### Generate survey table for further use

These tags are used in the following to differentiate the

- the 4D kicks (beambeam4d_tag)
- the 6D kicks not at the IP position (beambeam6d_tag)
- the 6D kicks at the IP position (beambeam6dip_tag)
```fortran
  beambeam4d_tag = 4;
  beambeam6d_tag = 6;
  beambeam6dip_tag = 60;
```
Calculate survey table on the left/right of each IP for madB1 and madB2
:warning: There are incompatibilities with madB4.
```fortran

  delete,table=suir1b1;
  delete,table=suir1b2;
  delete,table=suir2b1;
  delete,table=suir2b2;
  delete,table=suir5b1;
  delete,table=suir5b2;
  delete,table=suir8b1;
  delete,table=suir8b2;

  select,flag=survey,clear;
  select,flag=survey,class=bbmarker;
  use,sequence=lhcb1,range=e.ds.l1.b1/s.ds.r1.b1;survey,x0=-0.097,file="temp/surveyaux.tfs";
  readmytable,file="temp/surveyaux.tfs",table=suir1b1;
  use,sequence=lhcb2,range=e.ds.l1.b2/s.ds.r1.b2;survey,x0= 0.097,file="temp/surveyaux.tfs";
  readmytable,file="temp/surveyaux.tfs",table=suir1b2;
  use,sequence=lhcb1,range=e.ds.l2.b1/s.ds.r2.b1;survey,x0= 0.097,file="temp/surveyaux.tfs";
  readmytable,file="temp/surveyaux.tfs",table=suir2b1;
  use,sequence=lhcb2,range=e.ds.l2.b2/s.ds.r2.b2;survey,x0=-0.097,file="temp/surveyaux.tfs";
  readmytable,file="temp/surveyaux.tfs",table=suir2b2;
  use,sequence=lhcb1,range=e.ds.l5.b1/s.ds.r5.b1;survey,x0=-0.097,file="temp/surveyaux.tfs";
  readmytable,file="temp/surveyaux.tfs",table=suir5b1;
  use,sequence=lhcb2,range=e.ds.l5.b2/s.ds.r5.b2;survey,x0= 0.097,file="temp/surveyaux.tfs";
  readmytable,file="temp/surveyaux.tfs",table=suir5b2;
  use,sequence=lhcb1,range=e.ds.l8.b1/s.ds.r8.b1;survey,x0= 0.097,file="temp/surveyaux.tfs";
  readmytable,file="temp/surveyaux.tfs",table=suir8b1;
  use,sequence=lhcb2,range=e.ds.l8.b2/s.ds.r8.b2;survey,x0=-0.097,file="temp/surveyaux.tfs";
  readmytable,file="temp/surveyaux.tfs",table=suir8b2;
```
:question: Why the need to specify a x0?
### Generate twiss table for further use
```fortran

  delete,table=twissb1;
  delete,table=twissb2;
  
```
:warning: There are incompatibilities with madB4.
```fortran

  select,flag=twiss,clear;
  select,flag=twiss,class=bbmarker,column=name,x,y,px,py,betx,bety,sig11,sig12,sig22,sig33,sig34,sig44,sig13,sig14,sig23,sig24;
  use,sequence=lhcb1;twiss,file="temp/twiss.tfs";
  readmytable,file="temp/twiss.tfs",table=twissb1;
  use,sequence=lhcb2;twiss,file="temp/twiss.tfs";
  readmytable,file="temp/twiss.tfs",table=twissb2;
```
:warning: The naming convention is not particularly strong.

Calculate twiss table with the crab cavities by switching off all crossings bumps.
```fortran

  if (abs(fraction_crab)>1e-10){
      on0_x1=on_x1; on0_sep1=on_sep1; on0_x2=on_x2; on0_sep2=on_sep2; on0_alice=on_alice;
      on0_x5=on_x5; on0_sep5=on_sep5; on0_x8=on_x8; on0_sep8=on_sep8; on0_lhcb =on_lhcb;
      on0_a1=on_a1; on0_o1=on_o1; on0_oe1=on_oe1; on0_a5=on_a5; on0_o5=on_o5; on0_oe5=on_oe5;
      on0_a2=on_a2; on0_o2=on_o2; on0_oe2=on_oe2; on0_a8=on_a8; on0_o8=on_o8; on0_oe8=on_oe8;
      on0_oh1=on_oh1; on0_oh2=on_oh2; on0_oh5=on_oh5; on0_oh8=on_oh8;
      on0_ov1=on_ov1; on0_ov2=on_ov2; on0_ov5=on_ov5; on0_ov8=on_ov8;
```
:question: why using deferred expressions?
```fortran
      on_x1:=0; on_sep1:=0; on_x2:=0; on_sep2:=0; on_alice:=0;
      on_x5:=0; on_sep5:=0; on_x8:=0; on_sep8:=0; on_lhcb :=0;
      on_a1=0; on0_o1=0; on_oe1=0; on_a5=0; on_o5=0; on_oe5=0;
      on_a2=0; on0_o2=0; on_oe2=0; on_a8=0; on_o8=0; on_oe8=0;
      on_oh1=0; on_oh2=0; on_oh5=0; on_oh8=0;
      on_ov1=0; on_ov2=0; on_ov5=0; on_ov8=0;
      
```
Check that the xcomax and the ycomax are vanishing.
```fortran

      use,sequence=lhcb1;twiss;corbitmax1=table(summ,xcomax)^2+table(summ,ycomax)^2;
      if(corbitmax1>1.d-15) {print,text="crossing bump not off for b1 when calculating CC effect in bbmacro"; stop;};
      use,sequence=lhcb2;twiss;corbitmax2=table(summ,xcomax)^2+table(summ,ycomax)^2;
      if(corbitmax2>1.d-15) {print,text="crossing bump not off for b2 when calculating CC effect in bbmacro"; stop;};
      
```
switch on the CC bumps assuming a parting at *z_crab* from the crab-unaffected particle
```fortran
      on_crab1:=fraction_crab*on0_x1;on_crab5:=fraction_crab*on0_x5;z_crab=0.075;
      select,flag=twiss,clear;
      select,flag=twiss,class=bbmarker,column=name,s,x,y,betx,bety,sig11,sig12,sig22,sig33,sig34,sig44,sig13,sig14,sig23,sig24;
      use,sequence=lhcb1;twiss,file="temp/twiss.tfs";
      readmytable,file="temp/twiss.tfs",table=twissb1_crab;
      use,sequence=lhcb2;twiss,file="temp/twiss.tfs";
      readmytable,file="temp/twiss.tfs",table=twissb2_crab;
      
      on_x1=on0_x1; on_sep1=on0_sep1;on_x2=on0_x2; on_sep2=on0_sep2; on_alice=on0_alice;
      on_x5=on0_x5; on_sep5=on0_sep5;on_x8=on0_x8; on_sep8=on0_sep8; on_lhcb =on0_lhcb;
      on_a1=on0_a1; on_o1=on0_o1;on_oe1=on0_oe1;on_a5=on0_a5;on_o5=on0_o5;on_oe5=on0_oe5;
      on_a2=on0_a2; on_o2=on0_o2;on_oe2=on0_oe2;on_a8=on0_a8;on_o8=on0_o8;on_oe8=on0_oe8;
      on_oh1=on0_oh1;on_oh2=on0_oh2;on_oh5=on0_oh5;on_oh8=on0_oh8;
      on_ov1=on0_ov1;on_ov2=on0_ov2;on_ov5=on0_ov5;on_ov8=on0_ov8;
```
reset to zero the CC configuration
```fortran
      on_crab1:=0;on_crab5:=0;z_crab=0;
    }
```
### Define HO BB lens for beam1/2
:warning: For clarity, the **define_BB_lens** should be moved before the present macro.
```fortran

  exec define_BB_lens(ho,1,0,hocharge_IR1,beambeam6dip_tag);
  n=1;while(n<=(nho_IR1/2)) {
    exec define_BB_lens(ho.L,1,$n,hocharge_IR1,beambeam6d_tag);
    exec define_BB_lens(ho.R,1,$n,hocharge_IR1,beambeam6d_tag);n=n+1;};

  exec define_BB_lens(ho,2,0,hocharge_IR2,beambeam6dip_tag);
  n=1;while(n<=(nho_IR2/2)) {
    exec define_BB_lens(ho.L,2,$n,hocharge_IR2,beambeam6d_tag);
    exec define_BB_lens(ho.R,2,$n,hocharge_IR2,beambeam6d_tag);n=n+1;};
  
  exec define_BB_lens(ho,5,0,hocharge_IR5,beambeam6dip_tag);
  n=1;while(n<=(nho_IR5/2)) {
    exec define_BB_lens(ho.L,5,$n,hocharge_IR5,beambeam6d_tag);
    exec define_BB_lens(ho.R,5,$n,hocharge_IR5,beambeam6d_tag);n=n+1;};
  
  exec define_BB_lens(ho,8,0,hocharge_IR8,beambeam6dip_tag);
  n=1;while(n<=(nho_IR8/2)) {
    exec define_BB_lens(ho.L,8,$n,hocharge_IR8,beambeam6d_tag);
    exec define_BB_lens(ho.R,8,$n,hocharge_IR8,beambeam6d_tag);n=n+1;};
```
### Define LR BB lens for beam1/2
```fortran

  n=1; while ( n <= nparasitic ) {
    exec define_BB_lens(par.L,1,$n,lr_charge,beambeam4d_tag);exec define_BB_lens(par.R,1,$n,lr_charge,beambeam4d_tag); if (abs(x_su) < 1.e-12) {npara0_1 = n;};
    exec define_BB_lens(par.L,2,$n,lr_charge,beambeam4d_tag);exec define_BB_lens(par.R,2,$n,lr_charge,beambeam4d_tag); if (abs(x_su) < 1.e-12) {npara0_2 = n;};
    exec define_BB_lens(par.L,5,$n,lr_charge,beambeam4d_tag);exec define_BB_lens(par.R,5,$n,lr_charge,beambeam4d_tag); if (abs(x_su) < 1.e-12) {npara0_5 = n;};
    exec define_BB_lens(par.L,8,$n,lr_charge,beambeam4d_tag);exec define_BB_lens(par.R,8,$n,lr_charge,beambeam4d_tag); if (abs(x_su) < 1.e-12) {npara0_8 = n;};
  n=n+1;};

  system,"echo 'Number of parasitic encounter before D1 in IR1/2/5/8'";
  value, npara0_1, npara0_2, npara0_5, npara0_8;
};

```
## DEFINE_BB_LENS
Using the twiss and the survey tables pre-computed by CALCULATE_BB_LENS, this macro defines the BB lens elements.
```fortran

DEFINE_BB_LENS(label,NIR,nn,flag,bbcomm) : macro = {
```
Define the reference amplitude of the CC kick.
:warning: The values 0.075 has to be consistent with the z_crab in CALCULATE_BB_LENS.
```fortran
  anorm_crab=sin(twopi*HRF400/LHCLENGTH*0.075);
```
Set the distance survey distance at a given encounter.
NB: the possible residual survey offset at the corresponding IP is subtracted.
:warning: Only x-survey offset is assumed
```fortran
  x_su_labelNIR_nn=table(suirNIRb2,bbmk_labelNIRb2_nn,x)-table(suirNIRb1,bbmk_labelNIRb1_nn,x)-
                  (table(suirNIRb2,bbmk_hoNIRb2_0,x)-table(suirNIRb1,bbmk_hoNIRb1_0,x));
  x_su = x_su_labelNIR_nn;
```
Strong beam parameters
:warning: The B2 is assumed to be the strong beam (see twissb2).
:warning: The sigx_labelNIRb1_nn and sigy_labelNIRb1_nn are used on the MAD-X BB lens but not for the SixTrack one were sig11 and sig33 are preferred.
```fortran
  sigx_labelNIRb1_nn  = sqrt(beamx*table(twissb2,bbmk_labelNIRb2_nn,betx));
  sigy_labelNIRb1_nn  = sqrt(beamy*table(twissb2,bbmk_labelNIRb2_nn,bety));
```
**IMPORTANT**: The positions of the strong beam wrt the reference orbit of the weak beam
```fortran
  posx_labelNIRb1_nn  = table(twissb2,bbmk_labelNIRb2_nn,x)+x_su_labelNIR_nn;
  posy_labelNIRb1_nn  = table(twissb2,bbmk_labelNIRb2_nn,y);
```
The HO slices are positioned also according to the crabbing (the crabbing is neglected for the LR, 4D lenses).
It there is crabbing (see **fraction_crab**), one computes the *s*-position of the encounter wrt the IP.
Then, the x and y positions due to the crabbing are computed.
```fortran
  if (abs(fraction_crab)>1e-10){ 
     s_labelNIRb1_nn = table(twissb1_crab,bbmk_labelNIRb1_nn,s)-table(twissb1_crab,bbmk_hoNIRb1_0,s);
     sin_labelNIRb2_nn=sin(2*s_labelNIRb1_nn*twopi*HRF400/LHCLENGTH)/anorm_crab;
     if (abs(s_labelNIRb1_nn)> b_h_dist*0.5) {sin_labelNIRb2_nn=0;};
     posx_labelNIRb1_crab_nn  = table(twissb2_crab,bbmk_labelNIRb2_nn,x)*sin_labelNIRb2_nn;
     posy_labelNIRb1_crab_nn  = table(twissb2_crab,bbmk_labelNIRb2_nn,y)*sin_labelNIRb2_nn;
  }
  else{
     posx_labelNIRb1_crab_nn  = 0.;
     posy_labelNIRb1_crab_nn  = 0.;
  }
```
As done for the madB1, one iterate on the madB2.
**NB**: the survey contribution is taken into account with the sign changed.
:question: The study for the madB2, is it needed?
:warning: The definition of the emittance (**beamx/y** is not consistent).
```fortran
  sigx_labelNIRb2_nn  = sqrt(beamx*table(twissb1,bbmk_labelNIRb1_nn,betx));
  sigy_labelNIRb2_nn  = sqrt(beamy*table(twissb1,bbmk_labelNIRb1_nn,bety));
  posx_labelNIRb2_nn  = table(twissb1,bbmk_labelNIRb1_nn,x)-x_su_labelNIR_nn;
  posy_labelNIRb2_nn  = table(twissb1,bbmk_labelNIRb1_nn,y);

  if (abs(fraction_crab)>1e-10){
     s_labelNIRb2_nn = table(twissb2_crab,bbmk_labelNIRb2_nn,s)-table(twissb2_crab,bbmk_hoNIRb2_0,s);
     sin_labelNIRb1_nn=sin(2*s_labelNIRb2_nn*twopi*HRF400/LHCLENGTH)/anorm_crab;
     if (abs(s_labelNIRb2_nn)> b_h_dist*0.5) {sin_labelNIRb1_nn=0;};
     posx_labelNIRb2_crab_nn  = table(twissb1_crab,bbmk_labelNIRb1_nn,x)*sin_labelNIRb1_nn;
     posy_labelNIRb2_crab_nn  = table(twissb1_crab,bbmk_labelNIRb1_nn,y)*sin_labelNIRb1_nn;
  }
  else{
     posx_labelNIRb2_crab_nn  = 0.;
     posy_labelNIRb2_crab_nn  = 0.;
  }

  bb_labelNIRb1_nn : beambeam, sigx   = sigx_labelNIRb1_nn, sigy    = sigy_labelNIRb1_nn,
                              xma    = posx_labelNIRb1_nn + posx_labelNIRb1_crab_nn,
            yma    = posy_labelNIRb1_nn + posy_labelNIRb1_crab_nn,
                  charge:= flag * ON_BB_CHARGE;
  bb_labelNIRb1_nn, slot_id = bbcomm;
```
**NB**: for the case of the B2, the BBDIR of the **beambeam** element takes is custom value (-1), that is opposite to the beam relative to the study (B2 in this clock of code).
```fortran
  bb_labelNIRb2_nn : beambeam, sigx   = sigx_labelNIRb2_nn, sigy    = sigy_labelNIRb2_nn,
                              xma    = posx_labelNIRb2_nn + posx_labelNIRb2_crab_nn,
            yma    = posy_labelNIRb2_nn + posy_labelNIRb2_crab_nn,
                  charge:= flag * ON_BB_CHARGE;
  bb_labelNIRb2_nn, slot_id =  bbcomm;
};

```
## PRINT_BB_LENSES
Print the lenses information in bb_lenses.dat. It will be used by SixTrack.
```fortran

PRINT_BB_LENSES: macro = {
```
Set outfile as *bb_lenses.dat*.
```fortran
  option,-echo, -info;
  system,"rm -rf bb_lenses.dat";
```
assign printing to bb_lenses.dat
```fortran
  assign, echo=bb_lenses.dat;
```
Print header in **EXPERT** mode.
:warning: the strong beam is assumed to be the madB2.
```fortran
  print, TEXT="BEAM";
  print, TEXT="EXPERT";
  printf, TEXT="%F %F %F %F %F 1 0 2 0", value= beam%lhcb2->NPART,
                beam%lhcb2->exn*1e6, beam%lhcb2->eyn*1e6,
                beam%lhcb2->sigt, beam%lhcb2->sige;
```
Print HO 6D lenses
:construction: In order to give continuity of the document, the PRINT_LENS6D and PRINT_LENS4D should be defined before this macro.
```fortran
  exec PRINT_LENS6D(ho,1,0,hocharge_IR1);
  n=1;while(n<=(nho_IR1/2)) {
    exec PRINT_LENS6D(ho.L,1,$n,ho_charge);
    exec PRINT_LENS6D(ho.R,1,$n,ho_charge); n=n+1;};
  
  exec PRINT_LENS6D(ho,2,0,hocharge_IR2);
  n=1;while(n<=(nho_IR2/2)) {
    exec PRINT_LENS6D(ho.L,2,$n,ho_charge);
    exec PRINT_LENS6D(ho.R,2,$n,ho_charge); n=n+1;};
  
  exec PRINT_LENS6D(ho,5,0,hocharge_IR5);
  n=1;while(n<=(nho_IR5/2)) {
    exec PRINT_LENS6D(ho.L,5,$n,ho_charge);
    exec PRINT_LENS6D(ho.R,5,$n,ho_charge); n=n+1;};
  
  exec PRINT_LENS6D(ho,8,0,hocharge_IR8);
  n=1;while(n<=(nho_IR8/2)) {
    exec PRINT_LENS6D(ho.L,8,$n,ho_charge);
    exec PRINT_LENS6D(ho.R,8,$n,ho_charge); n=n+1;};
  
```
Print LR 4D lenses
```fortran
  n=1; while ( n <= nparasitic ) {
    exec PRINT_LENS4D(par.L,1,$n,lr_charge);
    exec PRINT_LENS4D(par.R,1,$n,lr_charge); n=n+1;}
  n=1; while ( n <= nparasitic ) {
    exec PRINT_LENS4D(par.L,2,$n,lr_charge);
    exec PRINT_LENS4D(par.R,2,$n,lr_charge); n=n+1;}
  n=1; while ( n <= nparasitic ) {
    exec PRINT_LENS4D(par.L,5,$n,lr_charge);
    exec PRINT_LENS4D(par.R,5,$n,lr_charge); n=n+1;}
  n=1; while ( n <= nparasitic ) {
    exec PRINT_LENS4D(par.L,8,$n,lr_charge);
    exec PRINT_LENS4D(par.R,8,$n,lr_charge); n=n+1;}

  print, TEXT="NEXT";
```
restore printing to stdout
```fortran
  assign,echo=terminal;
}

```
## SIXTRACK_INPUT_BB_LENSES
Prepare the fc.3 and fc.2
```fortran
SIXTRACK_INPUT_BB_LENSES: macro = {
```
:question: why not creating directly the fc.3 wothout passing trought the bb_lenses.dat?
```fortran
  system,"cat bb_lenses.dat >> fc.3";
```
set the all the parameters of the lenses (denoted with the **20** tag) to zero in the fc.2 to allow reading from the fc.3
```fortran
  system,"sed -r -i 's/ 20 .+/ 20 0.0 0.0 0.0 0.0 0.0 0.0/g' fc.2";
}

```
## PRINT_LENS4D
Printing of the 4D lenses in SixTrack format.
```fortran

PRINT_LENS4D(label,NIR,nn,flag): macro = {
```
Printing of the 4D lenses
```fortran
  if (flag > 0.) {
    option,-echo, -info;
```
Emittance units are expressed in um.
:warning: The madB2 is assumed to be the strong beam.
```fortran
    s2x_labelNIRb2_nn = table(twissb2,bbmk_labelNIRb2_nn,sig11)*1e6;
    s2y_labelNIRb2_nn = table(twissb2,bbmk_labelNIRb2_nn,sig33)*1e6;
```
Changing from reference to closed orbit and putting units in mm.
It is important to remember the following definitions [DEFINE_BB_LENS](#DEFINE_BB_LENS)
posx_labelNIRb1_nn= table(twissb2,bbmk_labelNIRb2_nn,x)+x_su_labelNIR_nn;
posx_labelNIRb1_crab_nn=table(twissb2_crab,bbmk_labelNIRb2_nn,x)*sin(2*s_labelNIRb1_nn*twopi*HRF400/LHCLENGTH)/anorm_crab
posx_labelNIRb2_nn= table(twissb1,bbmk_labelNIRb1_nn,x)-x_su_labelNIR_nn
x_su_labelNIR_nn=table(suirNIRb2,bbmk_labelNIRb2_nn,x)-table(suirNIRb1,bbmk_labelNIRb1_nn,x)-(table(suirNIRb2,bbmk_hoNIRb2_0,x)-table(suirNIRb1,bbmk_hoNIRb1_0,x));
The ox_labelNIRb2_nn represent the algebric distanca of the strong beam from the weak beam and is computed as the
twissb2.x + twissb2_crab.x - twissb1.x - (survey2.x - survey1.x)

:warning: :construction: I would say it should be twissb2.x + twissb2_crab.x - twissb1.x **- twissb1_crab.x +** (survey2.x - survey1.x)
```fortran
    ox_labelNIRb2_nn = (posx_labelNIRb1_nn+posx_labelNIRb1_crab_nn-posx_labelNIRb2_nn-x_su_labelNIR_nn+1e-10)*1e3; 
    oy_labelNIRb2_nn = (posy_labelNIRb1_nn+posy_labelNIRb1_crab_nn-posy_labelNIRb2_nn+1e-10)*1e3;
    
```
Avoid numerical instabilities in SixTrack
```fortran
    if ( ox_labelNIRb2_nn > 0 && ox_labelNIRb2_nn <  1e-7 ) { ox_labelNIRb2_nn =  1e-7; }
    if ( ox_labelNIRb2_nn < 0 && ox_labelNIRb2_nn > -1e-7 ) { ox_labelNIRb2_nn = -1e-7; }
    if ( oy_labelNIRb2_nn > 0 && oy_labelNIRb2_nn <  1e-7 ) { oy_labelNIRb2_nn =  1e-7; }
    if ( oy_labelNIRb2_nn < 0 && oy_labelNIRb2_nn > -1e-7 ) { oy_labelNIRb2_nn = -1e-7; }
```
```python
# python code
print, TEXT="name nslices Sxx Syy hsep vsep ratio";
```
```fortran
    printf, TEXT="bb_labelnirb1_nn 0 %F %F %F %F 1", value= s2x_labelNIRb2_nn, s2y_labelNIRb2_nn,-ox_labelNIRb2_nn,-oy_labelNIRb2_nn;
```
```python
# python code
printf, TEXT="%F %F %F %F %F %F", value = posx_labelNIRb2_nn, posx_labelNIRb2_crab_nn, posx_labelNIRb1_nn, posx_labelNIRb1_crab_nn, ox_labelNIRb2_nn, x_su_labelNIR_nn;
```
```fortran
  }
};

```
## PRINT_LENS6D
Printing of the 6D lenses in SixTrack format.
```fortran
PRINT_LENS6D(label,NIR,nn,flag) : macro = {
```
:warning: :construction: See the comment wrote for the PRINT_LENS4D
```fortran
  ox_labelNIRb2_nn = (posx_labelNIRb1_nn+posx_labelNIRb1_crab_nn-posx_labelNIRb2_nn-x_su_labelNIR_nn+1e-10)*1e3;
  oy_labelNIRb2_nn = (posy_labelNIRb1_nn+posy_labelNIRb1_crab_nn-posy_labelNIRb2_nn+1e-10)*1e3;
```
Avoid numerical instabilities in Sixtrack
```fortran
  if ( ox_labelNIRb2_nn > 0 && ox_labelNIRb2_nn <  1e-7 ) { ox_labelNIRb2_nn =  1e-7; }
  if ( ox_labelNIRb2_nn < 0 && ox_labelNIRb2_nn > -1e-7 ) { ox_labelNIRb2_nn = -1e-7; }
  if ( oy_labelNIRb2_nn > 0 && oy_labelNIRb2_nn <  1e-7 ) { oy_labelNIRb2_nn =  1e-7; }
  if ( oy_labelNIRb2_nn < 0 && oy_labelNIRb2_nn > -1e-7 ) { oy_labelNIRb2_nn = -1e-7; }

  /*
  printf, TEXT="TEST1 bb_labelnirb1_nn %F %F %F %F %F", value= posx_labelNIRb1_nn, posx_labelNIRb1_crab_nn, posx_labelNIRb2_nn, x_su_labelNIR_nn;
  printf, TEXT="TEST2 bb_labelnirb1_nn %F %F", value= ox_labelNIRb2_nn, (posx_labelNIRb1_nn+posx_labelNIRb1_crab_nn-posx_labelNIRb2_nn-x_su_labelNIR_nn+1e-10)*1e3;
  */
```
get the uncrabbed momenta to compute the crossing angle and plane
```fortran
  px_labelNIRb1_nn = table(twissb1,bbmk_labelNIRb1_nn,px);
  px_labelNIRb2_nn = table(twissb2,bbmk_labelNIRb2_nn,px);
  py_labelNIRb1_nn = table(twissb1,bbmk_labelNIRb1_nn,py);
  py_labelNIRb2_nn = table(twissb2,bbmk_labelNIRb2_nn,py);
```
Positive agles are defined if  px_labelNIRb1_nn>px_labelNIRb2_nn.
```fortran
  dlt_px=px_labelNIRb1_nn-px_labelNIRb2_nn;
  dlt_py=py_labelNIRb1_nn-py_labelNIRb2_nn;
```
Compute crossing angle and crossing plane.
More information can be found at https://www.overleaf.com/read/mspghkddjhbb
The checks are in the **check_alpha_phi_calculation** folder.
```fortran
  bbbmacros_absphi = sqrt(dlt_px^2 + dlt_py^2) / 2.0;
  if (bbbmacros_absphi < 1e-20)
      {xang_labelNIR_nn = bbbmacros_absphi;xplane_labelNIR_nn = 0.0;}
  else
      {if (dlt_py>=0)
          {if (dlt_px>=0) !First QUADRANT
              {if (abs(dlt_px) >= abs(dlt_py)) !First OCTANT
                  {xang_labelNIR_nn=bbbmacros_absphi;
                   xplane_labelNIR_nn = atan(dlt_py/dlt_px);}
              else                             !Second OCTANT
                  {
                   xang_labelNIR_nn=bbbmacros_absphi;
                   xplane_labelNIR_nn = 0.5*pi - atan(dlt_px/dlt_py);}
              }
          else !dlt_px<0  !Second QUADRANT
              {if (abs(dlt_px) < abs(dlt_py))  !Third OCTANT
                  {
                   xang_labelNIR_nn=bbbmacros_absphi;
                   xplane_labelNIR_nn = 0.5*pi - atan(dlt_px/dlt_py);}
              else                             !Fourth OCTANT
                  {
                   xang_labelNIR_nn=-bbbmacros_absphi;
                   xplane_labelNIR_nn = atan(dlt_py/dlt_px);}
              }
          }
      else !dlt_py<0
          {if (dlt_px<=0) !Third QUADRANT
              {if (abs(dlt_px) >= abs(dlt_py)) !Fifth OCTANT
                  {
                   xang_labelNIR_nn=-bbbmacros_absphi;
                   xplane_labelNIR_nn = atan(dlt_py/dlt_px);}
              else                             !Sixth OCTANT
                  {
                   xang_labelNIR_nn=-bbbmacros_absphi;
                   xplane_labelNIR_nn = 0.5*pi - atan(dlt_px/dlt_py);}
              }
          else !dlt_px>0  !Fourth QUADRANT
              {if (abs(dlt_px) < abs(dlt_py))  !Seventh OCTANT
                  {
                   xang_labelNIR_nn=-bbbmacros_absphi;
                   xplane_labelNIR_nn = 0.5*pi - atan(dlt_px/dlt_py);}
              else                             !Eighth  OCTANT
                  {
                   xang_labelNIR_nn=bbbmacros_absphi;
                   xplane_labelNIR_nn = atan(dlt_py/dlt_px);}
              }
          }
      }

```
```python
# python code
if (dlt_px == 0.) { xplane_labelNIR_nn = pi/2; }
else { xplane_labelNIR_nn = atan((dlt_py)/(dlt_px)); }
```
**IMPORTANT**: The minus sign is needed since, in SixTrack, we need to define the weak position wrt the strong frame.
```fortran
  printf, TEXT="bb_labelnirb1_nn 1 %F %F %F %F", value= xang_labelNIR_nn, xplane_labelNIR_nn, -ox_labelNIRb2_nn, -oy_labelNIRb2_nn;
```
The 4D sigma matrix is consired and the charge of the bunch is equally distributed on the different slices
```fortran
  printf, TEXT="%F %F %F %F %F", value=
          table(twissb2,bbmk_labelNIRb2_nn,sig11)*1e6, 
          table(twissb2,bbmk_labelNIRb2_nn,sig12)*1e6, 
          table(twissb2,bbmk_labelNIRb2_nn,sig22)*1e6, 
          table(twissb2,bbmk_labelNIRb2_nn,sig33)*1e6, 
          table(twissb2,bbmk_labelNIRb2_nn,sig34)*1e6;
  printf, TEXT="%F %F %F %F %F %F", value=
          table(twissb2,bbmk_labelNIRb2_nn,sig44)*1e6, 
          table(twissb2,bbmk_labelNIRb2_nn,sig13)*1e6, 
          table(twissb2,bbmk_labelNIRb2_nn,sig14)*1e6, 
          table(twissb2,bbmk_labelNIRb2_nn,sig23)*1e6, 
          table(twissb2,bbmk_labelNIRb2_nn,sig24)*1e6,
          1.0/nho_IRnir; 
```
```python
# python code
printf, text="CRABBING %F %F %F %F", value = posx_labelNIRb1_crab_nn, posx_labelNIRb2_crab_nn, posy_labelNIRb1_crab_nn, posy_labelNIRb2_crab_nn;
```
```fortran
};

```
## INSTALL_SINGLE_BB_LENS
Install a single BB lens
```fortran
INSTALL_SINGLE_BB_LENS(label,nn,where,origin) : macro = {
  install,element=bb_label_nn,at=where,from=origin;
};

```
## INSTALL_BB_LENS
This macro takse a beam as input (**BEAM**) and install (**seqedit**) in a in a loop all the BB lenses.
```fortran
INSTALL_BB_LENS(BIM) : macro = {
```
```python
# python code
option,warn,info;
```
```fortran
  seqedit,sequence=lhcBIM;
```
Head-on in IR1
```fortran
  if (on_ho1<>0){
    where= 1.e-9;
    exec INSTALL_SINGLE_BB_LENS(ho1BIM,0,where,IP1);
    n=1;
    while ( n <= (nho_IR1/2)) {
      exec HOLOC(1,$n);
      exec INSTALL_SINGLE_BB_LENS(ho.L1BIM,$n,wherem,IP1.L1);
      exec INSTALL_SINGLE_BB_LENS(ho.R1BIM,$n,wherep,IP1);
      n=n+1;
    };
  };
```
Head-on in IR2
```fortran
  if (on_ho2<>0){
    where= 1.e-9;
    exec INSTALL_SINGLE_BB_LENS(ho2BIM,0,where,IP2);
    n=1;
    while ( n <= (nho_IR2/2)) {
      exec HOLOC(2,$n);
      exec INSTALL_SINGLE_BB_LENS(ho.L2BIM,$n,wherem,IP2);
      exec INSTALL_SINGLE_BB_LENS(ho.R2BIM,$n,wherep,IP2);
      n=n+1;
    };
  };
  
```
Head-on in IR5
```fortran
  if (on_ho5<>0){
    where= 1.e-9;
    exec INSTALL_SINGLE_BB_LENS(ho5BIM,0,where,IP5);
    n=1;
    while ( n <= (nho_IR5/2)) {
      exec HOLOC(5,$n);
      exec INSTALL_SINGLE_BB_LENS(ho.L5BIM,$n,wherem,IP5);
      exec INSTALL_SINGLE_BB_LENS(ho.R5BIM,$n,wherep,IP5);
      n=n+1;
    };
  };
```
Head-on in IR8
```fortran
  if (on_ho8<>0){
    where= 1.e-9;
    exec INSTALL_SINGLE_BB_LENS(ho8BIM,0,where,IP8);
    n=1;
    while ( n <= (nho_IR8/2)) {
      exec HOLOC(8,$n);
      exec INSTALL_SINGLE_BB_LENS(ho.L8BIM,$n,wherem,IP8);
      exec INSTALL_SINGLE_BB_LENS(ho.R8BIM,$n,wherep,IP8);
      n=n+1;
    };
  };
  
```
Long-range in left of IP1
```fortran
  if (on_lr1l<>0){
    n=1;
    while ( n <= npara_1) {
      where=-n*b_h_dist;
      exec INSTALL_SINGLE_BB_LENS(par.L1BIM,$n,where,IP1.L1);n=n+1;
    };
  };
```
Long-range in right of IP1
```fortran
  if (on_lr1r<>0){
    n=1;
    while ( n <= npara_1) {
      where= n*b_h_dist;
      exec INSTALL_SINGLE_BB_LENS(par.R1BIM,$n,where,IP1);n=n+1;
    };
  };
```
Long-range in left of IP2
```fortran
  if (on_lr2l<>0){
    n=1;
    while ( n <= npara_2) {
      where=-n*b_h_dist;
      exec INSTALL_SINGLE_BB_LENS(par.L2BIM,$n,where,IP2);
      n=n+1;
    };
  };
```
Long-range in right of IP2
```fortran
  if (on_lr2r<>0){
    n=1;
    while ( n <= npara_2) {
      where= n*b_h_dist;
      exec INSTALL_SINGLE_BB_LENS(par.R2BIM,$n,where,IP2);n=n+1;
    };
  };
```
Long-range in left of IP5
```fortran
  if (on_lr5l<>0){
    n=1;
    while ( n <= npara_5) {
      where=-n*b_h_dist;
      exec INSTALL_SINGLE_BB_LENS(par.L5BIM,$n,where,IP5);
      n=n+1;
    };
  };
```
Long-range in right of IP5
```fortran
  if (on_lr5r<>0){
    n=1;
    while ( n <= npara_5) {
      where= n*b_h_dist;
      exec INSTALL_SINGLE_BB_LENS(par.R5BIM,$n,where,IP5);
      n=n+1;
    };
  };
```
Long-range in left of IP8
```fortran
  if (on_lr8l<>0){
    n=1;while ( n <= npara_8) {
      where=-n*b_h_dist;
      exec INSTALL_SINGLE_BB_LENS(par.L8BIM,$n,where,IP8);
      n=n+1;
    };
  };
```
Long-range in right of IP8
```fortran
  if (on_lr8r<>0){
    n=1;
    while ( n <= npara_8) {
      where= n*b_h_dist;
      exec INSTALL_SINGLE_BB_LENS(par.R8BIM,$n,where,IP8);
      n=n+1;
    };
  };
  endedit;
```
```python
# python code
option,-warn,-info;
```
```fortran
};

```
## REMOVE_BB_LENS
Remove BB marker from **lhcb1** and **lhcb2**.
:warning: The **lhcb2** is not considered.
```fortran
REMOVE_BB_LENS : macro = {
  option,warn,info;

  seqedit,sequence=lhcb1;
  select,flag=seqedit,clear;
  select,flag=seqedit,class=beambeam;
  remove,element=SELECTED;
  endedit;

  seqedit,sequence=lhcb2;
  select,flag=seqedit,clear;
  select,flag=seqedit,class=beambeam;
  remove,element=SELECTED;
  endedit;

  option,-warn,-info;
};

```
## SELECT_BB_LENS
This macro takes

- the start (**label**)
- and the end (**nn**) of a
**pattern** and select it in the **seqedit**. It is used in the macro **REMOVE_BB_LENS_FILL_SCHEME**.
```fortran
SELECT_BB_LENS(label,nn) : macro = {
  select,flag=seqedit,pattern="^label_nn$";
  print, text="label_nn selected";
};

```
## REMOVE_BB_LENS_FILL_SCHEME
This macro takes

- the beam (**BIM**)
- the number of the IR (**NIR**)
- the number of filled slot(s) (**BUNCHES**)
- the number of empty slot(s) (**EMPTY**)
- the weak beam bunch considered (**POS**)
:question: shold we consider this macro in a more general cpymad oriented approach?
```fortran
REMOVE_BB_LENS_FILL_SCHEME : macro(BIM, NIR, BUNCHES, EMPTY, POS) = {
  printf, text="Removing long ranges for %gb%ge, considering bunch %g in the train", value = BUNCHES, EMPTY, POS; 
  seqedit,sequence=lhcbBIM;
  select,flag=seqedit,clear;
```
Right part
```fortran
  n = BUNCHES-POS+1;
  while ( n <= npara_NIR) {
    m = 0;
    while (n <= npara_NIR && m < EMPTY) {
      exec, SELECT_BB_LENS(bb_par.rNIRbBIM,$n);
      n=n+1;
      m=m+1;
    }
    n=n+BUNCHES;
  };
```
Left part
```fortran
  n = POS;
  while ( n <= npara_NIR) {
    m = 0;
    while (n <= npara_NIR && m < EMPTY) {
      exec, SELECT_BB_LENS(bb_par.lNIRbBIM,$n);
      n=n+1;
      m=m+1;
    }
    n=n+BUNCHES;
  };
  remove, element=SELECTED;
  endedit;
  print, text="Selected long ranges removed"; 
};

```
## PLOT_BB_SEP
This function takes the

- number of the IR (**NIR**)
- the number of the encounter (**nn**)
and plot the
```fortran
PLOT_BB_SEP(NIR,nn) : macro ={
```
Delete the existing tables.
```fortran
  delete,table=twissb1;
  delete,table=twissb2;
  delete,table=sub1;
  delete,table=sub2;
  delete,table=beambeamsep;
```
Define the $x$-survey starting point.
```fortran
  itest=NIR;
  if(itest==1) {xsu0=-0.097;};
  if(itest==2) {xsu0= 0.097;};
  if(itest==5) {xsu0=-0.097;};
  if(itest==8) {xsu0= 0.097;};
```
Twiss the **lhcb1** sequence.
```fortran
  use,sequence=lhcb1;
  select,flag=twiss,clear;
  select,flag=twiss,class=bbmarker,range=e.ds.lNIR.b1/s.ds.rNIR.b1, column=name,s,betx,bety,x,y;
  twiss,file="temp/twiss.tfs";readmytable,file="temp/twiss.tfs",table=twissb1;
```
Survey the **lhcb1** sequence.
```fortran
  use,sequence=lhcb1,range=e.ds.lNIR.b1/s.ds.rNIR.b1;
  select,flag=survey,clear;
  select,flag=survey,class=bbmarker;
  survey,x0=xsu0,file="temp/surveyaux.tfs";
  readmytable,file="temp/surveyaux.tfs",table=sub1;
```
Twiss the **lhcb2** sequence.
```fortran
  use,sequence=lhcb2;
  select,flag=twiss,clear;
  select,flag=twiss,class=bbmarker,range=e.ds.lNIR.b2/s.ds.rNIR.b2, column=name,s,betx,bety,x,y;
  twiss,file="temp/twiss.tfs";readmytable,file="temp/twiss.tfs",table=twissb2;
```
Survey the **lhcb2** sequence.
```fortran
  use,sequence=lhcb2,range=e.ds.lNIR.b2/s.ds.rNIR.b2;
  select,flag=survey,clear;
  select,flag=survey,class=bbmarker;
  survey,x0=-xsu0,file="temp/surveyaux.tfs";
  readmytable,file="temp/surveyaux.tfs",table=sub2;
```
Definition of the length of the table to be used in the loop.
```fortran
  ltab=table(twissb1,tablelength);
```
Create the separation table (**beambeamsep**) and define the location of the IP (**loc0**) and the $s$-interval from the IP to consider (**locmax**).
:warning: **imax** is not used in this macros.
```fortran
  create,table=beambeamsep,column=loc,sepx,sepy,sepxb1,sepyb1,sepxb2,sepyb2;

  loc0  =table(sub1,bbmk_hoNIRb1_0,s);
  imax  =nn;
  locmax=nn*b_h_dist+0.1;
  n=1;
```
In this loop the separation table is filled by calling **FILTABSEP**.

:warning: It seems that only $n>1$ encounters are considered.
```fortran
  while(n<=ltab) {
    exec FILTABSEP($n);n=n+1;
  };

  /*
  write,table=beambeamsep;
  */

  PLOT,style=100,table=beambeamsep,title="H/V Beam-beam sep. for beam1 [sigma]",symbol=3,noversion=true,haxis=loc,
      vaxis=sepxb1,sepyb1;
  PLOT,style=100,table=beambeamsep,title="H/V Beam-beam sep. for beam2 [sigma]",symbol=3,noversion=true,haxis=loc,
      vaxis=sepxb2,sepyb2;
  PLOT,style=100,table=beambeamsep,title="H/V Beam-beam sep. [mm]",symbol=3,noversion=true,haxis=loc,
      vaxis=sepx,sepy;
};

```
## FILTABSEP
This macro takse the number of parasitic encounter (**nn**) and fill the separation table (**beambeamsep**).
It is used only in the PLOT_BB_SEP macro but is important for sanity checks.
In the **FILTABSEP** table there are the following columns:

- **loc**: position in [m] of the encounter wrt to the IP (defined in the madB1 survey table (**sub1**))
- **sepx**: absolute value of separation in $x$ in [mm] of the madB2 from the closed orbit of the madB1. The survey is take into account.
- **sepy**: absolute value of separation in $y$ in [mm] of the madB2 from the closed orbit of the madB1 (the survey is ignored assuming a horizotal machine).
- **sepxb1**: **sepx** expressed in madB1's $\sigma_x$
- **sepyb1**: **sepy** expressed in madB1's $\sigma_y$
- **sepxb2**: **sepx** expressed in madB2's $\sigma_x$
- **sepyb2**: **sepy** expressed in madB2's $\sigma_y$

:warning: The normalized emittances (**beamx**, **beamy**) are associated to the strong beam.
```fortran
FILTABSEP(nn) : macro = {
  loc        =table(sub1,s,nn)-loc0;
  sepx   =abs(table(twissb2,x,nn)-table(twissb1,x,nn)+table(sub2,x,nn)-table(sub1,x,nn))*1000.;
  sepy   =abs(table(twissb2,y,nn)-table(twissb1,y,nn))*1000.;
  sepxb1 =sepx/sqrt(beamx*table(twissb1,betx,nn))/1000.;
  sepyb1 =sepy/sqrt(beamy*table(twissb1,bety,nn))/1000.;
  sepxb2 =sepx/sqrt(beamx*table(twissb2,betx,nn))/1000.;
  sepyb2 =sepy/sqrt(beamy*table(twissb2,bety,nn))/1000.;
  if (abs(loc)<locmax){fill,table=beambeamsep;};
};

```
## PRINT_BB_lens_param
This macro takes as input the

- label of the beambeam element (**label**)
- the IP number (**NIR**)
- the beam (**BIM**)
- the number of the encounter (**nn**)

It returns the following attributes of the

- longitudinal position of the encouter in meters (**xma**)
- the MADX x-position of the beambeam element in mm (**xma**)
- the MADX y-position of the beambeam element in mm (**yma**)
- the MADX $\sigma_x$ of the beambeam element in mm (**sigx**)
- the MADX $\sigma_y$ of the beambeam element in mm (**sigy**)
```fortran
PRINT_BB_lens_param(label,NIR,BIM,nn) : macro = {
```
:question: Can we get the $s$-position as attribute of bb_labelNIRBIM_nn?
```fortran
  loc=table(twiss,bb_labelNIRBIM_nn,s);
  xma=bb_labelNIRBIM_nn->xma*1000.;
  yma=bb_labelNIRBIM_nn->yma*1000.;
  sigx=bb_labelNIRBIM_nn->sigx*1000.;
  sigy=bb_labelNIRBIM_nn->sigy*1000.;
};

```
## PRINT_BB_table
This macro takes as input the beam (**BIM**) and print the summary BB table (**BBtable_BIM**).
```fortran
PRINT_BB_table(BIM) : macro = {
  delete,table=BBtable_BIM;
  create,table=BBtable_BIM,column=loc,xma,yma,sigx,sigy;

  delete,table=twissBIM;
  select,flag=twiss,clear;
  select,flag=twiss,class=beambeam,column=name,s;
  use,sequence=lhcBIM;twiss,file="temp/twiss.tfs";
  readmytable,file="temp/twiss.tfs",table=twissBIM;

  n=1;while(n<=npara_5) {exec PRINT_BB_lens_param(par.L,5,BIM,$n);fill,table=BBtable_BIM;n=n+1;};
```
:warning: It seems that the printing is done only for 5 HO slices (for all IPs, see below)
```fortran
  exec PRINT_BB_lens_param(ho.L,5,BIM,2);fill,table=BBtable_BIM;
  exec PRINT_BB_lens_param(ho.L,5,BIM,1);fill,table=BBtable_BIM;
  exec PRINT_BB_lens_param(ho,5,BIM,0);fill,table=BBtable_BIM;
  exec PRINT_BB_lens_param(ho.R,5,BIM,1);fill,table=BBtable_BIM;
  exec PRINT_BB_lens_param(ho.R,5,BIM,2);fill,table=BBtable_BIM;
  n=1;while(n<=npara_5) {exec PRINT_BB_lens_param(par.R,5,BIM,$n);fill,table=BBtable_BIM;n=n+1;};

  n=1;while(n<=npara_8) {exec PRINT_BB_lens_param(par.L,8,BIM,$n);fill,table=BBtable_BIM;n=n+1;};
  exec PRINT_BB_lens_param(ho.L,8,BIM,2);fill,table=BBtable_BIM;
  exec PRINT_BB_lens_param(ho.L,8,BIM,1);fill,table=BBtable_BIM;
  exec PRINT_BB_lens_param(ho,8,BIM,0);fill,table=BBtable_BIM;
  exec PRINT_BB_lens_param(ho.R,8,BIM,1);fill,table=BBtable_BIM;
  exec PRINT_BB_lens_param(ho.R,8,BIM,2);fill,table=BBtable_BIM;
  n=1;while(n<=npara_8) {exec PRINT_BB_lens_param(par.R,8,BIM,$n);fill,table=BBtable_BIM;n=n+1;};

  n=1;while(n<=npara_1) {exec PRINT_BB_lens_param(par.L,1,BIM,$n);fill,table=BBtable_BIM;n=n+1;};
  exec PRINT_BB_lens_param(ho.L,1,BIM,2);fill,table=BBtable_BIM;
  exec PRINT_BB_lens_param(ho.L,1,BIM,1);fill,table=BBtable_BIM;
  exec PRINT_BB_lens_param(ho,1,BIM,0);fill,table=BBtable_BIM;
  exec PRINT_BB_lens_param(ho.R,1,BIM,1);fill,table=BBtable_BIM;
  exec PRINT_BB_lens_param(ho.R,1,BIM,2);fill,table=BBtable_BIM;
  n=1;while(n<=npara_1) {exec PRINT_BB_lens_param(par.R,1,BIM,$n);fill,table=BBtable_BIM;n=n+1;};

  n=1;while(n<=npara_2) {exec PRINT_BB_lens_param(par.L,2,BIM,$n);fill,table=BBtable_BIM;n=n+1;};
  exec PRINT_BB_lens_param(ho.L,2,BIM,2);fill,table=BBtable_BIM;
  exec PRINT_BB_lens_param(ho.L,2,BIM,1);fill,table=BBtable_BIM;
  exec PRINT_BB_lens_param(ho,2,BIM,0);fill,table=BBtable_BIM;
  exec PRINT_BB_lens_param(ho.R,2,BIM,1);fill,table=BBtable_BIM;
  exec PRINT_BB_lens_param(ho.R,2,BIM,2);fill,table=BBtable_BIM;
  n=1;while(n<=npara_2) {exec PRINT_BB_lens_param(par.R,2,BIM,$n);fill,table=BBtable_BIM;n=n+1;};

  write,table=BBtable_BIM,file=temp/BBtable_BIM.tfs;
};

```
## MAKEFOOTPRINT
It takes as input the beam (**BIM**) and call the corresponding sequence.
This seems to be an old routine.
:question: should this routine be in the BB macros?
:question: is it alternative to the following PLOTFOOTPRINT?
```fortran
MAKEFOOTPRINT(BIM) : macro = {
```
:warning: We should not allowed rotation inside the macros.
```fortran
  seqedit,sequence=lhcBIM;
  cycle,start=IP3;
  flatten;
  endedit;

  use,sequence=lhcBIM;
```
```python
# python code
option,trace;
```
```fortran
  small=0.05;
  big=sqrt(1.-small^2);
  track;
  xs=small; ys=small;
  value,xs,ys;
  start,fx=xs,fy=ys;  // zero amplitude
  n=1; // sigma multiplier
  m=0; // angle multiplier
  while (n <= nsigmax)
  {
    angle = 15*m*pi/180;
    if (m == 0) {xs=n*big; ys=n*small;}
    elseif (m == 6) {xs=n*small; ys=n*big;}
    else
    {
      xs=n*cos(angle);
      ys=n*sin(angle);
    }
    value,xs,ys;
    start,fx=xs,fy=ys;
    m=m+1;
    if (m == 7) { m=0; n=n+1;}
  };
  dynap,fastune,turns=1024;
  endtrack;

  system, "rm -rf temp/dynap";
  system, "rm -rf temp/dynaptune";
  system, "rm -rf temp/footprint";
  write,table=dynap,file="temp/dynap";
  write,table=dynaptune,file="temp/dynaptune";
```
:warning: This code is reading a public folder
```fortran
  system,"/afs/cern.ch/work/f/frs/public/slap/bin/foot < temp/dynaptune > temp/footprint";
  /* system,"foot < temp/dynaptune > temp/footprint"; */

  
  seqedit,sequence=lhcBIM;
  cycle,start=IP3;
  endedit;
};

```
## PLOTFOOTPRINT 
This function is plotting the tune footprint.
It takes as inputs the

- beam to analyze (**BIM**). It will use the associated sequence.
- the tune space interval to plot (**qxmin**,**qxmax**,**qymin**,**qymax**)

A fortran executable is needed to plot the footprint (**fillfoottable**).
:question: should this routine be in the BB macros?
```fortran
PLOTFOOTPRINT(BIM,qxmin,qxmax,qymin,qymax) : macro = {
  use,sequence=lhcBIM;
  delete,table=foottable;
  create,table=foottable,column=dQ1,dQ2;
```
:warning: One should use a centralized version of the **fillfoottable** code.
```fortran
  system,"slhc/beambeam/fillfoottable";
  call,file="temp/fillfoottable.madx";
  plot,style=100,noversion=true,nolegend=true,title=Footprint-BIM,table=foottable,
      colour=2,haxis=dq1,vaxis=dq2,hmin=qxmin,hmax=qxmax,vmin=qymin,vmax=qymax;
};

```
## LEVEL_OFFSET_COMMON
This macro takes the

- target luminosity value (**TARGET_LUMI**)
- the number of the IP (**nIP**)
and compute the $\sqrt{\log(\frac{\rm actual~luminosity}{\rm target~luminosity})}$ (**offlvl_log**).

From **offlvl_log** one can compute the separation in the crossing plane or in the parallel plane with the macros **LEVEL_TRANSVERSE_OFFSET_FOR** or **LEVEL_PARALLEL_OFFSET_FOR**, respectively.

The number of bunch interactions should be available in the mask as:
**nco_IP1**= 2064;
**nco_IP5**= nco_IP1;
**nco_IP2**= 1692;
**nco_IP8**= 1765;

:warning: It uses only the madB1 beam.
```fortran
LEVEL_OFFSET_COMMON(TARGET_LUMI,nIP): macro = {

  use,sequence=lhcb1;
  twiss;
```
Definition of the $\sigma_x$ [m], $\sigma_y$ [m], $\sigma_z$ [m], intensity [ppb], **px** and **py** of the madB1.
```fortran
  offlvl_sx= sqrt(beam%lhcb1->ex * table(TWISS,IPnIP,betx));
  offlvl_sy= sqrt(beam%lhcb1->ey * table(TWISS,IPnIP,bety));
  offlvl_sigz= beam%lhcb1->sigt;
  offlvl_int = beam%lhcb1->npart;
  offlvl_px = table(TWISS,IPnIP,px);
  offlvl_py = table(TWISS,IPnIP,py);
```
:warning: It assumes only horizontal or vertical crossings.
Define accordingly

- the crossing semi-angle (**offlvl_phi_2**)
- the $\sigma$ in the crossing plane (**offlvl_sigX**)
- the $\sigma$ in the parallel plane (**offlvl_sigP**)
```fortran

  if (abs(offlvl_px)>abs(offlvl_py)) {
```
Horizontal Crossing
```fortran
    offlvl_phi_2 = offlvl_px;
    offlvl_sigX = offlvl_sx; !sigma in the crossing direction
    offlvl_sigP = offlvl_sy; !sigma in the parallel direction
  } else {
```
Vertical Crossing
```fortran
    offlvl_phi_2 = offlvl_py;
    offlvl_sigX = offlvl_sy; !sigma in the crossing direction
    offlvl_sigP = offlvl_sx; !sigma in the parallel direction
  };
```
Computation of the the effective $\sigma$ in the crossing plane assuming vanishing separation in the parallel plane.
```fortran
  offlvl_sigEff = sqrt(offlvl_sigX^2 + (offlvl_phi_2*offlvl_sigz)^2);
```
Computation of the luminosity.

:warning: Ultrarelativistic approximation.
```fortran
  offlvl_frev = CLIGHT/LHCLENGTH;
  offlvl_nb = nco_IPnIP;
  offlvl_L0=(offlvl_int^2*offlvl_frev*offlvl_nb)/(4*PI*offlvl_sigP*offlvl_sigEff)*1e-4;
```
**offlvl_log** computation.
```fortran
  offlvl_log=log(offlvl_L0/TARGET_LUMI);
  if (offlvl_log>0) {
    offlvl_log=sqrt(offlvl_log);
  } else {
    printf, text="LEVEL_OFFSET: the luminosity target is larger than the maximum luminosity: L0=%F Hz/cm2", value=offlvl_L0;
    offlvl_log=0;
  };
};

```
## LEVEL_PARALLEL_OFFSET_FOR
Auxiliary macro for the offset leveling in the parallel plane.
The macro takes the

- target luminosity value (**TARGET_LUMI**)
- the number of the IP (**nIP**)
and using the **LEVEL_OFFSET_COMMON** compute the IP normalized separation in the parallel plane (**halonIP**).
```fortran
LEVEL_PARALLEL_OFFSET_FOR(TARGET_LUMI, nIP): macro = {
  exec LEVEL_OFFSET_COMMON(TARGET_LUMI,nIP);
  halonIP = 2*offlvl_log;
  printf, text="Set%g halo to %f sigma, the lumi is reduced from %F Hz/cm2 to %F Hz/cm2", value=nIP,halonIP,offlvl_L0,TARGET_LUMI;
};

```
## LEVEL_TRANSVERSE_OFFSET_FOR
Auxiliary macro for the offset leveling in the transverse plane.
The macro takes the

- target luminosity value (**TARGET_LUMI**)
- the number of the IP (**nIP**)
and using the **LEVEL_OFFSET_COMMON** compute the IP normalized separation in the transverse plane (**halonIP**).
```fortran
LEVEL_TRANSVERSE_OFFSET_FOR(TARGET_LUMI, nIP): macro = {
  exec LEVEL_OFFSET_COMMON(TARGET_LUMI,nIP);
  halonIP = 2*offlvl_log * offlvl_sigEff/offlvl_sigX;
  printf, text="Set%g halo to %f sigma, the lumi is reduced from %F Hz/cm2 to %F Hz/cm2", value=nIP,halonIP,offlvl_L0,TARGET_LUMI;
};
```
