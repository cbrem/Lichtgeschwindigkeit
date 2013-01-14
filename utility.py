#utility.py

import math

#applies the distance formula to find the distance between (x1,y1) and (x2,y2).
# this works for any 2-vector, so it will also return the magnitude of a
# velocity vector
def distance(x1,y1,x2=0,y2=0):
    distance= math.sqrt((abs(x1-x2))**2.0 + (abs(y1-y2))**2.0)
    return distance

#checkes if the outer limits of two spherical bodies are seperated by a distance
# equal to or less than a specified limit
def seperationLessThan(body1,body2,limit):
    (ex1,ey1,rad1,color1)=body1
    (ex2,ey2,rad2,color2)=body2

    cDifference=distance(ex1,ey1,ex2,ey2)
    radSum=rad1+rad2
    if(cDifference<=radSum+limit):
        return True

#a special case of seperationLessThan: checks if the bodies are actually in
# contact
def touching(body1,body2):
    return seperationLessThan(body1,body2,0)

#another special case of seperationLessThan: checks if the bodies are seperated
# by a distance of less than a set fraction of the larger body's mass -- for the
# purposes of this game, if two bodies are in such a configuration, the smaller
# one is said to be orbiting the larger one
def inOrbit(body1,body2):
    rad1,rad2=body1[2],body2[2]
    largerRad=max(rad1,rad2)

    orbitSeperation=0.3*largerRad

    return seperationLessThan(body1,body2,orbitSeperation)

#given the coordinates of two points, returns that angle of a line between them
def angle(x1,y1,x2,y2):
    if x1==x2: #prevents divide-by-zero
        return math.pi/2.0 if y2>y1 else -1*math.pi/2
    
    tan=(y2-y1)/(x2-x1)
    arctan = math.atan(tan)
    return arctan if x2>x1 else math.pi+arctan
        #if the the second point is not in the positive x direction relative to
        #the first, correct the fact that arctan always returns a value
        #corresponding to a positive x direction

#expresses a number in the form a*10**b and rounds "a" to a given number
#of decimal places (or just the rounded number if it only has one digit in
#from of the decimal place)
def sciNotation(number,places=2):
    if number==0: 
        return str(0.0) #don't bother putting it into scientific notation
    
    else:
        powerOfTen = int( math.log(abs(number),10) )
        aUntruncated = str( number / (10**powerOfTen) )
        if -2 <= powerOfTen <= 0:
            return str(number)[:4-powerOfTen] #return the first 4 characters
                # (x.xx) for a number on the order of 1, plus one digit for
                # every order of magnitude less than ten that the number is
        else:
            #this is the funtion's normal mode of operation
            a = aUntruncated[:2+places] #include only that one's digit, the
                                        # the decimal, and the given number of
                                        # places after the decimal (2+places
                                        # characters total)
            return "%s * 10^%d" % (a,powerOfTen)

#calculates the mass of an object when given its radius -- assumes that all
# objects have the same density and treats them as three-dimensional
def massFromRad(rad,density):
    volume = (math.pi*4/3) * rad**3
    mass = volume * density
    return mass

#returns the position on a 2D Cartesian plane of a given point, whose position
# on a polar plane is given by rad and angle
def polarToCartesian(rad,angle):
    x = rad * math.cos(angle)
    y = rad * math.sin(angle)

    return (x,y)

#finds the midpoint of p1=(x1,y1) and p2=(x2,y2)
def midpoint(p1,p2):
    (x1,y1)=p1
    (x2,y2)=p2

    xMid=(x1+x2)/2.0
    yMid=(y1+y2)/2.0

    midpoint=(xMid,yMid)
    return midpoint

#flips p1=(x1,y1) over p2=(x2,y2)
def flip(p1,p2):
    (x1,y1)=p1
    (x2,y2)=p2

    xFlip=2*x2-x1
    yFlip=2*y2-y1

    flippedPoint=(xFlip,yFlip)
    return flippedPoint

#takes a number of seconds as a float -- returns a string equal to this number
# of seconds expressed in clock notation ("hours:minutes:seconds")
def clockTime(time):
    #seconds
    totalSeconds=int(round(time)) #fractions of seconds will not be displayed
    secPerMin=60
    secs=totalSeconds%secPerMin
    secStr=str(secs) if secs>=10 else "0%d" % secs
                                            #make sure  secStr is double-digit
    #minutes
    minPerHour=60
    totalMins=totalSeconds/secPerMin
    mins=totalMins%minPerHour
    minStr=str(mins) if mins>=10 else "0%d" % mins
                                            #make sure  minStr is double-digit
    #hours
    totalHours=totalMins/minPerHour
    hourStr=str(totalHours)

    clockTime="%s : %s : %s" % (hourStr,minStr,secStr)
    return clockTime

#returns the sum of all the elements in a dictionary -- if any element is not
# a real number, returns zero
def sumDictElements(dict):    
    sum=0
    for key in dict:
        value=dict[key]
        if isReal(value): sum+=value
        else: return 0
    return sum

#returns True if the value sent to it is a real number (an integer, float, or
# long). returns False otherwise
def isReal(value):
    if isinstance(value,int)\
       or isinstance(value,float)\
       or isinstance(value,long):
        return True
    else: return False
