#physics.py

import math, utility

#relativistically adds two velocities, v and u, and returns their sum, w;
# each velocity is expressed as a 2-vector in the form (x,y),(x,y);
# treats v as the velocity of a relativistic reference frame and u as the
# velocity of something within that frame
def velocityAddition(v,u,gamma_v,c):
    (vx,vy) = v
    (ux,uy) = u
    dot_VU = dot(v,u)/c**2

    #using the values calculated above, calculates one component at a time of
    # the velocity resulting from the relativistic addition of v and u
    def velocityAddition2(vComp,uComp):
        # if the relativistical velocity sum is w:
        #         1                            gamma_v 
        # w = -------- * [ vComp * ( 1+dot_VU*--------- ) + uComp/gamma_v ]
        #     1+dot_VU                        1+gamma_v
        return (1/(1+dot_VU)) * \
               (vComp*(1+dot_VU*(gamma_v/(1+gamma_v)))+uComp/gamma_v)

    wx = velocityAddition2(vx,ux)
    wy = velocityAddition2(vy,uy)
    w = (wx,wy)
    return w

#returns the dot product of two 2-vectors 
def dot(v1,v2):
    (v1x,v1y) = v1
    (v2x,v2y) = v2
    return v1x*v2x+v1y*v2y

#given the position and speed of the ship relative to earth on the x and y axes,
# does calculus to find the rate at which the ship's distance from the earth is
# changing. the result, called vEarth, is the relative movement of the earth-
# and ship-reference frames and is crucial to relativistic calculations
def vEarth(v,eCords):
    #                  d ex          d ey
    #           2*ex * ---- + 2*ey * ----
    #                   dt            dt        ex*vX + ey*vY
    # vEarth = --------------------------- = -------------------
    #           2 * (ex^2 + ey^2)^0.5         (ex^2 + ey^2)^0.5
    
    (vX,vY) = v
    (ex,ey) = eCords

    vEarth = (ex*vX + ey*vY) / utility.distance(ex,ey)
    return vEarth

#given a velocity 2-vector and c, calcultes the relativitstic factor beta. Beta
# is simply the factor by which c must be multiplied to yield a give speed
def beta(v,eCords,c):
    vRelativeToEarth = vEarth(v,eCords)

    beta= vRelativeToEarth/c
    return beta

#calculates gamma for two reference frames moving relative to eachother with
# speed equal to the 2-vector v; gamma is a unitless relativistic factor which
# determines the magnitude of many relativistic effects, such as time
# dilation and Lorentz contraction (shortening of moving objects)
def gamma(beta):
    gamma = 1/math.sqrt(1 - beta**2) #definition of gamma
    return gamma 

#uses the Tsiolkovsky rocket equation to calculate the change in velocity that
# a rocket with effective velocity vEff (constant for a given engine) and
# initial mass m0 experiences when it burns a mass=mf of fuel with  
def deltaVRocket(m0,mf,vEff):
    #                     m0
    # deltaV= vEff * ln ------
    #                    m0-mf
    deltaV = vEff * math.log( m0/(m0-mf),math.e )
    return deltaV

#calculates the gravitional force between two objects with masses M and m
# seperated by a distance d 
def gravForce(G,M,m,d):
    #              G*M*m
    # forceGrav = -------
    #               d^2
    forceGrav = G*M*m / d**2
    return forceGrav

#determines the velocity attained by a mass m acted on a force F for a time t.
# F=ma is true only for situations in which the accelerating object has constant
# mass, so this function is an approximation.
def vFromForce(F,m,t):
    a = F/m #approximately Newton's second law
    v = a*t
    return v
    
#an observer will see the progression of time in a relatively moving frame of
# reference slow down by a factor of gamma (a relativistic factor)
def timeDilation(time,gamma):
    return time/gamma

#when objects are observed to move quickly, their length is reduced by a factor
# of a gamma
def lorentzContraction(length,gamma):
    return length/gamma

#objects moving quickly relative to a stationary observer will have the
# frequency of the light leaving them shifted based on the relativistic factor
# beta. as a result, their color will change -- this is the origin for the terms
# "redshift" and "blueshift"
def dopplerShift(properFreq,beta):
    newFreq = properFreq * math.sqrt(1-beta)/math.sqrt(1+beta)
    return newFreq

#integrate everything for more accurate results????
