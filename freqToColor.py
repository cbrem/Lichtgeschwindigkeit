#freqToColor.py

#takes a frequency and returns the hex value of a color that looks approximately
# like light at that frequency would. It should be noted that, while the
# 'anchors' at the ends of the spectrum -- 400 and 789 terahertz -- are indeed
# the red and violet ends, respectively, of the visible light spectrum, the rest
# of the frequency to color conversion is much more approximate and cartoonish.
# As frequency rises, colors returned by this function will move from red to
# orange to yellow etc., as they do in a realistic spectrum. However, the amount
# of bandwidth that each color receives is not as realistic because of the fact
# that color distrubution between the spretrums ends is based on hue (in the
# HSV format), not on frequency.

#In many cases, numbers should not given physical or mathematical significance,
# for they have been picked solely because they appear to simulate a
# scientifically accurate spectrum that decreases in brightness near the edges
# to give the appearance of drifting into ultraviolet or infrared frequencies.
# Lines containing numbers or operations chosen in such a manner will be marked
# with a #*

import colorsys

def colorize(freq,saturation=255,value=255):
    minVis = 400.0 #minumum visible frequency (red/infrared threshold)
    maxVis = 789.0 #maximum visible frequency (violet/ultraviolet threshold)
    visBand = maxVis-minVis
    if (freq<minVis) or (freq>maxVis):
        return "Gray20" #for design purposes -- in reality would be black
    else:
        THz_steps = (freq-minVis) #the number of THz by which this frequency is
                               #greater than the frequency of red light
                                       
        hue = ( ((THz_steps) * 230.0/visBand) + 240 ) % 255 # *
            #maps visible light frequencies to the number 0-254 and also moves
            #red from high hues (~240) to
                            #low hues to simulate a realistic spectrum

        return colorize2(hue, saturation, value)

#given hsv (hue, saturation, value) coordinates for a color, returns a string
# containing rgb coordinates describing the color
def colorize2(h, s, v):
    rgb=colorsys.hsv_to_rgb(h/255.0, s/255.0, v/255.0)
    r=hex(int(round(float(rgb[0])*255)))[2:]
    g=hex(int(round(float(rgb[1])*255)))[2:]
    b=hex(int(round(float(rgb[2])*255)))[2:]
    if(len(r)==1):
        r="0"+r
        
    if(len(g)==1):
        g="0"+g
        
    if(len(b)==1):
        b="0"+b
    return "#"+r+g+b

#I owe credit for color2 and for alerting me about the usefulness of colorsys to
# kratos, whose original post can be found at:
#     http://www.portugal-a-programar.org/forum/index.php?topic=34871.0
