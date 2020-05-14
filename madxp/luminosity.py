import numpy as np
from cl2pd import particle
from scipy import integrate

def beta(z, beta0, alpha_z0):
    '''Beta function in drift space'''
    return beta0-2*alpha_z0*z+(1+alpha_z0**2)/beta0*z**2

def dispersion(z, d0, dp0):
    '''Dispersion in drift space'''
    return d0+z*dp0

def sigma(beta, epsilon0, betagamma):
    '''Betatronic sigma'''
    return np.sqrt(beta*epsilon0/betagamma)

def L(f, nb, 
      N1, N2,
      x_1, x_2,
      y_1, y_2,
      px_1, px_2,
      py_1, py_2,
      energy_tot1, energy_tot2,
      deltap_p0_1, deltap_p0_2,
      epsilon_x1, epsilon_x2,
      epsilon_y1, epsilon_y2, 
      sigma_z1, sigma_z2,
      beta_x1, beta_x2,
      beta_y1, beta_y2,
      alpha_x1, alpha_x2,
      alpha_y1, alpha_y2,
      dx_1, dx_2,
      dy_1, dy_2,
      dpx_1, dpx_2,
      dpy_1, dpy_2,
      CC_V_x_1=0, CC_f_x_1=0, CC_phase_x_1=0,
      CC_V_x_2=0, CC_f_x_2=0, CC_phase_x_2=0,
      CC_V_y_1=0, CC_f_y_1=0, CC_phase_y_1=0,
      CC_V_y_2=0, CC_f_y_2=0, CC_phase_y_2=0,
      R12_1=0, R22_1=0, R34_1=0, R44_1=0,
      R12_2=0, R22_2=0, R34_2=0, R44_2=0,
      verbose=False, sigma_integration=3):
    '''
    Returns luminosity in Hz/cm^2.

    f: revolution frequency
    nb: number of colliding bunch per beam in the specific Interaction Point (IP).
    N1,2: B1,2 number of particle per bunch
    x,y,1,2: horizontal/vertical position at the IP of B1,2, as defined in MADX [m]
    px,y,1,2: px,py at the IP of B1,2, as defined in MADX
    energy_tot1,2: total energy of the B1,2 [GeV]
    deltap_p0_1,2: rms momentum spread of B1,2 (formulas assume Gaussian off-momentum distribution)
    epsilon_x,y,1,2: horizontal/vertical normalized emittances of B1,2 [m rad]
    sigma_z1,2: rms longitudinal spread in z of B1,2 [m]
    beta_x,y,1,2: horizontal/vertical beta-function at IP of B1,2 [m]
    alpha_x,y,1,2: horizontal/vertical alpha-function at IP of B1,2 
    dx,y_1,2: horizontal/vertical dispersion-function at IP of B1,2, as defined in MADX [m]
    dpx,y_1,2: horizontal/vertical differential-dispersion-function IP of B1,2, as defined in MADX 
    CC_V_x,y,1,2: B1,2 H/V CC total of the cavities that the beam sees before reaching the IP [V]
    CC_f_x,y,1,2: B1,2 H/V CC frequency of cavities that the beam sees before reaching the IP [Hz]
    CC_phase_1,2: B1,2 H/V CC phase of cavities that the beam sees before reaching the IP. 
        Sinusoidal function with respect to the center of the bunch is assumed.
        Therefore 0 rad means no kick for the central longitudinal slice [rad]
    RAB_1,2: B1,2 equivalent H/V linear transfer matrix coefficients between the CC
        that the beam sees before reaching the IP and IP itself [SI units] 
    verbose: to have verbose output
    sigma_integration: the number of sigma consider for the integration 
        (taken into account only if CC(s) is/are present)

    In MAD-X px is p_x/p_0 (p_x is the x-component of the momentum and p_0 is the design momentum).
    In our approximation we use the paraxial approximation: p_0~p_z so px is an angle. 
    Similar arguments holds for py.

    In MAD-X, dx and dpx are the literature dispersion and is derivative in s divided by the relatistic beta.
    In fact, since pt=beta*deltap, where beta is the relativistic Lorentz factor, 
    those functions given by MAD-X must be multiplied by beta a number of times equal to the order of
    the derivative to find the functions given in the literature.
    To note that dpx is normalized by the reference momentum (p_s) and not the design momentum (p_0),
    ps = p0(1+deltap). We assume that dpx is the z-derivative of the px.

    '''
    particle_1=particle.setTotalEnergy_GeV(energy_tot1)
    betagamma_1=particle_1['relativisticBetaGamma']
    br_1=particle_1['relativisticBeta']

    particle_2=particle.setTotalEnergy_GeV(energy_tot2)
    betagamma_2=particle_2['relativisticBetaGamma']
    br_2=particle_2['relativisticBeta']

    c=particle.speedOfLight_m_s

    # module of B1 speed
    v0_1=br_1*c 
    # paraxial hypothesis 
    vx_1=v0_1*px_1
    vy_1=v0_1*py_1
    vz_1=v0_1*np.sqrt(1-px_1**2-py_1**2)
    v_1=np.array([vx_1, vy_1, vz_1])

    v0_2=br_2*c # module of B2 speed
    # Assuming counter rotating B2 ('-' sign)
    vx_2=-v0_2*px_2
    vy_2=-v0_2*py_2
    # assuming px_2**2+py_2**2 < 1
    vz_2=-v0_2*np.sqrt(1-px_2**2-py_2**2)
    v_2=np.array([vx_2, vy_2, vz_2])

    if verbose:
        print(f'B1 velocity vector:{v_1}')
        print(f'B2 velocity vector:{v_2}')

    diff_v = v_1-v_2
    cross_v= np.cross(v_1, v_2)

    # normalized to get 1 for the ideal case 
    # NB we assume px_1 and py_1 constant along the z-slices 
    # NOT TRUE FOR CC! In any case the Moeller efficiency is almost equal to 1 in most cases...
    Moeller_efficiency=np.sqrt(c**2*np.dot(diff_v,diff_v)-np.dot(cross_v,cross_v))/c**2/2

    def sx1(z):
        '''The sigma_x of B1, quadratic sum of betatronic and dispersive sigma'''
        return np.sqrt(sigma(beta(z, beta_x1, alpha_x1), epsilon_x1, betagamma_1)**2 \
                       + (dispersion(z, br_1*dx_1, br_1*dpx_1)*deltap_p0_1)**2)

    def sy1(z):
        '''The sigma_y of B1, quadratic sum of betatronic and dispersive sigma'''
        return np.sqrt(sigma(beta(z, beta_y1, alpha_y1), epsilon_y1, betagamma_1)**2 \
                       + (dispersion(z, br_1*dy_1, br_1*dpy_1)*deltap_p0_1)**2)

    def sx2(z):
        '''The sigma_x of B2, quadratic sum of betatronic and dispersive sigma'''
        return np.sqrt(sigma(beta(z, beta_x2, alpha_x2), epsilon_x2, betagamma_2)**2 \
                       + (dispersion(z, br_2*dx_2, br_2*dpx_2)*deltap_p0_2)**2)

    def sy2(z):
        '''The sigma_y of B2, quadratic sum of betatronic and dispersive sigma'''
        return np.sqrt(sigma(beta(z, beta_y2, alpha_y2), epsilon_y2, betagamma_2)**2 \
                       + (dispersion(z, br_2*dy_2,  br_2*dpy_2)*deltap_p0_2)**2)

    sigma_z=np.max([sigma_z1, sigma_z2])

    if not [CC_V_x_1, CC_V_y_1, CC_V_x_2, CC_V_y_2]==[0,0,0,0]:
        q = particle.elementaryChargeProton_C
        def theta_x_1(delta_z):
            # Eq. 3 of https://espace.cern.ch/acc-tec-sector/Chamonix/Chamx2012/papers/RC_9_04.pdf
            return CC_V_x_1/energy_tot1/1e9*np.sin(CC_phase_x_1 + 2*np.pi*CC_f_x_1/c*delta_z)

        def theta_y_1(delta_z):
            return CC_V_y_1/energy_tot1/1e9*np.sin(CC_phase_y_1 + 2*np.pi*CC_f_y_1/c*delta_z)

        def theta_x_2(delta_z):
            return CC_V_x_2/energy_tot2/1e9*np.sin(CC_phase_x_2 + 2*np.pi*CC_f_x_2/c*delta_z)

        def theta_y_2(delta_z):
            return CC_V_y_2/energy_tot2/1e9*np.sin(CC_phase_y_2 + 2*np.pi*CC_f_y_2/c*delta_z)

        def mx1(z, t):
            '''The mu_x of B1 as straight line'''
            return x_1 + R12_1*theta_x_1(z-c*t) + (px_1+R22_1*theta_x_1(z-c*t))*z

        def my1(z, t):
            '''The mu_y of B1 as straight line'''
            return y_1 + R34_1*theta_y_1(z-c*t) + (py_1+R44_1*theta_y_1(z-c*t))*z

        def mx2(z, t):
            '''The mu_x of B2 as straight line'''
            return x_2 + R12_2*theta_x_2(z+c*t) + (px_2+R22_2*theta_x_2(z+c*t))*z

        def my2(z, t):
            '''The mu_y of B2 as straight line'''
            return y_2 + R34_2*theta_y_2(z+c*t) + (py_2+R44_2*theta_y_2(z+c*t))*z

        def kernel_double_integral(t, z):
            return np.exp(0.5*(-(mx1(z, t) - mx2(z, t))**2/(sx1(z)**2 + sx2(z)**2) \
                               -(my1(z, t) - my2(z, t))**2/(sy1(z)**2 + sy2(z)**2) \
                               -(-br_1*c*t+z)**2/(sigma_z1**2) \
                               -( br_2*c*t+z)**2/(sigma_z2**2))) \
        /np.sqrt((sx1(z)**2 + sx2(z)**2)*(sy1(z)**2 + sy2(z)**2))/sigma_z1/sigma_z2

        integral=integrate.dblquad((lambda t, z: kernel_double_integral(t, z)),
                                   -sigma_integration*sigma_z, sigma_integration*sigma_z,-sigma_integration*sigma_z/c, sigma_integration*sigma_z/c)
        L0=f*N1*N2*nb*c/2/np.pi**(2)*integral[0]
    else:
        def mx1(z):
            '''The mu_x of B1 as straight line'''
            return x_1 + px_1*z

        def my1(z):
            '''The mu_y of B1 as straight line'''
            return y_1 + py_1*z

        def mx2(z):
            '''The mu_x of B2 as straight line'''
            return x_2 + px_2*z

        def my2(z):
            '''The mu_y of B2 as straight line'''
            return y_2 + py_2*z

        def kernel_single_integral(z):
            return np.exp(0.5*(-(mx1(z) - mx2(z))**2/(sx1(z)**2 + sx2(z)**2) \
                               -(my1(z) - my2(z))**2/(sy1(z)**2 + sy2(z)**2) \
                               -((br_1+br_2)**2*z**2)/(br_2**2*sigma_z1**2 + br_1**2*sigma_z2**2))) \
            /np.sqrt((sx1(z)**2 + sx2(z)**2)*(sy1(z)**2 + sy2(z)**2)*(sigma_z1**2 + sigma_z2**2))

        integral=integrate.quad(lambda z: kernel_single_integral(z), -20*sigma_z, 20*sigma_z)
        L0=f*N1*N2*nb/np.sqrt(2)/np.pi**(3/2)*integral[0]
    result= L0*Moeller_efficiency/1e4
    if verbose:
        print(f'Moeller efficiency: {Moeller_efficiency}')
        print(f'Integral Relative Error: {integral[1]/integral[0]}')
        print(f'==> Luminosity [Hz/cm^2]: {result}')
    return result
