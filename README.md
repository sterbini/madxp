## madxp package

This package aims to complement the cpymad package with some additional functions, namely to access the MAD-X variables.
In a second stage, we will propose to merge with the main package cpymad.



## To install the package 
One can install the package by
```
pip install --user git+https://github.com/sterbini/madxp.git
```
or upgrade it by
```
pip install --upgrade --user git+https://github.com/sterbini/madxp.git
```
The numpy, pandas and cpymad packages are required.

## Example
In the following we will present with simple example the main functions of the package.
It will be also an occasion to introduce the jargon we will use.

After a standard import 


```python
from madxp import cpymadTool as mt
from cpymad.madx import Madx
mad=Madx()
```

    
      ++++++++++++++++++++++++++++++++++++++++++++
      +     MAD-X 5.05.01  (64 bit, Linux)       +
      + Support: mad@cern.ch, http://cern.ch/mad +
      + Release   date: 2019.06.07               +
      + Execution date: 2020.04.19 10:26:43      +
      ++++++++++++++++++++++++++++++++++++++++++++


we setup a simple MAD-X input file


```python
mad.input('''
! variables definition
a=1;
b:=c+3*a+sqrt(d)+pi;
c:=a+2+e; 
d:=2+f;
f=g;
h:=3;
const i=2;

! element definition
my_quad: quadrupole, l=1, k1:=(myk1+h+b)/1000;

! sequence definition
my_sequence: sequence,l=10, refer=exit;
q1: my_quad, at=3;
endsequence;

! beam defintion
beam, sequence=my_sequence;
''');
```

In the file we defined constants (e.g., **i**), independent variables (e.g., **a**), dependent variables (e.g., **b**).
To be noted that **k1** (the parameter of **my_quad** depends on **myk1**, that is not explicitly defined).

Finally, we define a sequence and a beam.

The following **sequences_df** function


```python
mt.sequences_df(mad)
```




<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>beam</th>
      <th>expanded</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>my_sequence</th>
      <td>False</td>
      <td>False</td>
    </tr>
  </tbody>
</table>



is used to extract a pandas dataframe (df) contained the sequences in the **mad** handle.
NB: there is only one  sequence and has not yet be USEd: this implies that is not expanded (not drifts/checks). 

Despite the fact the beam is defined to be attached to the sequence, no beam is attached to the sequence (one needs to USE the sequence to attach it). 

Similarly on can use the **beams_df** function to list the beams that are attached to the sequence.


```python
mt.beams_df(mad)
```

    The sequence my_sequence has no beam attached.

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>



In our case the beams df is empty since no beam is attached yet (see above).

One can export the variable of the present **mad** workspace.


```python
my_variable_dict=mt.variables_dict(mad)
my_variable_dict.keys()
```




    dict_keys(['constant_df', 'independent_variable_df', 'dependent_variable_df'])



There are three df's representing MAD-X global workspace. 
- constant_df, contains the constant (system and user defined)
- independent_variable_df, contains the indipendent variables
- dependent_variable_df, contains the dependent variables


```python
my_variable_dict['constant_df']
```

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>value</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>amu0</th>
      <td>1.25664e-06</td>
    </tr>
    <tr>
      <th>clight</th>
      <td>2.99792e+08</td>
    </tr>
    <tr>
      <th>degrad</th>
      <td>57.2958</td>
    </tr>
    <tr>
      <th>e</th>
      <td>2.71828</td>
    </tr>
    <tr>
      <th>emass</th>
      <td>0.000510999</td>
    </tr>
    <tr>
      <th>erad</th>
      <td>2.81794e-15</td>
    </tr>
    <tr>
      <th>hbar</th>
      <td>6.58212e-25</td>
    </tr>
    <tr>
      <th>i</th>
      <td>2</td>
    </tr>
    <tr>
      <th>mumass</th>
      <td>0.105658</td>
    </tr>
    <tr>
      <th>nmass</th>
      <td>0.931494</td>
    </tr>
    <tr>
      <th>pi</th>
      <td>3.14159</td>
    </tr>
    <tr>
      <th>pmass</th>
      <td>0.938272</td>
    </tr>
    <tr>
      <th>prad</th>
      <td>1.5347e-18</td>
    </tr>
    <tr>
      <th>qelect</th>
      <td>1.60218e-19</td>
    </tr>
    <tr>
      <th>raddeg</th>
      <td>0.0174533</td>
    </tr>
    <tr>
      <th>twopi</th>
      <td>6.28319</td>
    </tr>
    <tr>
      <th>version</th>
      <td>50501</td>
    </tr>
  </tbody>
</table>


NB: in addition to the MAD-X predefined constants, **i** (user defined constant) is present too.


```python
my_variable_dict['independent_variable_df']
```



<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>value</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>a</th>
      <td>1</td>
    </tr>
    <tr>
      <th>f</th>
      <td>0</td>
    </tr>
    <tr>
      <th>g</th>
      <td>0</td>
    </tr>
    <tr>
      <th>h</th>
      <td>3</td>
    </tr>
    <tr>
      <th>none</th>
      <td>0</td>
    </tr>
    <tr>
      <th>twiss_tol</th>
      <td>1e-06</td>
    </tr>
  </tbody>
</table>




NB: 
 - **g** is not explicitly declared, then is an independent variable (with 0 values)
 - despite **h** is assigned via a deferred expression, it is an independent variables (trivial deferred expression)
 - the variable **myk1** (in the definition of the **my_quad** element) is not present in the list of the independent variable (since the sequence is not yet used) 
 - the **none** and **twiss_tol** are system-defined independent variables.


```python
my_variable_dict['dependent_variable_df']

```





<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>value</th>
      <th>expression</th>
      <th>parameters</th>
      <th>knobs</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>b</th>
      <td>13.2741</td>
      <td>c+3*a+sqrt(d)+pi</td>
      <td>[a, c, d, pi]</td>
      <td>[a, f]</td>
    </tr>
    <tr>
      <th>c</th>
      <td>5.71828</td>
      <td>a+2+e</td>
      <td>[a, e]</td>
      <td>[a]</td>
    </tr>
    <tr>
      <th>d</th>
      <td>2</td>
      <td>2+f</td>
      <td>[f]</td>
      <td>[f]</td>
    </tr>
  </tbody>
</table>




The dependent variable DF contains the numerical values, the expression, the parameters and the knobs for each dependent variables. 

The *knobs of a given dependent variable*, my_variable, are a set of  independent variables that control the value of my_variable. 

NB: 
 - for **b**, **pi** is not a knobs (since it is a constant). The same argument holds for **c**  and its parameter **e** (Euler number),
 - to determine the knobs, all parameters that are dependent variables (e.g., **c** as parameter of **b**)  are *decomposed* in their independent variables.

Another interesting method **sequence_df** (not to be be conbused with **sequences_df**) allows to transform a sequence in a df.


```python
mt.sequence_df(mad, 'my_sequence')
```

    Variable myk1 not defined! Cosidered as a knob.






<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>position</th>
      <th>parent</th>
      <th>base_type</th>
      <th>length</th>
      <th>parameters</th>
      <th>knobs</th>
      <th>align_errors</th>
      <th>aper_offset</th>
      <th>aper_offset value</th>
      <th>aper_tol</th>
      <th>...</th>
      <th>slot_id</th>
      <th>slot_id value</th>
      <th>thick</th>
      <th>thick value</th>
      <th>tilt</th>
      <th>tilt value</th>
      <th>type</th>
      <th>type value</th>
      <th>v_pos</th>
      <th>v_pos value</th>
    </tr>
    <tr>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>my_sequence$start</th>
      <td>0.0</td>
      <td>marker</td>
      <td>marker</td>
      <td>0.0</td>
      <td>[none]</td>
      <td>[none]</td>
      <td>None</td>
      <td>[0.0]</td>
      <td>[0.0]</td>
      <td>[0.0, 0.0, 0.0]</td>
      <td>...</td>
      <td>none</td>
      <td>0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td></td>
      <td></td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>q1</th>
      <td>2.0</td>
      <td>my_quad</td>
      <td>quadrupole</td>
      <td>1.0</td>
      <td>[b, h, myk1, none]</td>
      <td>[a, f, h, myk1, none]</td>
      <td>None</td>
      <td>[0.0]</td>
      <td>[0.0]</td>
      <td>[0.0, 0.0, 0.0]</td>
      <td>...</td>
      <td>none</td>
      <td>0</td>
      <td>False</td>
      <td>False</td>
      <td>0.0</td>
      <td>0.0</td>
      <td></td>
      <td></td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>my_sequence$end</th>
      <td>10.0</td>
      <td>marker</td>
      <td>marker</td>
      <td>0.0</td>
      <td>[none]</td>
      <td>[none]</td>
      <td>None</td>
      <td>[0.0]</td>
      <td>[0.0]</td>
      <td>[0.0, 0.0, 0.0]</td>
      <td>...</td>
      <td>none</td>
      <td>0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td></td>
      <td></td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
<p>3 rows × 81 columns</p>


NB:
- for each element you have the *parameters* and the *knobs* columns. This knobs are the element knobs (very similar to the knobs of the variables mentioned above),
- you can see **myk1** has knob.

As for the variable and the element, we can naturally define the knobs of a sequence.



```python
mt.knobs_df(mt.sequence_df(mad, 'my_sequence'))
```





<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>multeplicity</th>
      <th>dependences</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>none</th>
      <td>3</td>
      <td>[my_sequence\$start, q1, my_sequence\$end]</td>
    </tr>
    <tr>
      <th>a</th>
      <td>1</td>
      <td>[q1]</td>
    </tr>
    <tr>
      <th>f</th>
      <td>1</td>
      <td>[q1]</td>
    </tr>
    <tr>
      <th>h</th>
      <td>1</td>
      <td>[q1]</td>
    </tr>
    <tr>
      <th>myk1</th>
      <td>1</td>
      <td>[q1]</td>
    </tr>
  </tbody>
</table>




For each knob you have the multeplicity, that is the number of elements are controlled by that specific knob. In the **dependences** column one have the explicit list of the elements controlled by this knob.

One can do also use the same funtion to extract of the knobs of the dependent variables.


```python
mt.knobs_df(my_variable_dict['dependent_variable_df'])
```





<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>multeplicity</th>
      <th>dependences</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>a</th>
      <td>2</td>
      <td>[b, c]</td>
    </tr>
    <tr>
      <th>f</th>
      <td>2</td>
      <td>[b, d]</td>
    </tr>
  </tbody>
</table>



With a similar spirit, one can sub-select a sequence df with the elements controlled only on this knob. 


```python
mt.knob_df('myk1',mt.sequence_df(mad, 'my_sequence'))
```




<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>position</th>
      <th>parent</th>
      <th>base_type</th>
      <th>length</th>
      <th>parameters</th>
      <th>knobs</th>
      <th>align_errors</th>
      <th>aper_offset</th>
      <th>aper_offset value</th>
      <th>aper_tol</th>
      <th>...</th>
      <th>slot_id</th>
      <th>slot_id value</th>
      <th>thick</th>
      <th>thick value</th>
      <th>tilt</th>
      <th>tilt value</th>
      <th>type</th>
      <th>type value</th>
      <th>v_pos</th>
      <th>v_pos value</th>
    </tr>
    <tr>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>q1</th>
      <td>2.0</td>
      <td>my_quad</td>
      <td>quadrupole</td>
      <td>1.0</td>
      <td>[b, h, myk1, none]</td>
      <td>[a, f, h, myk1, none]</td>
      <td>None</td>
      <td>[0.0]</td>
      <td>[0.0]</td>
      <td>[0.0, 0.0, 0.0]</td>
      <td>...</td>
      <td>none</td>
      <td>0</td>
      <td>False</td>
      <td>False</td>
      <td>0.0</td>
      <td>0.0</td>
      <td></td>
      <td></td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
<p>1 rows × 81 columns</p>


One can do the same analysis for the dependent variables df.


```python
mt.knob_df('f', my_variable_dict['dependent_variable_df'])
```




<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>value</th>
      <th>expression</th>
      <th>parameters</th>
      <th>knobs</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>b</th>
      <td>13.2741</td>
      <td>c+3*a+sqrt(d)+pi</td>
      <td>[a, c, d, pi]</td>
      <td>[a, f]</td>
    </tr>
    <tr>
      <th>d</th>
      <td>2</td>
      <td>2+f</td>
      <td>[f]</td>
      <td>[f]</td>
    </tr>
  </tbody>
</table>



Let us *USE* the sequence


```python
mad.input('use, sequence=my_sequence;');
```

The we can see that


```python
mt.sequences_df(mad)
```




<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>beam</th>
      <th>expanded</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>my_sequence</th>
      <td>True</td>
      <td>True</td>
    </tr>
  </tbody>
</table>



and


```python
mt.beams_df(mad)
```




<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>particle</th>
      <th>sequence</th>
      <th>bunched</th>
      <th>radiate</th>
      <th>mass</th>
      <th>charge</th>
      <th>energy</th>
      <th>pc</th>
      <th>gamma</th>
      <th>beta</th>
      <th>...</th>
      <th>circ</th>
      <th>dtbyds</th>
      <th>deltap</th>
      <th>alfa</th>
      <th>u0</th>
      <th>qs</th>
      <th>arad</th>
      <th>bv</th>
      <th>pdamp</th>
      <th>n1min</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>my_sequence</th>
      <td>positron</td>
      <td>my_sequence</td>
      <td>True</td>
      <td>False</td>
      <td>0.000511</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>1956.951198</td>
      <td>1.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>2.611199e-07</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>2.817940e-15</td>
      <td>1.0</td>
      <td>[1.0, 1.0, 2.0]</td>
      <td>-1.0</td>
    </tr>
  </tbody>
</table>
<p>1 rows × 32 columns</p>


To ease the visualization of a given element you can run


```python
mt.show_element('q1', mt.sequence_df(mad, 'my_sequence'))
```

    q1
    position                                     2
    parent                                 my_quad
    base_type                           quadrupole
    length                                       1
    parameters                  [b, h, myk1, none]
    knobs                    [a, f, h, myk1, none]
    aper_offset                              [0.0]
    aper_offset value                        [0.0]
    aper_tol                       [0.0, 0.0, 0.0]
    aper_tol value                 [0.0, 0.0, 0.0]
    aperture                                 [0.0]
    aperture value                           [0.0]
    apertype                                circle
    apertype value                          circle
    assembly_id                               none
    assembly_id value                            0
    at                                         3.0
    at value                                     3
    base_name                           quadrupole
    bend_fringe                              False
    bend_fringe value                        False
    calib                                      0.0
    calib value                                  0
    comments                                      
    comments value                                
    enable                                       0
    exact                                       -1
    exact value                                 -1
    from                                          
    from value                                    
    k0                                         0.0
    k0 value                                     0
    k1                     ( myk1 + h + b ) / 1000
    k1 value                             0.0162741
    k1s                                        0.0
    k1s value                                    0
    kill_ent_fringe                          False
    kill_ent_fringe value                    False
    kill_exi_fringe                          False
    kill_exi_fringe value                    False
    kmax                                       0.0
    kmax value                                   0
    kmin                                       0.0
    kmin value                                   0
    knl                                      [0.0]
    knl value                                [0.0]
    ksl                                      [0.0]
    ksl value                                [0.0]
    l                                          1.0
    l value                                      1
    magnet                                       1
    magnet value                                 1
    mech_sep                                   0.0
    mech_sep value                               0
    method                                      -1
    method value                                -1
    model                                       -1
    model value                                 -1
    node_name                                   q1
    nst                                         -1
    nst value                                   -1
    occ_cnt                                      1
    permfringe                               False
    permfringe value                         False
    polarity                                   0.0
    polarity value                               0
    slice                                        1
    slice value                                  1
    slot_id                                   none
    slot_id value                                0
    thick                                    False
    thick value                              False
    tilt                                       0.0
    tilt value                                   0
    type                                          
    type value                                    
    v_pos                                      0.0
    v_pos value                                  0




<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>position</th>
      <th>parent</th>
      <th>base_type</th>
      <th>length</th>
      <th>parameters</th>
      <th>knobs</th>
      <th>aper_offset</th>
      <th>aper_offset value</th>
      <th>aper_tol</th>
      <th>aper_tol value</th>
      <th>...</th>
      <th>slot_id</th>
      <th>slot_id value</th>
      <th>thick</th>
      <th>thick value</th>
      <th>tilt</th>
      <th>tilt value</th>
      <th>type</th>
      <th>type value</th>
      <th>v_pos</th>
      <th>v_pos value</th>
    </tr>
    <tr>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>q1</th>
      <td>2.0</td>
      <td>my_quad</td>
      <td>quadrupole</td>
      <td>1.0</td>
      <td>[b, h, myk1, none]</td>
      <td>[a, f, h, myk1, none]</td>
      <td>[0.0]</td>
      <td>[0.0]</td>
      <td>[0.0, 0.0, 0.0]</td>
      <td>[0.0, 0.0, 0.0]</td>
      <td>...</td>
      <td>none</td>
      <td>0</td>
      <td>False</td>
      <td>False</td>
      <td>0.0</td>
      <td>0.0</td>
      <td></td>
      <td></td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
<p>1 rows × 78 columns</p>



One can note that, after using the sequence, **myk1** appears in the independent variables df.


```python
my_variable_dict=mt.variables_dict(mad)
my_variable_dict['independent_variable_df']
```



<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>value</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>a</th>
      <td>1</td>
    </tr>
    <tr>
      <th>f</th>
      <td>0</td>
    </tr>
    <tr>
      <th>g</th>
      <td>0</td>
    </tr>
    <tr>
      <th>h</th>
      <td>3</td>
    </tr>
    <tr>
      <th>myk1</th>
      <td>0</td>
    </tr>
    <tr>
      <th>none</th>
      <td>0</td>
    </tr>
    <tr>
      <th>twiss_tol</th>
      <td>1e-06</td>
    </tr>
  </tbody>
</table>


We can simply twiss the active sequence.


```python
mad.input('twiss, betx=1,bety=1;')
```

    enter Twiss module
    
    ++++++ table: summ
    
                length             orbit5               alfa            gammatr 
                    10                 -0                  0                  0 
    
                    q1                dq1            betxmax              dxmax 
          0.2356243527                  0        94.80191493                  0 
    
                 dxrms             xcomax             xcorms                 q2 
                     0                  0                  0       0.2327327674 
    
                   dq2            betymax              dymax              dyrms 
                     0        107.4425105                  0                  0 
    
                ycomax             ycorms             deltap            synch_1 
                     0                  0                  0                  0 
    
               synch_2            synch_3            synch_4            synch_5 
                     0                  0                  0                  0 
    
                nflips 
                     0 





    True



and we can list the tables of the MAD-X instance by using



```python
list(mad.table)
```




    ['summ', 'twiss']



We can import in df the two tables *twiss* and *summ* (the summary table) by


```python
mt.table_df(mad.table.twiss)
```




<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>name</th>
      <th>keyword</th>
      <th>s</th>
      <th>betx</th>
      <th>alfx</th>
      <th>mux</th>
      <th>bety</th>
      <th>alfy</th>
      <th>muy</th>
      <th>x</th>
      <th>...</th>
      <th>sig54</th>
      <th>sig55</th>
      <th>sig56</th>
      <th>sig61</th>
      <th>sig62</th>
      <th>sig63</th>
      <th>sig64</th>
      <th>sig65</th>
      <th>sig66</th>
      <th>n1</th>
    </tr>
    <tr>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>my_sequence$start:1</th>
      <td>my_sequence$start:1</td>
      <td>marker</td>
      <td>0.0</td>
      <td>1.000000</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>1.000000</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>drift_0:0</th>
      <td>drift_0:0</td>
      <td>drift</td>
      <td>2.0</td>
      <td>5.000000</td>
      <td>-2.000000</td>
      <td>0.176208</td>
      <td>5.000000</td>
      <td>-2.000000</td>
      <td>0.176208</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>q1:1</th>
      <td>q1:1</td>
      <td>quadrupole</td>
      <td>3.0</td>
      <td>9.870401</td>
      <td>-2.843951</td>
      <td>0.198879</td>
      <td>10.130788</td>
      <td>-3.158591</td>
      <td>0.198706</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>drift_1:0</th>
      <td>drift_1:0</td>
      <td>drift</td>
      <td>10.0</td>
      <td>94.801915</td>
      <td>-9.289122</td>
      <td>0.235624</td>
      <td>107.442511</td>
      <td>-10.743083</td>
      <td>0.232733</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>my_sequence$end:1</th>
      <td>my_sequence$end:1</td>
      <td>marker</td>
      <td>10.0</td>
      <td>94.801915</td>
      <td>-9.289122</td>
      <td>0.235624</td>
      <td>107.442511</td>
      <td>-10.743083</td>
      <td>0.232733</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 256 columns</p>


and


```python
mt.summ_df(mad.table.summ)
```




<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>length</th>
      <th>orbit5</th>
      <th>alfa</th>
      <th>gammatr</th>
      <th>q1</th>
      <th>dq1</th>
      <th>betxmax</th>
      <th>dxmax</th>
      <th>dxrms</th>
      <th>xcomax</th>
      <th>...</th>
      <th>dyrms</th>
      <th>ycomax</th>
      <th>ycorms</th>
      <th>deltap</th>
      <th>synch_1</th>
      <th>synch_2</th>
      <th>synch_3</th>
      <th>synch_4</th>
      <th>synch_5</th>
      <th>nflips</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>summ</th>
      <td>10.0</td>
      <td>-0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.235624</td>
      <td>0.0</td>
      <td>94.801915</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
<p>1 rows × 25 columns</p>



In needed one can "interpolate" the optical function at specific *s*-position using the function table_interpolation_df. The "interpolation" recompute with a minimal twiss the correct values (therefore is not a proper interpolation but re-computation).  


```python
import numpy as np
mt.table_interpolation_df(my_s_list=np.linspace(2,3,11), my_table=mt.table_df(mad.table.twiss))
```




<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>name</th>
      <th>keyword</th>
      <th>s</th>
      <th>betx</th>
      <th>alfx</th>
      <th>mux</th>
      <th>bety</th>
      <th>alfy</th>
      <th>muy</th>
      <th>x</th>
      <th>...</th>
      <th>sig54</th>
      <th>sig55</th>
      <th>sig56</th>
      <th>sig61</th>
      <th>sig62</th>
      <th>sig63</th>
      <th>sig64</th>
      <th>sig65</th>
      <th>sig66</th>
      <th>n1</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>drift_0:0</th>
      <td>drift_0:0</td>
      <td>drift</td>
      <td>2</td>
      <td>5</td>
      <td>-2</td>
      <td>0.176208</td>
      <td>5</td>
      <td>-2</td>
      <td>0.176208</td>
      <td>0</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>at_2.1:1</th>
      <td>at_2.1:1</td>
      <td>interpolation</td>
      <td>2.1</td>
      <td>5.40914</td>
      <td>-2.0912</td>
      <td>0.179269</td>
      <td>5.41086</td>
      <td>-2.1088</td>
      <td>0.179268</td>
      <td>0</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>at_2.2:1</th>
      <td>at_2.2:1</td>
      <td>interpolation</td>
      <td>2.2</td>
      <td>5.83639</td>
      <td>-2.18104</td>
      <td>0.182101</td>
      <td>5.84361</td>
      <td>-2.21897</td>
      <td>0.182099</td>
      <td>0</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>at_2.3:1</th>
      <td>at_2.3:1</td>
      <td>interpolation</td>
      <td>2.3</td>
      <td>6.28146</td>
      <td>-2.26946</td>
      <td>0.18473</td>
      <td>6.29854</td>
      <td>-2.33059</td>
      <td>0.184723</td>
      <td>0</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>at_2.4:1</th>
      <td>at_2.4:1</td>
      <td>interpolation</td>
      <td>2.4</td>
      <td>6.74408</td>
      <td>-2.35641</td>
      <td>0.187175</td>
      <td>6.77595</td>
      <td>-2.44372</td>
      <td>0.187159</td>
      <td>0</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>at_2.5:1</th>
      <td>at_2.5:1</td>
      <td>interpolation</td>
      <td>2.5</td>
      <td>7.22393</td>
      <td>-2.44182</td>
      <td>0.189455</td>
      <td>7.27614</td>
      <td>-2.55845</td>
      <td>0.189426</td>
      <td>0</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>at_2.6:1</th>
      <td>at_2.6:1</td>
      <td>interpolation</td>
      <td>2.6</td>
      <td>7.7207</td>
      <td>-2.52564</td>
      <td>0.191587</td>
      <td>7.79944</td>
      <td>-2.67484</td>
      <td>0.191538</td>
      <td>0</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>at_2.7:1</th>
      <td>at_2.7:1</td>
      <td>interpolation</td>
      <td>2.7</td>
      <td>8.23407</td>
      <td>-2.60782</td>
      <td>0.193583</td>
      <td>8.34619</td>
      <td>-2.79297</td>
      <td>0.193511</td>
      <td>0</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>at_2.8:1</th>
      <td>at_2.8:1</td>
      <td>interpolation</td>
      <td>2.8</td>
      <td>8.76371</td>
      <td>-2.68829</td>
      <td>0.195456</td>
      <td>8.91675</td>
      <td>-2.91292</td>
      <td>0.195356</td>
      <td>0</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>at_2.9:1</th>
      <td>at_2.9:1</td>
      <td>interpolation</td>
      <td>2.9</td>
      <td>9.30927</td>
      <td>-2.76702</td>
      <td>0.197218</td>
      <td>9.51149</td>
      <td>-3.03477</td>
      <td>0.197084</td>
      <td>0</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>q1:1</th>
      <td>q1:1</td>
      <td>quadrupole</td>
      <td>3</td>
      <td>9.8704</td>
      <td>-2.84395</td>
      <td>0.198879</td>
      <td>10.1308</td>
      <td>-3.15859</td>
      <td>0.198706</td>
      <td>0</td>
      <td>...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
<p>11 rows × 256 columns</p>


The table_interpolation_df is somehow equivalent to the *intepolate* flag of MAD-X, as you can see below


```python
mad.input('''
select, flag=interpolate, clear;
select, flag=interpolate, sequence=my_sequence,class=quadrupole, slice=10;
! more on 
twiss, betx=1,bety=1,table='with_interpolation';
''')
mt.table_df(mad.table.with_interpolation)
```

    enter Twiss module
    
    ++++++ table: summ
    
                length             orbit5               alfa            gammatr 
                    10                 -0                  0                  0 
    
                    q1                dq1            betxmax              dxmax 
          0.2356243527                  0        94.80191493                  0 
    
                 dxrms             xcomax             xcorms                 q2 
                     0                  0                  0       0.2327327674 
    
                   dq2            betymax              dymax              dyrms 
                     0        107.4425105                  0                  0 
    
                ycomax             ycorms             deltap            synch_1 
                     0                  0                  0                  0 
    
               synch_2            synch_3            synch_4            synch_5 
                     0                  0                  0                  0 
    
                nflips 
                     0 




<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>name</th>
      <th>keyword</th>
      <th>s</th>
      <th>betx</th>
      <th>alfx</th>
      <th>mux</th>
      <th>bety</th>
      <th>alfy</th>
      <th>muy</th>
      <th>x</th>
      <th>...</th>
      <th>sig54</th>
      <th>sig55</th>
      <th>sig56</th>
      <th>sig61</th>
      <th>sig62</th>
      <th>sig63</th>
      <th>sig64</th>
      <th>sig65</th>
      <th>sig66</th>
      <th>n1</th>
    </tr>
    <tr>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>my_sequence$start:1</th>
      <td>my_sequence$start:1</td>
      <td>marker</td>
      <td>0.0</td>
      <td>1.000000</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>1.000000</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>drift_0:0</th>
      <td>drift_0:0</td>
      <td>drift</td>
      <td>2.0</td>
      <td>5.000000</td>
      <td>-2.000000</td>
      <td>0.176208</td>
      <td>5.000000</td>
      <td>-2.000000</td>
      <td>0.176208</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>q1:1</th>
      <td>q1:1</td>
      <td>quadrupole</td>
      <td>2.1</td>
      <td>5.409142</td>
      <td>-2.091202</td>
      <td>0.179269</td>
      <td>5.410858</td>
      <td>-2.108800</td>
      <td>0.179268</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>q1:1</th>
      <td>q1:1</td>
      <td>quadrupole</td>
      <td>2.2</td>
      <td>5.836390</td>
      <td>-2.181043</td>
      <td>0.182101</td>
      <td>5.843611</td>
      <td>-2.218972</td>
      <td>0.182099</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>q1:1</th>
      <td>q1:1</td>
      <td>quadrupole</td>
      <td>2.3</td>
      <td>6.281465</td>
      <td>-2.269464</td>
      <td>0.184730</td>
      <td>6.298543</td>
      <td>-2.330590</td>
      <td>0.184723</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>q1:1</th>
      <td>q1:1</td>
      <td>quadrupole</td>
      <td>2.4</td>
      <td>6.744077</td>
      <td>-2.356408</td>
      <td>0.187175</td>
      <td>6.775948</td>
      <td>-2.443724</td>
      <td>0.187159</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>q1:1</th>
      <td>q1:1</td>
      <td>quadrupole</td>
      <td>2.5</td>
      <td>7.223926</td>
      <td>-2.441818</td>
      <td>0.189455</td>
      <td>7.276139</td>
      <td>-2.558449</td>
      <td>0.189426</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>q1:1</th>
      <td>q1:1</td>
      <td>quadrupole</td>
      <td>2.6</td>
      <td>7.720698</td>
      <td>-2.525639</td>
      <td>0.191587</td>
      <td>7.799439</td>
      <td>-2.674840</td>
      <td>0.191538</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>q1:1</th>
      <td>q1:1</td>
      <td>quadrupole</td>
      <td>2.7</td>
      <td>8.234072</td>
      <td>-2.607815</td>
      <td>0.193583</td>
      <td>8.346191</td>
      <td>-2.792972</td>
      <td>0.193511</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>q1:1</th>
      <td>q1:1</td>
      <td>quadrupole</td>
      <td>2.8</td>
      <td>8.763711</td>
      <td>-2.688294</td>
      <td>0.195456</td>
      <td>8.916749</td>
      <td>-2.912922</td>
      <td>0.195356</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>q1:1</th>
      <td>q1:1</td>
      <td>quadrupole</td>
      <td>2.9</td>
      <td>9.309273</td>
      <td>-2.767023</td>
      <td>0.197218</td>
      <td>9.511486</td>
      <td>-3.034769</td>
      <td>0.197084</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>q1:1</th>
      <td>q1:1</td>
      <td>quadrupole</td>
      <td>3.0</td>
      <td>9.870401</td>
      <td>-2.843951</td>
      <td>0.198879</td>
      <td>10.130788</td>
      <td>-3.158591</td>
      <td>0.198706</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>drift_1:0</th>
      <td>drift_1:0</td>
      <td>drift</td>
      <td>10.0</td>
      <td>94.801915</td>
      <td>-9.289122</td>
      <td>0.235624</td>
      <td>107.442511</td>
      <td>-10.743083</td>
      <td>0.232733</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>my_sequence$end:1</th>
      <td>my_sequence$end:1</td>
      <td>marker</td>
      <td>10.0</td>
      <td>94.801915</td>
      <td>-9.289122</td>
      <td>0.235624</td>
      <td>107.442511</td>
      <td>-10.743083</td>
      <td>0.232733</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
<p>14 rows × 256 columns</p>


but the proposed function can do the interpolation without a "live" MAD-X handle and sequence.

