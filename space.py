#space.py

#determines if a fixed star or space-object will show at least partially on the
# screen
def onScreen(sx,sy,sRad,data2):
    (gameLeft,gameRight,gameTop,gameBottom)=data2
    if (gameLeft<sx+sRad and sx-sRad<gameRight) and\
       (gameTop<sy+sRad and sy-sRad<gameBottom):
        return True
    else:
        return False

#determines which areas of the space to be drawn this timestep were not drawn
# during the previous timestep
def newSpace(data2):
    return

#translates a point from earth-coordinates (ex,ey) dictating distance from Earth
# in meters to screen-coordinates (sx,sy) dictating position on
# tKinter's canvas in pixels
def eCoordsToSCoords((ex,ey),data1):
    #unpacking data
    (exShip,eyShip,sxShip,syShip,mPerPixel)=data1
    #location relative to the ship (in meters)
    shipX,shipY=ex-exShip,ey-eyShip

    #location relative to the ship after zoom (in pixels)
    zx,zy,=shipX/mPerPixel,shipY/mPerPixel
    
    #location on the screen (in pixels)
    sx,sy=sxShip+zx,syShip-zy #accounts for y-axis inversion

    return (sx,sy)

#the inverse of eCoordsToSCoords: translates a point for tKinter
# screen-coordinates to Earth-coordinates
def sCoordsToECoords((sx,sy),data1):
    #unpacking data
    (exShip,eyShip,sxShip,syShip,mPerPixel)=data1  
    #location relative to the ship after zoom (in pixels)
    zx,zy=sx-sxShip,-1*(sy-syShip)#accounts for y-axis inversion

    #location relative to the ship before zoom (in meters)
    shipX,shipY=zx*mPerPixel,zy*mPerPixel

    #location relative to earth before zoom (in meters)
    ex,ey=shipX+exShip,shipY+eyShip

    return (ex,ey)
