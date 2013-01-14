#rotate.py

#This function is not entirely mine -- the version below was modified to work
# with my programing, but the original code and all of the math comes from
# a function written by Stephen D. Evans to allow for rotation of ovals in
# tKinter. His original post of the funtion can be found here:
#     http://mail.python.org/pipermail/python-list/2000-December/636222.html

import math

#returns a list of points representing a polygon. this polygon approximates
# how the oval designated by cx, cy, xRad, and yRad would appear if rotated
# counter-clockwise though an angle of rotation (rot) given in radians
def rotate(cx,cy,xRad,yRad,rot,points=100):
    point_list = []

    # create the oval as a list of points
    for point in xrange(points):

        # Calculate the angle for this point
        # 360 degrees == 2 pi radians
        theta = (math.pi * 2) * (float(point) / points)

        #find the point's rotation before rotation
        x = xRad * math.cos(theta)
        y = yRad * math.sin(theta)

        # rotate x, y
        rx = (x * math.cos(rot)) + (y * math.sin(rot))
        ry = (y * math.cos(rot)) - (x * math.sin(rot))

        point_list.append(round(cx+rx))
        point_list.append(round(cy+ry))

    return point_list

    """
    #below is same function with list comps -- use only if readable version works!
    # points is replaced with "pp" and point with "p"
    
    pp = points
    point_list=[(cx+(xRad*math.cos((math.pi*2)*(float(p)/pp)) * math.cos(rot))\
                 + (yRad*math.sin((math.pi*2)*(float(p)/pp)) * math.sin(rot)),\
                 cy+(yRad*math.sin((math.pi*2)*(float(p)/pp)) * math.cos(rot))\
                 - (xRad*math.cos((math.pi*2)*(float(p)/pp)) * math.sin(rot)))\
                for p in xrange(pp)]  

    return point_list
    """
