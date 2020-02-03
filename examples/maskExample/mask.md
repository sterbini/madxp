## Header and contributors
This file (mask) is the results of the work of many contributors. Aknowledgments go to

- **S. Fartoukh**
- **M. Giovannozzi**
- **R. De Maria**
- **F. Van Der Veken**
- **D. Pellegrini**

The first steps of the mask is to assign the proper symbolic links used afterward for calling

- sequences
- optics file strenght
- macros
and to clean the **temp** folder.

Then the **macro.madx** is called (it contains the *slicing* macros).

One defines few flags:

- **mylhcbeam**
- **not_a_mask** (to remove the masked values)
- **correct_magnetic_error** (and **correct_for_D2**, **correct_for_MCBX**)
- **choose_flat_optics** (as an alternative to round optics).

The thick LHC sequence is then called, completed with HL-LHC hardware and transformed in thin lens.

Additional place holders can be installed in  this sequence if **correct_magnetic_error** is set.

The sequences are then cycled in IP3.

One sets the energy and the octupole current.

One defines few flags:

- **ON_COLLISION**
- **ON_BB_SWITCH**
- and the bunch coarse spacing.

The the beam parameters such as

- normalized emittances
- bunch length at collision
are defined.

The the geometrical emittances are computed.

Then integer tunes are defined and depending on the energy also the fractional tune.
The thin lens strength ade called.
The beam are then defined and associated to the sequences.

The optics is then tested without crossing angle.

The crossing orbits are defined, with CC, spectrometers, solenoids.

The crossing knobs are printed, saves and disabled.

The optics is checked.

The crossing scheme is restored and checked.

Now the BB macro is called and the main BB parameters are set.

The leveling by separation is configured.
With the on_disp=0 the nominal crossing (with leveling by separation) is recorded.

One install the BB marker, calculate the BB elens from the marker position, install the BB lens,
print the BB lenses.

Then one install the CC for the weak beam and verify the installation for the long-range and the head-on.

Then the BB markers are removed.

At this stage, the optics correction part starts.
## Links 
The symbolic link should discriminate optics dependent links (e.g., sequences, strenghts files,...)
and optics independent ones (e.g., beam-beam macros).
```fortran

  option, warn,info;
```
In the **temp** folder we will store some intermediate output files.
:question: Should we remove the *temp* folder? I would say yes.
```fortran
  system, "rm -rf temp";
  system, "mkdir temp";
```
the **db5** link stores the multipole errors data
```fortran
  system, "ln -fns /afs/cern.ch/eng/lhc/optics/V6.503 db5";
```
the **lhc** link stores the present description of the machine sequence
```fortran
  system, "ln -fns /afs/cern.ch/eng/lhc/optics/runIII lhc";
```
the **slhc** link stores the HL-LHC description of the machine sequence and the needed toolkit macros
:question: are those macros optics independent?
```fortran
  system, "ln -fns /afs/cern.ch/eng/lhc/optics/HLLHCV1.4 slhc";
```
the **wise** link stores the error seeds for injection and collision
```fortran
  system, "ln -fns /afs/cern.ch/eng/lhc/optics/errors/0705 wise";
```
:warning: The **fidel** folder is not directly used in this file.
```fortran
  system, "ln -fns /afs/cern.ch/eng/lhc/optics/V6.503/WISE/After_sector_3-4_repair fidel";
```
:warning: Testing the *official* repository
```fortran
  system, "ln -fns /afs/cern.ch/eng/lhc/optics/beambeam_macros bbtoolkit";
  
  option, -echo,-info;

```
## Calling main macros file
:warning: This seems to be optics dependent since it is pointing to **slhc**
:warning: To be documented.
```fortran
  call, file="slhc/toolkit/macro.madx";        !Call some macro facilities

```
## Set the beam flag
**mylhcbeam** is the variable that sets the beam to track

- 1 : LHC beam 1 (clockwise)
- 2 : LHC beam 2 (clockwise)
- 4 : LHC beam 2 (counterclockwise)
:warning: This parameter is heavily used in the mask and in the BB macros
```fortran
  mylhcbeam=1; !LHC beam 1 (clockwise), LHC beam 2 (clockwise), LHC beam 2 (counterclockwise)

```
## Set the mask flag
Set this flag if the file is not used as a mask file (sets 1 for True)
```fortran
  not_a_mask=1;

```
## Set the correction flags
If you set this flag to 0 all the magnetic correction sections will be skipped.
```fortran
  correct_magnetic_error=0;
  if (correct_magnetic_error==1){
```
Set this flag to correct the errors of D2 in the NLC (warning: for now only correcting b3 of D2, still in development)
```fortran
    correct_for_D2=0;
```
Set this flag to correct the errors of MCBXF in the NLC (warning: this might be less reproducible in reality, use with care)
```fortran
    correct_for_MCBX=0;
  }
```
## Set the flag for the flat optics. 
```fortran
  choose_flat_optics=0;

```
## Manual Thin Sequence building
```fortran
  option, -echo,-warn,-info;
  if (mylhcbeam==4){
    call,file="lhc/lhcb4.seq";
  } 
  else {
    call,file="lhc/lhc.seq";
  };
  option, -echo,warn,-info;

```
## Install HL-LHC
:question: Should we target to have a common mask for LHC and HL-LHC? Probably not.
```fortran
  call,file="slhc/hllhc_sequence.madx";

```
## Slicing the sequence
This macro is in the [general macro](#Calling-main-macros-file).
```fortran
  exec, myslice;

```
## Adding place holders of the corrections
```fortran
  if (correct_magnetic_error==1):{
    call,file="slhc/errors/install_mqxf_fringenl.madx";    !adding fringe place holder
    call,file="slhc/errors/install_MCBXFAB_errors.madx";   !adding D1 corrector placeholders in IR1/5 (for errors)
    call,file="slhc/errors/install_MCBRD_errors.madx";     !adding D2 corrector placeholders in IR1/5 (for errors)
  }

```
## Cycling sequence to IP3 
The cycling is mandatory to find closed orbit in collision in the presence of errors.
It is also a good solution to have IR1/2/5/8 with monotonic $s$-position.
```fortran
  if (mylhcbeam<3){
    seqedit,sequence=lhcb1;flatten;cycle,start=IP3;flatten;endedit;
  };
  seqedit,sequence=lhcb2;flatten;cycle,start=IP3;flatten;endedit;

```
## Set the total energy flag
The NRJ= 450.0 or NRJ= 7000.0  is for for injection or collision respectively.
```fortran
  NRJ= 7000.0 ; 

```
## Set the octupole flag
The current of the Laundau octupole (some possible values are 20 A at inj and -570A at collision).

:warning: The value of this knob depends of the specif machine you want to simulate.
```fortran
  I_MO=1.000000e+02;

```
## Set the BB flag
General switch to run the halo settings of IP2/8 collision
```fortran
  ON_COLLISION:=1;
```
General switch to install bb lens
```fortran
  ON_BB_SWITCH:=1;

```
## Set bunch separation 
:warning: This is an approximate separation used only to discriminate the filling pattern (e.g., "25" vs "50" ns)
```fortran
  b_t_dist :=25.;  !bunch separation [ns]

```
## Set geometrical emittances
:construction: For consistency, all the other masked variable should be included in a similar **if** block.
```fortran
  if (not_a_mask==1){
    emittance_norm := 2.5e-6;
    Nb_0:=2.2E11;
  }
  else {
     emittance_norm := 2.300000e+00*1.0E-6;
      Nb_0:=2.250000e+11;
  };

```
## Set sigt_coll
Bunch length [m] in collision
```fortran
  sigt_col=0.075; 

```
## Compute normalized emittances 
```fortran
  gamma_rel      := NRJ/pmass;
```
:construction: Here we assume $\beta_r=1$.
```fortran
  epsx:=emittance_norm /gamma_rel;
  epsy:=emittance_norm /gamma_rel;

```
## Set integer tunes
```fortran
  qx00  = 62.0;  !integer h tune
  qy00  = 60.0;  !integer v tune
```
:construction: I would compute the tune split starting from **qx00** and **qy00**.
```fortran
  tsplit= 2.0;   !new tune split

```
## Call optics file, define the fractional tunes and chromaticity and beams
The rational is to chose the optics, tune and chromaticity of the beams
as function of the beam energy (i.e., injection or collision).
:warning: I would use **<=** and a threshold of 5000 GeV for both if
:warning: The chromaticity is implicitly assumed to be  the same in the H/V planes.
```fortran
  if (NRJ<4999.9999){
```
Injection optics in thin lens
```fortran
    call,file="slhc/ramp/opt_inj_6000_thin.madx";  !beta* [m]=6/10/6/10 in IR1/2/5/8
    qx0 = 62.27;   qy0 = 60.295;  qprime = 1.500000e+01;
    if (mylhcbeam<3){
      Beam,particle=proton,sequence=lhcb1,energy=NRJ,sigt=0.130,bv=1,NPART=Nb_0,sige=4.5e-4,ex=epsx,ey=epsy;
    };
    Beam,particle=proton,sequence=lhcb2,energy=NRJ,sigt=0.130,bv=-bv_aux,NPART=Nb_0,sige=4.5e-4,ex=epsx,ey=epsy;
  };

  if (NRJ>5000.0000){
```
Here we can chose the flat or round option
```fortran
    if (choose_flat_optics==1) {
      call,file="slhc/flat/opt_flatvh_75_300_1500_thin.madx";
    } else {
      call,file="slhc/round/opt_round_150_1500_thin.madx";
    };
    qx0 = 62.31;   qy0 = 60.32;  qprime = 1.500000e+01;
```
Correction of residual Q'' by MO's
:question: Is it used in a macro? It is not used in this file.
```fortran
    ON_QPP     :=0;  
```
Correction of spurious dispersion (if 1)
:warning: This **ON_DISP** is set also in the crossing angle sections.
```fortran
    ON_DISP    :=1;  
```
:warning: I would consider to explicitly put to **ON_QPP** and **ON_DISP** to 0 also in the previous **if**.
```fortran
    if (mylhcbeam<3){
      Beam,particle=proton,sequence=lhcb1,energy=NRJ,sigt=sigt_col,bv=1,
          NPART=Nb_0,sige=1.1e-4,ex=epsx,ey=epsy;
    };
    Beam,particle=proton,sequence=lhcb2,energy=NRJ,sigt=sigt_col,bv=-bv_aux,
        NPART=Nb_0,sige=1.1e-4,ex=epsx,ey=epsy;
  };

```
## Test of optics before crossings definition
:warning: Do we need to control the **mux_ip15** and **muy_ip15** in a this mask?
```fortran

  /*
```
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++;
  Rematch IP1 IP5 phase
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++;
nominal round: mux_ip15 = 31.21038468 ; muy_ip15 = 30.37288037 ;
nominal injection: mux_ip15 = 31.19538482 ; muy_ip15 = 30.36788031 ;

mux_ip15 = 31.21038468;
muy_ip15 = 31.19538482;

call,file="slhc/toolkit/make_ip15phase.madx";
call,file=slhc/toolkit/make_ip15phase_tm.madx; !use phase-trombone instead
call,file=slhc/toolkit/delete_ip15phase_tm.madx; !remove phase trombone

```fortran
  */
```
test new optics
```fortran
  if (mylhcbeam==1){
    exec,check_ip(b1);
  } else {
    exec,check_ip(b2);
  };
  mux_ip15_ref=table(twiss,IP1,mux)-table(twiss,IP5,mux);
  muy_ip15_ref=table(twiss,IP1,muy)-table(twiss,IP5,muy);
  value,mux_ip15_ref,muy_ip15_ref;

```
## Python: Test of optics before crossings definition
```python
# python code
pythonDictionary['twiss']=madx.table.twiss.dframe()
pythonDictionary['summ']=madx.table.summ.dframe()
```
## Set crossing angle, separations, spectrometers and crabbing 
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++;
Set crossing angle and separations knobs
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++;

phi_IR1 = 0.000;    phi_IR5 =   90.000;    !these are automatically set by the optics
:warning: What is the relation of **phi_IR1** and **phi_IR5** for round and flat?
:construction: Define on_a1...on_o8...
```fortran
  if (NRJ<4999.9999){
    if (not_a_mask==1){
       xing15=295; 
    } 
    else {
       xing15=2.450000e+02; 
    };
    on_x1= xing15;      on_sep1=-2;  
    on_x5= xing15;      on_sep5= 2;  
    on_x2= 170;         on_sep2= 3.5;
    on_x8=-170;         on_sep8=-3.5;
    on_a1=  0;          on_o1= 0;  
    on_a5=  0;          on_o5= 0;
    on_a2=-40;          on_o2= 0;          
    on_a8=-40;          on_o8= 0;
    on_crab1=0;
    on_crab5=0;
    on_disp=0;
  };
  if (NRJ>5000.0000){
    if (not_a_mask==1){
       xing15=250;
    }
    else {
      xing15=2.450000e+02;
    };
    on_x1= xing15;      on_sep1=-0.75;  
    on_x5= xing15;      on_sep5= 0.75;  
    on_x2= 170;         on_sep2= 1;
    on_x8=-200;         on_sep8=-1;
    on_a1= 0;           on_o1= 0;           
    on_a5= 0;           on_o5= 0;
    on_a2= 0;           on_o2= 0;
    on_a8= 0;           on_o8= 0;
    on_crab1=-190;
    on_crab5=-190;           
    on_disp=1;
  };
```
spectrometers in experiments
```fortran
  on_alice=7000/nrj;
  on_lhcb =7000/nrj;
```
Avoid crabbing more than the crossing angle
```fortran
  if ( abs(on_crab1)>abs(xing15) && on_crab1 <> 0) {on_crab1 = abs(on_crab1)/on_crab1 * abs(xing15);}
  if ( abs(on_crab5)>abs(xing15) && on_crab5 <> 0) {on_crab5 = abs(on_crab5)/on_crab5 * abs(xing15);}
```
solenoids in experiments
:question: Why they are off by default?
```fortran
  on_sol_atlas=0;
  on_sol_cms=  0;
  on_sol_alice=0; 

```
## Print the crossing knobs
```fortran
  exec, print_crossing_knobs;

```
## Save the crossing knobs
```fortran
  exec, crossing_save;

```
## Disable the crossing knobs to test the optics
```fortran
 exec, crossing_disable;

```
## Test of optics with disabled crossing knobs
Check of the optics at the IP1/2/5/8 with crossing disabled.
```fortran
  system,"rm -f twiss.b1";
  system,"rm -f twiss.b2";
  
  if (mylhcbeam<3){
    use, sequence=lhcb1;
    select,flag=twiss,clear;
    select, flag=twiss, pattern="IP1",   column=name,s,betx,bety,alfx,alfy,dx,dpx,mux,muy;
    select, flag=twiss, pattern="IP2",   column=name,s,betx,bety,alfx,alfy,dx,dpx,mux,muy;
    select, flag=twiss, pattern="IP5",   column=name,s,betx,bety,alfx,alfy,dx,dpx,mux,muy;
    select, flag=twiss, pattern="IP8",   column=name,s,betx,bety,alfx,alfy,dx,dpx,mux,muy;
    twiss,sequence=lhcb1,file=twiss.b1;system,"cat twiss.b1";
  };
```
:warning: In the **if (mylhcbeam<3)** there is no **else** for the ***mylhcbeam=4***...
```fortran
  use, sequence=lhcb2;
  select,flag=twiss,clear;
  select, flag=twiss, pattern="IP1",   column=name,s,betx,bety,alfx,alfy,dx,dpx,mux,muy;
  select, flag=twiss, pattern="IP2",   column=name,s,betx,bety,alfx,alfy,dx,dpx,mux,muy;
  select, flag=twiss, pattern="IP5",   column=name,s,betx,bety,alfx,alfy,dx,dpx,mux,muy;
  select, flag=twiss, pattern="IP8",   column=name,s,betx,bety,alfx,alfy,dx,dpx,mux,muy;
  twiss, sequence=lhcb2,file=twiss.b2;system,"cat twiss.b2";

  system,"rm -f twiss.b1";
  system,"rm -f twiss.b2";

```
## Restore the crossing scheme
After an optics test with the flat orbit the crossing is restored.
```fortran
  exec,crossing_restore;

```
## Test the IP positions and angles
The angle are checked in the IP1/2/5/8.
```fortran
  if (mylhcbeam<3){
    Use, sequence=lhcb1;
    select,flag=twiss,clear;
    select, flag=twiss, pattern="IP1",   column=name,s,x,y,px,py;
    select, flag=twiss, pattern="IP2",   column=name,s,x,y,px,py;
    select, flag=twiss, pattern="IP5",   column=name,s,x,y,px,py;
    select, flag=twiss, pattern="IP8",   column=name,s,x,y,px,py;
    twiss, sequence=lhcb1, file=twiss.b1;system,"cat twiss.b1";
  };
```
Definition of the x,y,px,py for the strong beam.
```fortran
  xnom1=table(twiss,IP1,x);pxnom1=table(twiss,IP1,px);ynom1=table(twiss,IP1,y);pynom1=table(twiss,IP1,py);
  xnom2=table(twiss,IP2,x);pxnom2=table(twiss,IP2,px);ynom2=table(twiss,IP2,y);pynom2=table(twiss,IP2,py);
  xnom5=table(twiss,IP5,x);pxnom5=table(twiss,IP5,px);ynom5=table(twiss,IP5,y);pynom5=table(twiss,IP5,py);
  xnom8=table(twiss,IP8,x);pxnom8=table(twiss,IP8,px);ynom8=table(twiss,IP8,y);pynom8=table(twiss,IP8,py);

  Use, sequence=lhcb2;
  select,flag=twiss,clear;
  select, flag=twiss, pattern="IP1",   column=name,s,x,y,px,py;
  select, flag=twiss, pattern="IP2",   column=name,s,x,y,px,py;
  select, flag=twiss, pattern="IP5",   column=name,s,x,y,px,py;
  select, flag=twiss, pattern="IP8",   column=name,s,x,y,px,py;
  twiss, sequence=lhcb2, file=twiss.b2;system,"cat twiss.b2";

  value,xnom1,xnom2,xnom5,xnom8;
  value,ynom1,ynom2,ynom5,ynom8;
  value,pxnom1,pxnom2,pxnom5,pxnom8;
  value,pynom1,pynom2,pynom5,pynom8;

```
## Call the BB macros if ON_BB_SWITCH==1
```fortran
  if( ON_BB_SWITCH == 1){
```
call,file="slhc/beambeam2/macro_bb.madx";   !macros for beam-beam
```fortran
    call,file="bbtoolkit/macro_bb.madx"; !macros for beam-beam          
  };

```
## Define the main BB parameters
Default value for the number of additional parasitic encounters inside D1
```fortran
  n_insideD1 = 5;    
```
number of slices for head-on in IP1/2/5/8 (between 0 and 201)
```fortran
  nho_IR1= 11;        
  nho_IR2= 11;        
  nho_IR5= 11;        
  nho_IR8= 11;        

  if( ON_BB_SWITCH == 1){
    exec DEFINE_BB_PARAM;  !Define main beam-beam parameters
  };

```
## Setting halo collision in IP2/8 if ON_COLLISION is set.
```fortran
  if (ON_COLLISION==1){
```
Switch on Xscheme in precollision
```fortran
    on_disp=0;
    halo1=0;halo2=5;halo5=0;halo8=0;  !halo collision at 5 sigma's in Alice
```
number of collision/turn at IP1/2/5/8 - BCMS https://espace.cern.ch/HiLumi/WP2/Wiki/HL-LHC%20Parameters.aspx
```fortran
    nco_IP1= 2592;
    nco_IP5= nco_IP1;
    nco_IP2= 2288;
    nco_IP8= 2396;
    exec LEVEL_PARALLEL_OFFSET_FOR(2e33, 8); value,halo8;
```
Redefine the on_sep's accordingly
```fortran
    exec CALCULATE_XSCHEME(halo1,halo2,halo5,halo8);
```
Saving new crossing scheme with separation
:question: Is **on_dispaux** defined in the **crossing_save**?
```fortran
    on_disp=on_dispaux; !reset on_disp before saving
    exec, crossing_save;
  };

```
## Set on_disp to 0
```fortran
  on_disp=0; !more precise angles at IPs

```
## Record the nominal IP position and crossing angle
```fortran
  if(mylhcbeam==1) {use,  sequence=lhcb1;};
  if(mylhcbeam>1) {use,  sequence=lhcb2;};
  twiss;
  xnom1=table(twiss,IP1,x);pxnom1=table(twiss,IP1,px);ynom1=table(twiss,IP1,y);pynom1=table(twiss,IP1,py);
  xnom2=table(twiss,IP2,x);pxnom2=table(twiss,IP2,px);ynom2=table(twiss,IP2,y);pynom2=table(twiss,IP2,py);
  xnom5=table(twiss,IP5,x);pxnom5=table(twiss,IP5,px);ynom5=table(twiss,IP5,y);pynom5=table(twiss,IP5,py);
  xnom8=table(twiss,IP8,x);pxnom8=table(twiss,IP8,px);ynom8=table(twiss,IP8,y);pynom8=table(twiss,IP8,py);
  value,xnom1,xnom2,xnom5,xnom8;
  value,ynom1,ynom2,ynom5,ynom8;
  value,pxnom1,pxnom2,pxnom5,pxnom8;
  value,pynom1,pynom2,pynom5,pynom8;

```
## Install BB markers
```fortran
  if( ON_BB_SWITCH == 1){
    exec INSTALL_BB_MARK(b1);exec INSTALL_BB_MARK(b2);
  }

```
## Define BB lenses for both beams in all IR's and calculate # of encounters before D1
```fortran
  if( ON_BB_SWITCH == 1){
    exec CALCULATE_BB_LENS;
  }

```
## Install BB lenses
```fortran
  if( ON_BB_SWITCH == 1){
    on_ho1 =1; on_lr1l = 1; on_lr1r = 1; npara_1 = npara0_1 + n_insideD1;
    on_ho5 =1; on_lr5l = 1; on_lr5r = 1; npara_5 = npara0_5 + n_insideD1;
    on_ho2 =1; on_lr2l = 1; on_lr2r = 1; npara_2 = npara0_2 + n_insideD1;
    on_ho8 =1; on_lr8l = 1; on_lr8r = 1; npara_8 = npara0_8 + n_insideD1;
    if(mylhcbeam==1) {exec INSTALL_BB_LENS(b1);};
    if(mylhcbeam>1) {exec INSTALL_BB_LENS(b2);};
  }

```
## Print the lenses in bb_lenses.dat
```fortran
  if( ON_BB_SWITCH == 1){
    exec, PRINT_BB_LENSES;
  }

```
## Switch off the BB charge
```fortran
  if( ON_BB_SWITCH == 1){
    ON_BB_CHARGE := 0; 
  }

```
## Install CC for the weak beam
:question: How this step is related to the one of HO crabbing used in the BB macros?
```fortran
  if( ON_BB_SWITCH == 1){
    call,file="slhc/toolkit/enable_crabcavities.madx";
  }

  /* Plot b-b separation
  exec PLOT_BB_SEP(1,$npara_1);
  exec PLOT_BB_SEP(2,$npara_2);
  exec PLOT_BB_SEP(5,$npara_5);
  exec PLOT_BB_SEP(8,$npara_8);
  */
```
/*
if (mylhcbeam<3){ seqedit,sequence=lhcb1;flatten;cycle,start=IP1;endedit; };
seqedit,sequence=lhcb2;flatten;cycle,start=IP1;endedit;
## Verify the installation of the thin lenses in twiss_bb.b1/2
For the long-range
```fortran
  if( ON_BB_SWITCH == 1){
   if (mylhcbeam<3){
    use,sequence=lhcb1;
    select,flag=twiss,clear;
    select,flag=twiss,class=marker,pattern=PAR.*L1,range=mbxf.4l1..4/IP1.L1,column=s,name,betx,bety,alfx,alfy,mux,muy,x,y,px,py;
    select,flag=twiss,class=marker,pattern=PAR.*L5,range=mbxf.4l5..4/IP5,column=s,name,betx,bety,alfx,alfy,mux,muy,x,y,px,py;
    select,flag=twiss,class=marker,pattern=PAR.*R1,range=IP1/mbxf.4r1..1,column=s,name,betx,bety,alfx,alfy,mux,muy,x,y,px,py;
    select,flag=twiss,class=marker,pattern=PAR.*R5,range=IP5/mbxf.4r5..1,column=s,name,betx,bety,alfx,alfy,mux,muy,x,y,px,py;
    select,flag=twiss,class=marker,pattern=IP1,column=s,name,betx,bety,alfx,alfy,mux,muy,x,y,px,py;
    select,flag=twiss,class=marker,pattern=IP5,column=s,name,betx,bety,alfx,alfy,mux,muy,x,y,px,py;
    twiss,file=twiss_bb.b1;system,"cat twiss_bb.b1";
    };

    use,sequence=lhcb2;
    select,flag=twiss,clear;
    select,flag=twiss,class=marker,pattern=PAR.*L1,range=mbxf.4l1..4/IP1.L1,column=s,name,betx,bety,alfx,alfy,mux,muy,x,y,px,py;
    select,flag=twiss,class=marker,pattern=PAR.*L5,range=mbxf.4l5..4/IP5,column=s,name,betx,bety,alfx,alfy,mux,muy,x,y,px,py;
    select,flag=twiss,class=marker,pattern=PAR.*R1,range=IP1/mbxf.4r1..1,column=s,name,betx,bety,alfx,alfy,mux,muy,x,y,px,py;
    select,flag=twiss,class=marker,pattern=PAR.*R5,range=IP5/mbxf.4r5..1,column=s,name,betx,bety,alfx,alfy,mux,muy,x,y,px,py;
    select,flag=twiss,class=marker,pattern=IP1,column=s,name,betx,bety,alfx,alfy,mux,muy,x,y,px,py;
    select,flag=twiss,class=marker,pattern=IP5,column=s,name,betx,bety,alfx,alfy,mux,muy,x,y,px,py;
    twiss,file=twiss_bb.b2;system,"cat twiss_bb.b2";
  }
  
```
### Prepare the head-on
```fortran
  if( ON_BB_SWITCH == 1){
    if(mylhcbeam==1) {use,sequence=lhcb1;};
    if(mylhcbeam>1) {use,sequence=lhcb2;};

    select,flag=twiss,clear;
    select,flag=twiss,pattern=HO,class=beambeam,column=s,name,betx,bety,alfx,alfy,mux,muy,x,y,px,py;
    twiss,file=twiss_bb;system,"cat twiss_bb";
  }

```
## Remove BB markers
```fortran
  if( ON_BB_SWITCH == 1){
    exec REMOVE_BB_MARKER;
  };
  /*
```
Make and plot footprint (at 6 sigmas)
```fortran
  ON_BB_CHARGE := 1;
```
Switch on Xscheme
```fortran
  exec, crossing_restore;

  nsigmax=6;

  if(qx0-qx00<0.3){
    if(mylhcbeam==1) {exec MAKEFOOTPRINT(b1);exec PLOTFOOTPRINT(b1,0.2795,0.2805,0.3095,0.3105);};
    if(mylhcbeam>1) {exec MAKEFOOTPRINT(b2);exec PLOTFOOTPRINT(b2,0.2795,0.2805,0.3095,0.3105);};
  };
  if(qx0-qx00>0.3){
    if(mylhcbeam==1) {exec MAKEFOOTPRINT(b1);exec PLOTFOOTPRINT(b1,0.300,0.315,0.310,0.325);};
    if(mylhcbeam>1) {exec MAKEFOOTPRINT(b2);exec PLOTFOOTPRINT(b2,0.300,0.315,0.310,0.325);};
  };
  ON_BB_CHARGE := 0;
  exec,crossing_disable;
  */
```
Remove bb lens for both beams
exec REMOVE_BB_LENS;
 =============================================================================  UNTIL FOR GIANNI
## Start the optics correction
```fortran




  print, text="=======================================";
  print, text="======  OPTICS PARAMETERS: BASE  ======";
  print, text="=======================================";
  call, file="slhc/toolkit/get_optics_params.madx";

```
## Prepare the nominal twiss tables

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++;
              Prepare nominal twiss tables
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++;
```fortran
  if (mylhcbeam==1) { use,sequence=lhcb1; } else { use,sequence=lhcb2; };

  /*
  twiss;
  x.ip1=table(twiss,IP1,x);px.ip1=table(twiss,IP1,px);
  y.ip1=table(twiss,IP1,y);px.ip1=table(twiss,IP1,py); //irrelevant when recycling the sequences
  */


  twiss, table=nominal;   // used by orbit correction
  beta.ip1=table(twiss,IP1,betx);value,beta.ip1;

```
## Dump the temp/optics0_MB.mad file
print nominal optics parameter at the MB, MQS and MSS for
b2, b3, b4, b5, a2 and a3 correction
```fortran
  if (correct_magnetic_error==1){
    select, flag=twiss, clear;
    select, flag=twiss,pattern=MB\.   ,class=multipole,column=name,k0L,k1L,betx,bety,dx,mux,muy;
    select, flag=twiss,pattern=MBH\.   ,class=multipole,column=name,k0L,k1L,betx,bety,dx,mux,muy;
    select, flag=twiss,pattern=MQT\.14,class=multipole,column=name,k0L,k1L,betx,bety,dx,mux,muy;
    select, flag=twiss,pattern=MQT\.15,class=multipole,column=name,k0L,k1L,betx,bety,dx,mux,muy;
    select, flag=twiss,pattern=MQT\.16,class=multipole,column=name,k0L,k1L,betx,bety,dx,mux,muy;
    select, flag=twiss,pattern=MQT\.17,class=multipole,column=name,k0L,k1L,betx,bety,dx,mux,muy;
    select, flag=twiss,pattern=MQT\.18,class=multipole,column=name,k0L,k1L,betx,bety,dx,mux,muy;
    select, flag=twiss,pattern=MQT\.19,class=multipole,column=name,k0L,k1L,betx,bety,dx,mux,muy;
    select, flag=twiss,pattern=MQT\.20,class=multipole,column=name,k0L,k1L,betx,bety,dx,mux,muy;
    select, flag=twiss,pattern=MQT\.21,class=multipole,column=name,k0L,k1L,betx,bety,dx,mux,muy;
    select, flag=twiss,class=MQS                      ,column=name,k0L,k1L,betx,bety,dx,mux,muy;
    select, flag=twiss,class=MSS                      ,column=name,k0L,k1L,betx,bety,dx,mux,muy;
    select, flag=twiss,class=MCO                      ,column=name,k0L,k1L,betx,bety,dx,mux,muy;
    select, flag=twiss,class=MCD                      ,column=name,k0L,k1L,betx,bety,dx,mux,muy;
    select, flag=twiss,class=MCS                      ,column=name,k0L,k1L,betx,bety,dx,mux,muy;
    twiss,  file='temp/optics0_MB.mad';
```
print nominal optics parameter at the D1, MQX and triplet corrector
for triplet correction
```fortran
    select, flag=twiss, clear;
    select, flag=twiss, pattern=MQX  , class=multipole, column=name,betx,bety,x,y;
    select, flag=twiss, pattern=MBX  , class=multipole, column=name,betx,bety,x,y;
    select, flag=twiss, pattern=MBRC , class=multipole, column=name,betx,bety,x,y;
    if (correct_for_D2==1){
      select, flag=twiss, pattern=MBRD , class=multipole, column=name,betx,bety,x,y;
    };
    select, flag=twiss, pattern=MQSX                  , column=name,betx,bety,x,y;
    select, flag=twiss, pattern=MCQSX                 , column=name,betx,bety,x,y;
    select, flag=twiss, pattern=MCSX                  , column=name,betx,bety,x,y;
    select, flag=twiss, pattern=MCTX                  , column=name,betx,bety,x,y;
    select, flag=twiss, pattern=MCOSX                 , column=name,betx,bety,x,y;
    select, flag=twiss, pattern=MCOX                  , column=name,betx,bety,x,y;
    select, flag=twiss, pattern=MCSSX                 , column=name,betx,bety,x,y;
    select, flag=twiss, pattern=MCDX                  , column=name,betx,bety,x,y;
    select, flag=twiss, pattern=MCDSX                 , column=name,betx,bety,x,y;
    select, flag=twiss, pattern=MCTSX                 , column=name,betx,bety,x,y;
    if (correct_for_MCBX==1){
      select, flag=twiss, pattern=MCBXF, class=multipole, column=name,betx,bety,x,y;
    };
    twiss,  file='temp/optics0_inser.mad';
  }  

```
## Call first time slhc/toolkit/BetaBeating.madx
```fortran
  if (correct_magnetic_error==1){
    call, file="slhc/toolkit/BetaBeating.madx";
  }
```
## Disable crossing bumps
```fortran
  if (correct_magnetic_error==1){
    exec, crossing_disable;
  }

```
## Align separation magnets

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                  Align separation magnets
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


if(mylhcbeam==1){
 call, file = "db5/measured_errors/align_D1_slices.b1.madx";
 call, file = "db5/measured_errors/align_D2_slices.b1.madx";
 call, file = "db5/measured_errors/align_D3_slices.b1.madx";
 call, file = "db5/measured_errors/align_D4_slices.b1.madx";
};

if(mylhcbeam>1){
 call, file = "db5/measured_errors/align_D1_slices.b2.madx";
 call, file = "db5/measured_errors/align_D2_slices.b2.madx";
 call, file = "db5/measured_errors/align_D3_slices.b2.madx";
 call, file = "db5/measured_errors/align_D4_slices.b2.madx";
};
```fortran
  if (correct_magnetic_error==1){
    call,file="slhc/toolkit/align_sepdip.madx";
```
exec,align_mbxw;  !V6.503  D1
exec,align_mbrc15;!V6.503 D2 in IR15
```fortran
    exec,align_mbx15; !HL-LHC D1
    exec,align_mbrd15;!HL-LHC D2 in IR15

    exec,align_mbx28; !V6.503 D1 in IR28
    exec,align_mbrc28;!V6.503 D2 in IR28
    exec,align_mbrs;  !V6.503 D3 in IR4
    exec,align_mbrb;  !V6.503 D4 in IR4
  }
```
## Align 11T dipoles
```fortran
  if (correct_magnetic_error==1){
    call,file="slhc/toolkit/align_mbh.madx"; !align 11T dipoles
  }
```
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        Call error subroutines (nominal machine and new IT/D1)
                        and error tables
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
## Error routine and measured error table for nominal LHC
```fortran
  if (correct_magnetic_error==1){
    call,file="db5/measured_errors/Msubroutines_new.madx";
    call,file="db5/measured_errors/Msubroutines_MS_MSS_MO_new.madx";
    call,file="db5/toolkit/Orbit_Routines.madx";
    call,file="slhc/errors/SelectLHCMonCor.madx";
    readtable, file="db5/measured_errors/rotations_Q2_integral.tab";
  }

```
## Error routine and error table for new IT/D1/D2/Q4/Q5
```fortran
  if (correct_magnetic_error==1){

    useMQXFAB=0;

    call,file="slhc/errors/macro_error.madx";   !macros for error generation in the new IT/D1's

    if (useMQXFAB==1) {
      call,file="slhc/errors/ITa_errortable_v5"; !target error table for the new IT
      call,file="slhc/errors/ITb_errortable_v5"; !target error table for the new IT
    } else {
      call,file="slhc/errors/ITbody_errortable_v5"; !target error table for the new IT
      call,file="slhc/errors/ITnc_errortable_v5"; !target error table for the new IT
      call,file="slhc/errors/ITcs_errortable_v5"; !target error table for the new IT
    };
    call,file="slhc/errors/D1_errortable_v1"; !target error table for the new D1

    call,file="slhc/errors/D2_errortable_v5"; !target error table for the new D2
    if (correct_for_D2==1){
      call,file="slhc/errors/D2_empty_errortable"; !We are only correcting the b3 errors, put the other errors to zero
    };
```
value,Rr_MQXCD,Rr_MBXAB,Rr_MBRD,Rr_MQYY,Rr_MQYL;
a2R_MQXCD_inj:=20.00;a2R_MQXCD_col:=20.00;!up to 3 mrad roll of the new MQX's (1 mrad r.m.s)

b5M_MQXCD_col  :=  0.0000 ; b5U_MQXCD_col  :=  0.4200 ; b5R_MQXCD_col  :=  0.4200 ; !..Errors as in IT_errortable_v3
a5M_MQXCD_col  :=  0.0000 ; a5U_MQXCD_col  :=  0.4300 ; a5R_MQXCD_col  :=  0.4300 ; !..Errors as in IT_errortable_v3
a6M_MQXCD_col  :=  0.0000 ; a6U_MQXCD_col  :=  0.3100 ; a6R_MQXCD_col  :=  0.3100 ; !..Errors as in IT_errortable_v3
```fortran

    call,file="slhc/errors/MCBXFAB_errortable_v1";
    call,file="slhc/errors/MBH_errortable_v3";
    call,file="slhc/errors/MCBRD_errortable_v1";
  }
```
## Switch ON/OFF some multipole

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
               Switch ON/OFF some multipole
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
```fortran
  if (correct_magnetic_error==1){
    exec ON_ALL_MULT;
    ON_LSF=1;

    ON_A1s =  0 ; ON_A1r =  0 ; ON_B1s =  0 ; ON_B1r =  0;
    ON_A2s =  0 ; ON_A2r =  0 ; ON_B2s =  0 ; ON_B2r =  0;
    ON_A3s =  1 ; ON_A3r =  1 ; ON_B3s =  1 ; ON_B3r =  1;
    ON_A4s =  1 ; ON_A4r =  1 ; ON_B4s =  1 ; ON_B4r =  1;
    ON_A5s =  1 ; ON_A5r =  1 ; ON_B5s =  1 ; ON_B5r =  1;
    ON_A6s =  1 ; ON_A6r =  1 ; ON_B6s =  1 ; ON_B6r =  1;
    ON_A7s =  1 ; ON_A7r =  1 ; ON_B7s =  1 ; ON_B7r =  1;
    ON_A8s =  1 ; ON_A8r =  1 ; ON_B8s =  1 ; ON_B8r =  1;
    ON_A9s =  1 ; ON_A9r =  1 ; ON_B9s =  1 ; ON_B9r =  1;
    ON_A10s =  1; ON_A10r =  1; ON_B10s =  1; ON_B10r =  1;
    ON_A11s =  1; ON_A11r =  1; ON_B11s =  1; ON_B11r =  1;
    ON_A12s =  ON_LSF; ON_A12r = ON_LSF; ON_B12s = ON_LSF; ON_B12r =  ON_LSF;
    ON_A13s =  ON_LSF; ON_A13r = ON_LSF; ON_B13s = ON_LSF; ON_B13r =  ON_LSF;
    ON_A14s =  ON_LSF; ON_A14r = ON_LSF; ON_B14s = ON_LSF; ON_B14r =  ON_LSF;
    ON_A15s =  ON_LSF; ON_A15r = ON_LSF; ON_B15s = ON_LSF; ON_B15r =  ON_LSF;
  }
```
## Define the seed number

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Define the seed number (for statistical error assignment in the new IT/D1)
and call the corresponding measured error table for nominal LHC magnets
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
```fortran
  if (correct_magnetic_error==1){
    if (not_a_mask==1){
      if (NRJ<4999.999) {readtable, file="wise/injection_errors-emfqcs-1.tfs" ;};
      if (NRJ>5000.000) {readtable, file="wise/collision_errors-emfqcs-1.tfs" ;};
    } else {
      if (NRJ<4999.999) {readtable, file="wise/injection_errors-emfqcs-1.tfs" ;};
      if (NRJ>5000.000) {readtable, file="wise/collision_errors-emfqcs-1.tfs" ;};
    };
  }

```
## Apply field errors to MB magnets

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            apply field errors to MB magnets
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
```fortran
  if (correct_magnetic_error==1){
    call,   file="db5/measured_errors/Efcomp_MB.madx"  ;
  }
```
## Correct orbit distortion resulting from MB magnets
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    correct orbit distortion resulting from MB magnets
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
```fortran
  if (correct_magnetic_error==1){
    if((ON_A1S)^2+(ON_A1r)^2+(ON_B1S)^2+(ON_B1r)^2 >0){
      exec,   initial_micado(4);
      exec,   initial_micado(4);
    };
  }

```
## Apply field errors to all other magnets

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
          apply field errors to all other magnets
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Nominal LHC magnets
Separation Dipoles
```fortran
  if (correct_magnetic_error==1){

    call,   file="db5/measured_errors/Efcomp_MBRB.madx";
    call,   file="db5/measured_errors/Efcomp_MBRC.madx";
    call,   file="db5/measured_errors/Efcomp_MBRS.madx";
    call,   file="db5/measured_errors/Efcomp_MBX.madx" ;
    call,   file="db5/measured_errors/Efcomp_MBW.madx" ;
```
Quadrupoles
```fortran
    ON_B2Saux=on_B2S;on_B2S=0*ON_B2Saux;call,file="db5/measured_errors/Efcomp_MQW.madx" ; on_B2S=ON_B2Saux;
    ON_B2Saux=on_B2S;on_B2S=0*ON_B2Saux;call,file="db5/measured_errors/Efcomp_MQTL.madx"; on_B2S=ON_B2Saux;
    ON_B2Saux=on_B2S;on_B2S=0*ON_B2Saux;call,file="db5/measured_errors/Efcomp_MQMC.madx"; on_B2S=ON_B2Saux;
    ON_B2Saux=on_B2S;on_B2S=0*ON_B2Saux;call,file="db5/measured_errors/Efcomp_MQX.madx" ; on_B2S=ON_B2Saux;
    ON_B2Saux=on_B2S;on_B2S=0*ON_B2Saux;call,file="db5/measured_errors/Efcomp_MQY.madx" ; on_B2S=ON_B2Saux;
    ON_B2Saux=on_B2S;on_B2S=0*ON_B2Saux;call,file="db5/measured_errors/Efcomp_MQM.madx" ; on_B2S=ON_B2Saux;
    ON_B2Saux=on_B2S;on_B2S=0*ON_B2Saux;call,file="db5/measured_errors/Efcomp_MQML.madx"; on_B2S=ON_B2Saux;
    ON_B2Saux=on_B2S;on_B2S=0*ON_B2Saux;call,file="db5/measured_errors/Efcomp_MQ.madx"  ; on_B2S=ON_B2Saux;

    call, file="db5/measured_errors/Set_alignment_errors.madx";
```
New IT/D1/D2/Q4/Q5
```fortran
    if (not_a_mask==1){ myseed=1; } else { myseed=1; }
    eoption,seed=myseed+101;
    if (useMQXFAB==1) {
      call, file="slhc/errors/Efcomp_MQXFA.madx";      !new IT in IR1/5
      call, file="slhc/errors/Efcomp_MQXFB.madx";
    } else {
      call, file="slhc/errors/Efcomp_MQXFbody.madx"; !new IT in IR1/5
      call, file="slhc/errors/Efcomp_MQXFends.madx";                            !new IT in IR1/5
    };
    eoption,seed=myseed+102;call, file="slhc/errors/Efcomp_MBXAB.madx";    !new D1 in IR1/5
    if (correct_for_D2==1){
      use_average_errors_MBRD=1;   !using average errors for correction algorithm
    };
    eoption,seed=myseed+103;call, file="slhc/errors/Efcomp_MBRD.madx";   	!new D2 in IR1/5
    call, file="slhc/errors/Efcomp_MQY.madx";     !old Q4 in IR1/5, but switched places around IP1-5
    eoption,seed=myseed+106;call, file="slhc/errors/Efcomp_MCBXFAB.madx";  !new triplet correctors in IR1/5
    ON_B2saux=on_B2s;on_B2s=0; ON_B2raux=on_B2r;on_B2r=0;
    eoption,seed=myseed+107;call, file="slhc/errors/Efcomp_MBH.madx";
    on_B2s=ON_B2saux; on_B2r=ON_B2raux;
    eoption,seed=myseed+108;call, file="slhc/errors/Efcomp_MCBRD.madx";
```
exec show_error_newHLmagnet;

select, flag=error, clear;
select, flag=error, pattern=".";
esave,  file="error_all.tfs";
```fortran
  }

```
## Compute optics parameters after the errors
```fortran
  if (correct_magnetic_error==1){
    print, text="===============================================";
    print, text="======  OPTICS PARAMETERS: AFTER ERRORS  ======";
    print, text="===============================================";
    call, file="slhc/toolkit/get_optics_params.madx";
  }
```
## Set the arc octupoles

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
MO settings
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
```fortran

  brho:=NRJ*1e9/clight;
  if (mylhcbeam==1){
    KOF.A12B1:=Kmax_MO*I_MO/Imax_MO/brho; KOF.A23B1:=Kmax_MO*I_MO/Imax_MO/brho;
    KOF.A34B1:=Kmax_MO*I_MO/Imax_MO/brho; KOF.A45B1:=Kmax_MO*I_MO/Imax_MO/brho;
    KOF.A56B1:=Kmax_MO*I_MO/Imax_MO/brho; KOF.A67B1:=Kmax_MO*I_MO/Imax_MO/brho;
    KOF.A78B1:=Kmax_MO*I_MO/Imax_MO/brho; KOF.A81B1:=Kmax_MO*I_MO/Imax_MO/brho;
    KOD.A12B1:=Kmax_MO*I_MO/Imax_MO/brho; KOD.A23B1:=Kmax_MO*I_MO/Imax_MO/brho;
    KOD.A34B1:=Kmax_MO*I_MO/Imax_MO/brho; KOD.A45B1:=Kmax_MO*I_MO/Imax_MO/brho;
    KOD.A56B1:=Kmax_MO*I_MO/Imax_MO/brho; KOD.A67B1:=Kmax_MO*I_MO/Imax_MO/brho;
    KOD.A78B1:=Kmax_MO*I_MO/Imax_MO/brho; KOD.A81B1:=Kmax_MO*I_MO/Imax_MO/brho;
  };

  if (mylhcbeam>1){
    KOF.A12B2:=Kmax_MO*I_MO/Imax_MO/brho; KOF.A23B2:=Kmax_MO*I_MO/Imax_MO/brho;
    KOF.A34B2:=Kmax_MO*I_MO/Imax_MO/brho; KOF.A45B2:=Kmax_MO*I_MO/Imax_MO/brho;
    KOF.A56B2:=Kmax_MO*I_MO/Imax_MO/brho; KOF.A67B2:=Kmax_MO*I_MO/Imax_MO/brho;
    KOF.A78B2:=Kmax_MO*I_MO/Imax_MO/brho; KOF.A81B2:=Kmax_MO*I_MO/Imax_MO/brho;
    KOD.A12B2:=Kmax_MO*I_MO/Imax_MO/brho; KOD.A23B2:=Kmax_MO*I_MO/Imax_MO/brho;
    KOD.A34B2:=Kmax_MO*I_MO/Imax_MO/brho; KOD.A45B2:=Kmax_MO*I_MO/Imax_MO/brho;
    KOD.A56B2:=Kmax_MO*I_MO/Imax_MO/brho; KOD.A67B2:=Kmax_MO*I_MO/Imax_MO/brho;
    KOD.A78B2:=Kmax_MO*I_MO/Imax_MO/brho; KOD.A81B2:=Kmax_MO*I_MO/Imax_MO/brho;
  };

```
## Correction of MB field error

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
              correction of field errors in MB (compatible with V6.503 & SLHC)
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
```fortran
  if (correct_magnetic_error==1){
    select, flag=error, clear;
    select, flag=error, pattern=MB\.,class=multipole;
    select, flag=error, pattern=MBH\.,class=multipole;
    esave,  file="temp/MB.errors";
  }

```
## Running  corr_MB_ats_v4
```fortran
  if (correct_magnetic_error==1){
    system, "slhc/errors/corr_MB_ats_v4";
  }

```
## Calling MB_corr_setting.mad
```fortran
  if (correct_magnetic_error==1){
    call,   file="temp/MB_corr_setting.mad";
```
exec reset_MB_corr;
```fortran
  }

```
## Correction of triplet and D1

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
correction of triplet and D1 (only in collision, not compatible V6.503)
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
```fortran
  if (correct_magnetic_error==1){
    if (NRJ>5000.0000){
      option, echo, warn, -info;
      select, flag=error, clear;
      select, flag=error, pattern=MQX,  class=multipole;
      select, flag=error, pattern=MBX,  class=multipole;
```
select, flag=error, pattern=MBRC, class=multipole;
```fortran
      if (correct_for_D2==1){
        select, flag=error, pattern=MBRD, class=multipole;
      };
      if (correct_for_MCBX==1){
        select, flag=error, pattern=MCBXF, class=multipole;
      };
      esave,  file="temp/tripD1D2.errors";
      system, "slhc/errors/corr_tripD1_v6";
      call,   file="temp/MCX_setting.mad";
```
kcsx3.l1:=0 ;kcsx3.r1:=0 ;kcsx3.l5:=0 ;kcsx3.r5:=0 ; !switch off b3  correction in IR1 and IR5
kcox3.l1:=0 ;kcox3.r1:=0 ;kcox3.l5:=0 ;kcox3.r5:=0 ; !switch off b4  correction in IR1 and IR5
kcdx3.l1:=0 ;kcdx3.r1:=0 ;kcdx3.l5:=0 ;kcdx3.r5:=0 ; !switch off b5  correction in IR1 and IR5
kctx3.l1:=0 ;kctx3.r1:=0 ;kctx3.l5:=0 ;kctx3.r5:=0 ; !switch off b6  correction in IR1 and IR5
kqsx3.l1:=0 ;kqsx3.r1:=0 ;kqsx3.l5:=0 ;kqsx3.r5:=0 ; !switch off a2  correction in IR1 and IR5
kcssx3.l1:=0;kcssx3.r1:=0;kcssx3.l5:=0;kcssx3.r5:=0; !switch off a3  correction in IR1 and IR5
kcosx3.l1:=0;kcosx3.r1:=0;kcosx3.l5:=0;kcosx3.r5:=0; !switch off a4  correction in IR1 and IR5
kcdsx3.l1:=0;kcdsx3.r1:=0;kcdsx3.l5:=0;kcdsx3.r5:=0; !switch off a5  correction in IR1 and IR5
kctsx3.l1:=0;kctsx3.r1:=0;kctsx3.l5:=0;kctsx3.r5:=0; !switch off a6  correction in IR1 and IR5
```fortran

      kcsx3.l2 :=0;kcsx3.r2 :=0;kcsx3.l8 :=0;kcsx3.r8 :=0; !switch off b3  correction in IR2 and IR8
      kcox3.l2 :=0;kcox3.r2 :=0;kcox3.l8 :=0;kcox3.r8 :=0; !switch off b4  correction in IR2 and IR8
      kctx3.l2 :=0;kctx3.r2 :=0;kctx3.l8 :=0;kctx3.r8 :=0; !switch off b6  correction in IR2 and IR8
      kqsx3.l2 :=0;kqsx3.r2 :=0;kqsx3.l8 :=0;kqsx3.r8 :=0; !switch off a2  correction in IR2 and IR8
      kcssx3.l2:=0;kcssx3.r2:=0;kcssx3.l8:=0;kcssx3.r8:=0; !switch off a3  correction in IR2 and IR8
      kcosx3.l2:=0;kcosx3.r2:=0;kcosx3.l8:=0;kcosx3.r8:=0; !switch off a4  correction in IR2 and IR8

      option, -echo; !exec reset_MQX_corr;                             !switch off all IT multipole correction in all IR's
    };

    if (correct_for_D2==1){
```
Remove the average errors and assign the real errors of D2
```fortran
      use_average_errors_MBRD=0;
      call,file="slhc/errors/D2_errortable_v5";
      eoption,add=false;
      eoption,seed=myseed+103;
      call, file="slhc/errors/Efcomp_MBRD.madx";
      eoption,add=true;
    };
  }
```
## Optics parameters before matching
```fortran
  if (correct_magnetic_error==1){
    print, text="==================================================";
    print, text="======  OPTICS PARAMETERS: BEFORE MATCHING  ======";
    print, text="==================================================";
    call, file="slhc/toolkit/get_optics_params.madx";
  }

```
## Correct orbit distorsion

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
   correct orbit distortion resulting from other magnets
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
```fortran
  if (correct_magnetic_error==1){
    if((ON_A1S)^2+(ON_A1r)^2+(ON_B1S)^2+(ON_B1r)^2 >0){
      exec, initial_micado(4);
      exec, initial_micado(4);
      exec, initial_micado(4);
      exec, initial_micado(4);
    };
  }


```
## Final orbit correction before applying the crossing scheme
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
   final orbit correction before applying crossing scheme
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
```fortran
  if (correct_magnetic_error==1){
    if((ON_A1S)^2+(ON_A1r)^2+(ON_B1S)^2+(ON_B1r)^2 >0){
      exec, final_micado(0.004);
    };
  }
```
end of orbit correction, now switch ON crossing scheme
restoring crossing angle
```fortran
  if (correct_magnetic_error==1){
    exec, crossing_restore;
```
coguess,x=x.ip1,px=px.ip1,y=y.ip1,py=py.ip1;
```fortran
  }

```
## Fine tuning of coupling after CO correction and with Xscheme

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  Fine tuning of coupling after CO correction and with Xscheme
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
```fortran
  call,file="slhc/errors/FineCouplingCorrectionSimplex.madx";

```
## Limit corrector strength

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                Limit corrector strength
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
```fortran
  call,file="slhc/errors/corr_limit.madx";

```
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                matching of orbit, tune and chromaticity
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
```fortran
  if(ON_COLLISION==0) {ON_BB_CHARGE:=1;};    !W/o head-on Q and Q' are matched with bb


```
## Rematch the Xscheme towards specified separation and Xange in IP1/2/5/8
```fortran
  call,file="slhc/toolkit/rematchCOIP.madx";
```
## Rematch the CO in the arc for dispersion correction
```fortran
  if(ON_DISP<>0) {call,file="slhc/toolkit/rematchCOarc.madx";};

  if(mylhcbeam==1){
    kqtf=kqtf.b1;kqtd=kqtd.b1;kqtf.b1:=kqtf;kqtd.b1:=kqtd;
    ksf=ksf.b1;ksd=ksd.b1;ksf.b1:=ksf;ksd.b1:=ksd;
  };
  if(mylhcbeam>1){
    kqtf=kqtf.b2;kqtd=kqtd.b2;kqtf.b2:=kqtf;kqtd.b2:=kqtd;
    ksf=ksf.b2;ksd=ksd.b2;ksf.b2:=ksf;ksd.b2:=ksd;
  };

  match;
  global, q1=qx0, q2=qy0;
  vary,   name=kqtf, step=1.0E-7 ;
  vary,   name=kqtd, step=1.0E-7 ;
  lmdif,  calls=100, tolerance=1.0E-21;
  endmatch;

  match,chrom;
  global, dq1=qprime, dq2=qprime;
  vary,   name=ksf;
  vary,   name=ksd;
  lmdif,  calls=100, tolerance=1.0E-21;
  endmatch;

  match,chrom;
  global, dq1=qprime, dq2=qprime;
  global, q1=qx0, q2=qy0;
  vary,   name=ksf;
  vary,   name=ksd;
  vary,   name=kqtf, step=1.0E-7 ;
  vary,   name=kqtd, step=1.0E-7 ;
  lmdif,  calls=500, tolerance=1.0E-21;
  endmatch;

```
## Check corrector strength

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                Check corrector strength
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
```fortran

  call, file="slhc/errors/corr_value_limit.madx";
```
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                final twiss before sending to sixtrack
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
## Set BB charge on 
```fortran
  ON_BB_CHARGE:=1;

```
## RF on
```fortran
  if (NRJ<4999.9999) {VRF400:=8. ;LAGRF400.B1=0.5;LAGRF400.B2=0.;};
  if (NRJ>5000.0000) {VRF400:=16.;LAGRF400.B1=0.5;LAGRF400.B2=0.;};


```
## Compute final optics parameters
```fortran
  print, text="========================================";
  print, text="======  OPTICS PARAMETERS: FINAL  ======";
  print, text="========================================";
  call, file="slhc/toolkit/get_optics_params.madx";

```
## Call second time slhc/toolkit/BetaBeating.madx
```fortran
  call, file="slhc/toolkit/BetaBeating.madx";

```
## Twiss, chrom
```fortran
  twiss, chrom;

```
## Sixtrack command
sixtrack,cavall, mult_auto_off,radius=0.017;
```fortran
  sixtrack,cavall, radius=0.017;

```
## Sixtrack BB lenses
```fortran
  if( ON_BB_SWITCH == 1){
```
Fix bb lenses in sixtrack input
```fortran
    exec, SIXTRACK_INPUT_BB_LENSES;
  }

```
## Final twiss
```fortran
  select, flag=twiss, clear;
  if (not_a_mask==1){
    twiss,file="last_twiss.1";
    System,"gzip -f last_twiss.1";
  } else {
    twiss,file="last_twiss.1";
    System,"gzip -f last_twiss.1";
  };
  stop;
```
