# -*- coding: cp1252 -*-

#lichtgeschwindigkeit.py
#Connor Brem
#Section E

from Tkinter import *
import math, random, string
import utility, physics, levels, space, rotate, freqToColor

################################################################################
#################### main run function #########################################
################################################################################

def playLightSpeed():
    global canvas
    root=Tk()

    #make sure that the canvas and window fill the screen
    canWidth,canHeight = root.winfo_screenwidth(),root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (canWidth,canHeight))
    canvas=Canvas(root, width=canWidth, height=canHeight)
    canvas.pack()

    class Struct: pass
    canvas.data=Struct()
    canvas.data.canWidth=canWidth
    canvas.data.canHeight=canHeight
    
    initProgram()
    root.bind("<Key>",recordPresses)
    root.bind("<KeyRelease>",recordReleases)
    root.mainloop()

################################################################################
################################ timer #########################################
################################################################################

def timerFired():
    state=canvas.data.state
    processPresses(state)
    
    stateAfterPresses=canvas.data.state
    updateModel(stateAfterPresses) 
    redrawAll(stateAfterPresses)
    
    canvas.after(canvas.data.delay,timerFired)

################################################################################
################################ updateModel ###################################
################################################################################

#update's the stored model of the game to be drawn by redrawAll()
def updateModel(state):
    if(state=="startScreen" or state=="controls"):
        pass
        
    elif(canvas.data.exploding):
        animateExplosion()

    elif(not canvas.data.exploded):
        performZooms()
        storePosition()
        if canvas.data.ghost: findGhost()
        if not canvas.data.suspendPhysics: doPhysics()
        prepareToDraw()
        findClosest()
        checkObjectives()

################################################################################
################################# music ########################################
################################################################################

def initMusic():
    canvas.data.music=True
    canvas.data.songs=["nachtmusik.wav"]
    updateMusic()

def updateMusic():
    if canvas.data.music:
        #play a song
        song = random.choice(canvas.data.songs)
        winsound.PlaySound(song, winsound.SND_FILENAME | winsound.SND_ASYNC)
    else:
        #turn off any songs playing
         winsound.PlaySound(None, winsound.SND_FILENAME)

################################################################################
################################ active ########################################
################################################################################

#preforms the zooms stored by processPresses
def performZooms():
    timeZoomToPerform=canvas.data.timeZoomToPerform
    spaceZoomToPerform=canvas.data.spaceZoomToPerform
    
    if canvas.data.timeZoomToPerform!=None:
        timeZoom(timeZoomToPerform)
        canvas.data.timeZoomToPerform=None
    if canvas.data.spaceZoomToPerform!=None:
        spaceZoom(spaceZoomToPerform)
        canvas.data.spaceZoomToPerform=None

def storePosition():
    #each timestep, before the ships position changes, store the position from the
    # previous timestep for use by certain funtions
    def temporaryStorage():
        canvas.data.old_exShip=canvas.data.exShip
        canvas.data.old_eyShip=canvas.data.eyShip

    # adds ex and ey to a dictionary for use by "ghosts" during later plays of
    # the same level. They are stored as a tuple with the elapsed number of
    # minSPerStep's (minSteps)as the key
    def longtermStorage():
        #though the time step has not necessarily been at the smallest possible
        # setting for the duration of this level, positions must be stored as if
        # it was in order to make their dictionary keys usable by all possible
        # later plays of this level. below is the elapsed time that this
        # function is called, in units of minSteps
        startMinSteps=canvas.data.minSteps=\
                    int(round(canvas.data.earthSeconds/canvas.data.minSPerStep))

        #below is the length of the current timestep in units of minSteps. The
        # ship's position will be stored as its postion for the number of
        # minSteps calculated below
        minStepsPerCurrentStep=\
                    int(round(canvas.data.sPerStep/canvas.data.minSPerStep))
                                
        for extraMinSteps in xrange(minStepsPerCurrentStep):
            equivMinSteps=startMinSteps+extraMinSteps
            ex,ey,vX,vY=canvas.data.exShip,canvas.data.eyShip,canvas.data.vX,\
                canvas.data.vY
            canvas.data.movesThisLevel[equivMinSteps]=((ex,ey),(vX,vY))
    
    temporaryStorage()
    if(canvas.data.state=="active"):longtermStorage()
        #it is not necessary to store what the ghost does after it wins

#determines where to draw the high score ghost if there is a recorded position
# for this time and if it is one the screen
def findGhost():
    try:
        data1=(canvas.data.exShip,canvas.data.eyShip,canvas.data.sxShip,\
               canvas.data.syShip,canvas.data.mPerPixel)
        
        level,minSteps = canvas.data.level,canvas.data.minSteps
        (eCoordsGhost,vGhost) = canvas.data.highScoreMoves[level][minSteps]
        sCoordsGhost = space.eCoordsToSCoords(eCoordsGhost,data1)
        
        (canvas.data.sxGhost,canvas.data.syGhost) = sCoordsGhost
        (canvas.data.vXGhost,canvas.data.vYGhost) = vGhost

        canvas.data.betaGhost,canvas.data.gammaGhost = \
                            findFactors(vGhost,eCoordsGhost)
            
    except:
        #print "There's no ghost to find!"
        canvas.data.ghost=False #if there are no more ghost positons left to
                                # retrieve (if "time" corresponds to an index that
                                # is out of range), stop trying to retrieve them

################################################################################
############################### prepareToDraw #################################
################################################################################

#determines what from the model should be drawn this timestep and where it
# should be drawn -- packages things to be drawn nicely for redrawAll
def prepareToDraw():
    spaceToDraw()
    shipsToDraw()

#make sets of the objects and fixed stars that should be drawn each timestep;
# also, finds which object should be drawn on the instrument panel as the
# closest object
def spaceToDraw():
    data1=(canvas.data.exShip,canvas.data.eyShip,canvas.data.sxShip,\
           canvas.data.syShip,canvas.data.mPerPixel)
    data2=(canvas.data.gameLeft,canvas.data.gameRight,canvas.data.gameTop,
           canvas.data.gameBottom)
    #updates the set of fixed stars every timestep, deleting those to far from
    # the ship and adding new ones as necessary
    def updateFixedStars():
        #each timestep, some stars that were drawn during the last timestep
        # move out of the range of the screen -- this function flips these
        # stars' earth-coordinates around the midpoint between the ship's
        # present positon and its position from last timestep, giving the
        # appearence of continuous random star generation
        def flipOffScreenStars():
            midpoint=utility.midpoint((canvas.data.exShip,canvas.data.eyShip),\
                                (canvas.data.old_exShip,canvas.data.old_eyShip))
            #flippedStars=0
            flipped,notFlipped=set(),set() #temporary sets
            
            for star in canvas.data.fixedStars:
                (ex,ey,rad,color)=star
                (sx,sy)=space.eCoordsToSCoords((ex,ey),data1)
                if space.onScreen(sx,sy,rad,data2):
                    notFlipped.add(star)
                else:
                    #flippedStars+=1
                    flip_ex,flip_ey=utility.flip((ex,ey),midpoint)
                    flippedStar=(flip_ex,flip_ey,rad,color)
                    flipped.add(flippedStar)
                    
            canvas.data.fixedStars=flipped.union(notFlipped)
            #print "I flipped %d stars this timestep." % flippedStars
        def addNewStars():
            pass
              
        flipOffScreenStars()
        
    def thingsToDraw():
        canvas.data.objectsToDraw.clear()
        canvas.data.fixedStarsToDraw.clear()
        #picks which of the objects in canvas.data.objects are within the
        # dimensions of the screen this timestep and should, therefore, be sent
        # to drawObjects
        def objectsToDraw():
            objects=canvas.data.objects
            for object in objects:
                (ex,ey,rad,color)=objects[object]
                (sx,sy)=space.eCoordsToSCoords((ex,ey),data1)
                sRad=rad/canvas.data.mPerPixel
                if space.onScreen(sx,sy,sRad,data2):
                    drawChars=(sx,sy,sRad,color)
                    canvas.data.objectsToDraw.add(drawChars)
                
        objectsToDraw()
        fixedStarsToDraw()

    updateFixedStars()
    thingsToDraw()

#like objectsToDraw, but adds every fixed star, as
# canvas.data.fixedStars is maintained so that it only contains stars
# that will appear on the screen. this is called in "startScreen"
def fixedStarsToDraw():
    data1=(canvas.data.exShip,canvas.data.eyShip,canvas.data.sxShip,\
           canvas.data.syShip,canvas.data.mPerPixel)
    for star in canvas.data.fixedStars:
        (ex,ey,rad,color)=star
        (sx,sy)=space.eCoordsToSCoords((ex,ey),data1)
        drawChars=(sx,sy,rad,color)
        canvas.data.fixedStarsToDraw.add(drawChars)

#generate enough fixed stars to refill canvas.data.fixed stars to a number of
# elements equal to totalFixedStars. also called once in "startScreen"
def generateFixedStars():
    gameLeft,gameRight,gameTop,gameBottom=canvas.data.gameLeft,\
                canvas.data.gameRight,canvas.data.gameTop,canvas.data.gameBottom
    data1=(canvas.data.exShip,canvas.data.eyShip,canvas.data.sxShip,\
           canvas.data.syShip,canvas.data.mPerPixel)

    starsToGenerate=canvas.data.totalFixedStars-len(canvas.data.fixedStars)
    for starToGenerate in xrange(starsToGenerate):
        sx=random.randint(gameLeft,gameRight)
        sy=random.randint(gameTop,gameBottom)
        (ex,ey)=space.sCoordsToECoords((sx,sy),data1)
        rad=random.choice(canvas.data.fixedStarRadii)
        color=random.choice(canvas.data.fixedStarColors)
        star=(ex,ey,rad,color)
        canvas.data.fixedStars.add(star)

def shipsToDraw():

    def prepareCapsule():
        canvas.data.moveDirection = direction = \
                            utility.angle(0,0,canvas.data.vX,canvas.data.vY)
        
        canvas.data.rzdBodyPoints,canvas.data.rzdWindowPoints=\
            rotateZoomShip(canvas.data.dRadShip,canvas.data.properRadShip,
                           canvas.data.sxShip,canvas.data.syShip, direction)

    def prepareGhost():
        canvas.data.ghostDirection = direction = \
            utility.angle(0,0,canvas.data.vXGhost,canvas.data.vYGhost)
        try:
            canvas.data.rzdBodyPointsGhost,canvas.data.rzdWindowPointsGhost=\
                rotateZoomShip(canvas.data.dRadGhost,canvas.data.properRadShip,
                           canvas.data.sxGhost,canvas.data.syGhost, direction)
        except:
            #depending on when in the timestep the player initializes the ghost,
            # the game may attempt to draw the ghost without finding it first
            pass
            #print the ghost hasn't been found yet!
        
    #given radii as seem from the Earth's frame of reference (in meters and
    # already relativistically dilated), returns the ship's shape and position
    # as a polygon that is rotated and zoomed to pixel-scale in addition to
    # being relativistically dilated
    def rotateZoomShip(dRad,properRad,sx,sy,direction):
        #radii in the Earth's frame of reference, now zoomed to be in pixels
        mPerPixel = canvas.data.mPerPixel
        zdRadShip = dRad/mPerPixel #radius after zooming and dilation
        zProperRadShip = properRad/mPerPixel #radius after only zooming
        zdRadWindow = zdRadShip/2.0
        zProperRadWindow = zProperRadShip/2.0
            #the radius is the window is defined as half the radius of the ship

        #finally, these radii are assigned to directions -- dRad is the radius
        # in the direction of the ship's movement, while the radius in the
        # direction perpendicular to the ships direction of movement stays
        # at properRad (that is, it is not relativistically dilated). These
        # radii are used to produce a polygon that approximates the rotated
        # oval that is the ship, as seen from the earth's perspective, in pixels
        rzdBodyPoints = \
                    rotate.rotate(sx,sy,zdRadShip,zProperRadShip,direction)
        rzdWindowPoints = \
                    rotate.rotate(sx,sy,zdRadWindow,zProperRadWindow,direction)
        return rzdBodyPoints, rzdWindowPoints
    
    prepareCapsule()
    if canvas.data.ghost: prepareGhost()

################################################################################
############################### closest ########################################
################################################################################

#compares the position relative to the ship of every object in
# canvas.data.objects to the position of the closest object from the
# previous timestep
def findClosest():
        objects=canvas.data.objects
        exShip,eyShip=canvas.data.exShip,canvas.data.eyShip
        
        closest=canvas.data.closest
        closeChars=objects[closest]
        exClose,eyClose,radClose=closeChars[0],closeChars[1],closeChars[2]
        closestDistance=utility.distance(exShip,eyShip,exClose,eyClose)-radClose

        for object in objects:
            objChars=objects[object]
            exObj,eyObj,radObj=objChars[0],objChars[1],objChars[2]
            objDistance=utility.distance(exShip,eyShip,exObj,eyObj)-radObj
            if objDistance<closestDistance:
                closest=object
                closestDistance=objDistance

        canvas.data.closestDistance,canvas.data.closest=closestDistance,closest

################################################################################
############################### highscores #####################################
################################################################################

#these high scores will persist between game-mode switches, but will not be
# saved when the game closes
def initHighScores():
    canvas.data.highScores=dict()
    canvas.data.highScoreMoves=dict() #a 2-dimensional dictionary

#check the current score against the standing high score for the level. If the
# current score is higher, store the moves that occured this level for ghosting
# purposes
def updateHighScores():
    level=canvas.data.level
    oldHighScore=canvas.data.highScores[level]
    currentScore=canvas.data.earthSeconds
    if currentScore<=oldHighScore or oldHighScore==None:
        canvas.data.highScores[level]=currentScore
        canvas.data.totalScore=utility.sumDictElements(canvas.data.highScores)
        canvas.data.highScoreMoves[level]=canvas.data.movesThisLevel
        canvas.data.newHighScore=True

################################################################################
############################### exploding ######################################
################### (not a state, but similar to one) ##########################

#set up the explosion animation
def explode():
    canvas.data.exploding=True
    canvas.data.exploded=True
    canvas.data.explosionSteps=0
    canvas.data.explosionStepsMax=5
    canvas.data.radExplosion=zRadShip=canvas.data.properRadShip

def animateExplosion():
    stepsMax=canvas.data.explosionStepsMax
    if(canvas.data.explosionSteps<=stepsMax):
        canvas.data.radExplosion*=1.2
        canvas.data.explosionSteps+=1
    else:
        canvas.data.exploding=False
        canvas.data.suspendPhysics=True

################################################################################
######################## transitions between states ############################
################################################################################

#stop the model from updating, pausing the game
def pauseGame():
    canvas.data.suspendPhysics=True
    canvas.data.state="paused"

#resume the game after a pause
def unpauseGame():
    canvas.data.explainControls=False
    canvas.data.instructionNumber=0
    canvas.data.suspendPhysics=False
    canvas.data.levelAlreadyAttempted=True
    canvas.data.state="active"

#runs only once when a level is failed
def failLevel():
    canvas.data.state="levelFailed"
    canvas.data.currentPutDown = random.choice(canvas.data.putDowns)

def winLevel():
    canvas.data.state="levelWon"
    canvas.data.levelWonAlready=True
    canvas.data.currentCompliment = random.choice(canvas.data.compliments)
    updateHighScores()

def winGame():
    canvas.data.state="gameWon"
    canvas.data.featuresUnlocked=True #the next time the game runs, more
                                      # features will be available

################################################################################
######################## general init functions ################################
################################################################################

def initProgram():
    canvas.data.level=0
    initColors()
    initImages()
    initDimensions()
    initKeys()
    initHighScores()
    initStartScreen()
    initPhysics()
    #initMusic()
    initZooms()
    initDisplay()
    timerFired()
    
def initStartScreen():
    canvas.data.state="startScreen"
    canvas.data.startButtons=["New Game","Controls"]
    #canvas.data.startButtons=["New Game","Select Level","See the Physics"]
    canvas.data.buttonSelection=0 #new game is initially selected
    canvas.data.buttonSpacing=canvas.data.gameHeight/8.0
        #vertical spacing between start-buttons
    canvas.data.buttonDefaults=(canvas.data.colors["button0"],\
                canvas.data.colors["button1"],canvas.data.colors["button2"])
    canvas.data.delay=50
        #the start screen refreshes every 50 milliseconds

def initDimensions():
    canWidth=canvas.data.canWidth
    canHeight=canvas.data.canHeight

    #define edges where the game meets the frame
    gameLeft=canvas.data.gameLeft=160
    gameRight=canvas.data.gameRight=canWidth-gameLeft
    gameTop=canvas.data.gameTop=75
    gameBottom=canvas.data.gameBottom=canHeight

    canvas.data.gameWidth=gameRight-gameLeft
    canvas.data.gameHeight=gameBottom-gameTop
    canvas.data.frameWidth=canvas.data.gameLeft

def initColors():
    colors=dict()
    #start colors
    colors["button0"]="Light Goldenrod"
    colors["button1"]="Purple"
    colors["button2"]="Black"
    colors["buttonSelect"]="Gold"
    #frame colors
    colors["title"]="Gold"
    colors["back"]="Black"
    colors["frame0"]="Gray20"
    colors["frame1"]="Purple"
    colors["sidebar0"]="Gold"
    colors["sidebar1"]="Purple"
    colors["complete"]="White"
    #ship colors
    colors["ship0"]="Gray"
    colors["ship1"]=None #initialized in initShip, calculated every turn after
    colors["ship2"]="Black"
    colors["moveArrow"]="White"
    colors["ghost0"]="Ghost White"
    colors["ghost1"]=None
    colors["ghost2"]="Gray50"
    colors["flame"]="Orange"
    colors["explosion"]="Orange"

    canvas.data.colors=colors

def initImages():
    canvas.data.controlsImage = \
        PhotoImage(file="controls.gif") #image created by Lydia Utkin

def initKeys():
    canvas.data.presses=set() #records the keypresses within a timestep
    canvas.data.holdablePresses=set() #records presses intented to be held
    canvas.data.holdablesReleased=set() #records key releases within a timestep
    canvas.data.movements={"d":(1,0), "w":(0,1), "a":(-1,0), "s":(0,-1)}
                    #movements are unit vectors showing the direction of motion
    
################################################################################
######################## init functions for active #############################
################################################################################

#runs only when the player advances from the start screen
def buttonSelected():
    selected = canvas.data.startButtons[canvas.data.buttonSelection]
    if selected=="New Game":
        #start the first level
        canvas.data.level=0
        canvas.data.state="paused"
        nextLevel()
    elif selected=="Controls":
        canvas.data.state="controls"

    #elif selected=="Select Level":
    #    #change this to go to level selection window
    #    canvas.data.level=0
    #    canvas.data.state="paused"
    #    nextLevel()
    #elif selected=="See the Physics":
    #    #change this to go to physics window
    #    pass

#runs whenever the player advances to a new level or replays the current level
def initLevel():
    canvas.data.objects,canvas.data.objectsToVisit,canvas.data.instructions=\
                                            levels.load(canvas.data.level)
    canvas.data.ghost=False
    canvas.data.explainControls=False
    canvas.data.numberOfInstructions=len(canvas.data.instructions)
    canvas.data.exploded=False #the explosion is currently being animated
    canvas.data.exploding=False #the ship has exploded at some point in the past
    canvas.data.newHighScore=False
    canvas.data.delay=50 #the timer wil fire every 50 real-world milliseconds
    canvas.data.objectsVisited=set()
    canvas.data.movesThisLevel=dict()

    initPhysics()
    initDisplay()
    initZooms()

    #set the game to pause and show the first instruction
    canvas.data.instructionNumber=1
    pauseGame()

def initDisplay():
    def initSpace():
        canvas.data.radHaloObject=5.0
        canvas.data.closest="Earth"
        canvas.data.objectsToDraw=set()
        canvas.data.fixedStarsToDraw=set()
        #translate all distances and radii from common units (light years, solar
        # radii) to meters
        def translateDimensions():
            mPerLy,mPerRSol=canvas.data.mPerLy,canvas.data.mPerRSol
            translatedObjects=dict()
            for object in canvas.data.objects:
                (ex,ey,rad,color)=canvas.data.objects[object]
                translatedObjectChars=(ex*mPerLy,ey*mPerLy,rad*mPerRSol,color)
                translatedObjects[object]=translatedObjectChars
            canvas.data.objects=translatedObjects
        #generates the initial set of random fixed stars to draw on the screen
        def initFixedStars():
            canvas.data.fixedStars=set()
            canvas.data.totalFixedStars = \
                        250 if canvas.data.state=="startScreen" else 50
            canvas.data.fixedStarRadii=[1.0,2.0,3.0] #in pixels
            canvas.data.fixedStarColors=["White","Steel Blue","Yellow","red"]
            generateFixedStars()
            fixedStarsToDraw()
                #for the first step only, bypass on-screen checking for stars

        if canvas.data.state!="startScreen": translateDimensions()
        initFixedStars()

    def initShip():
        canWidth=canvas.data.canWidth
        gameTop,gameHeight=canvas.data.gameTop,canvas.data.gameHeight

        #these give the ship's actal location on the screen (constant)
        canvas.data.sxShip=canWidth/2.0 # (in pixels)
        canvas.data.syShip=gameTop+(gameHeight)/2.0 # (in pixels)

        #these give the ship's location relative to earth. these will change
        canvas.data.exShip=exShip=0.0 # (in meters)
        canvas.data.eyShip=180.0#starting orbit (in meters)
        canvas.data.dRadShip=canvas.data.properRadShip=2.0 #for now, the radius
            # of the ship after relativistic dilation (dRad) is equal it its
            # proper radius (a technical term for its radius before dilation)
            # (both values are in meters)
        canvas.data.radHaloShip=9.0 # (in pixels)
        canvas.data.moveArrow=False
        canvas.data.moveArrowRad=40.0

        canvas.data.dryMass=1000.0 #mass of ship minus fuel (in kg)
        canvas.data.fuelMass=canvas.data.initFuelMass=800.0
        canvas.data.outOfFuel=False
        canvas.data.vX=canvas.data.vY=0.0 #velocity (in m/s)

        canvas.data.colors["ship1"]="Yellow"
        canvas.data.windowFrequency=canvas.data.properFrequency=500.0
            #properFrequency is the frequency of the light emitted by the ship's
            # window, in terahertz,in the ship's frame of reference.
            #windowFrequency is this frequency in the earth's frame of
            # reference. At the beginning of the game, these two values are
            # equal, and the ship's color is yellow in both frames

        #each key is the movement direction that causes a given thruster to fire
        canvas.data.thrustersOn=\
                            {(1,0):False,(0,1):False,(-1,0):False,(0,-1):False}
        canvas.data.thrusterWidth=1.0

    def initHUD():
        canvas.data.closestArrowRad=canvas.data.gameLeft/4.0
        canvas.data.relativityStats=False
        canvas.data.instructionNumber=0
        canvas.data.numberOfInstructions=1
        canvas.data.compliments=["Wunderbar","Super","Spitze","Prima"]
            #compliments for a win
        canvas.data.putDowns=["Dunnkopf","Kindchen"]
            #putdowns for a loss
        canvas.data.xBuffer=canvas.data.gameLeft/10.0
            #boundries of frame text
        canvas.data.sideSpacing = canvas.data.gameHeight/32.0
            #vertical space between sidebar elements
        canvas.data.centerSpacing = canvas.data.gameHeight/24.0
            #vertical space between center-text lines
    initHUD()
    initShip()
    initSpace()

def initZooms():
    canvas.data.minSPerStep=canvas.data.sPerStep/4.0 #prevent excessive
    canvas.data.maxSPerStep=canvas.data.sPerStep*4.0 # time-zooming
    canvas.data.timeZoomToPerform=None
    canvas.data.timeZooms={"Right":1.25,"Left":0.8}
        #right doubles the number of seconds represented by the timestep,
        #left halves it

    canvas.data.minMPerPixel=canvas.data.mPerPixel/4.0 #prevent excessive
    canvas.data.maxMPerPixel=canvas.data.mPerPixel*1024.0 # space-zooming
    canvas.data.spaceZoomToPerform=None
    canvas.data.spaceZooms={"Down":2.0,"Up":0.5}
        #down doubles the number of meters represented by a pixel, zooming out;
        #up halves it, zooming in
    
################################################################################
################################ physics #######################################
################################################################################

def initPhysics():    
    canvas.data.mPerRSol=1.0  #meters per solar radius [actually 6.955*(10**8)]
    canvas.data.mPerLy=1.0 #meters per lightyear [actually 9.4605284*(10**15)]

    canvas.data.G=5.0e-4#universal gravitational constant [actually 6.67384e-11]
    canvas.data.objectDensity=1000.0 #density of space-objects (in kg/m^3)
    
    canvas.data.c=1000.0 #speed of light (in m/s) [actually 2.99792458*(10**8)]
    canvas.data.gamma=1.0 #rel. factor, explained in physics.py (unitless)
    canvas.data.beta=1.0 #another rel. factor (unitless)

    canvas.data.vEff=10000.0 # (in N/(kg/s) = m/s)
    canvas.data.flowRate=10.0 # (in kg/s)
    
    canvas.data.mPerPixel=0.4 #meters per pixel
    canvas.data.sPerStep=0.1 #seconds per timestep

    canvas.data.earthSeconds=0.0 #time elapsed in the Earth's frame of reference
    canvas.data.shipSeconds=0.0 #time elapsed in the Earth's frame of reference

def thrusterOn(press):
    (xDir,yDir)=canvas.data.movements[press]
    canvas.data.thrustersOn[(xDir,yDir)]=True

################################################################################
############################### doPhysics ######################################
################################################################################

#updates the model using relativistic and classical physics
def doPhysics():
    v = (canvas.data.vX,canvas.data.vY)
    eCoords = (canvas.data.exShip,canvas.data.eyShip)
    try: canvas.data.beta,canvas.data.gamma = findFactors(v,eCoords)
    except: pass
    
    dilateLength()
    moveShip()
    moveClocks()
    dopplerShift()
    
#determine the value of the relativistic factors gamma and beta for this
# timestep
def findFactors(v,eCoords):
    c = canvas.data.c

    beta = physics.beta(v,eCoords,c)
    gamma = physics.gamma(beta)
    return beta,gamma

#Advances the in-game clock. As time can be speed or slowed in the game, this
# must be independent of real-world time.
def moveClocks():
    sPerStep=canvas.data.sPerStep
    canvas.data.earthSeconds+=sPerStep
    canvas.data.shipSeconds+=physics.timeDilation(sPerStep,canvas.data.gamma)

#relativistically dilate the ship's dimensions
def dilateLength():
    #dilated the ship's direction of motion
    gamma, properRadShip = canvas.data.gamma, canvas.data.properRadShip
    canvas.data.dRadShip = physics.lorentzContraction(properRadShip,gamma)

    #dilates the ghost's radius in the direction of motion
    if canvas.data.ghost:
        try:
            gammaGhost = canvas.data.gammaGhost
            canvas.data.dRadGhost=\
                physics.lorentzContraction(properRadShip,gammaGhost)
        except:
            pass
            #the ghost hasn't be found yet

#adjust the ship's velocity and change its postion based on that velocity
def moveShip():
    #adjust velocity if the engines have fired
    thrustersOn = canvas.data.thrustersOn
    vXInFrame = vYInFrame = 0.0

    #add velocity from engines firing
    for thrusterDir in thrustersOn:
        if thrustersOn[thrusterDir]:
            (xDir,yDir) = thrusterDir
            if abs(xDir)==1:
                vXInFrame += fireEngine(xDir)
            elif abs(yDir)==1:
                vYInFrame += fireEngine(yDir)

    #add velocity from gravitational attraction
    (deltaVXGrav,deltaVYGrav) = deltaVGrav()
    vXInFrame += deltaVXGrav
    vYInFrame += deltaVYGrav

    vOfFrame = (canvas.data.vX,canvas.data.vY)
        #velocity of the ship's frame of reference relative to Earth
    vInFrame = (vXInFrame,vYInFrame)
        #velocity of the ship in its frame from the beginning of the timestep
    (canvas.data.vX,canvas.data.vY) = physics.velocityAddition(vOfFrame,\
                                    vInFrame,canvas.data.gamma,canvas.data.c)
    
    #move the ship based on its velocity (assumes all velocity changes occur
    # at beginning of timestep and velocities are constant thereafter)
    canvas.data.exShip += canvas.data.sPerStep*canvas.data.vX
    canvas.data.eyShip += canvas.data.sPerStep*canvas.data.vY  

#calculates the change in velocity resulting from and engine-fire and burns the
# fuel associated with the engine-fire
def fireEngine(thrusterDir):
    state=canvas.data.state
    vEff,flowRate=canvas.data.vEff,canvas.data.flowRate
    m0=canvas.data.dryMass+canvas.data.fuelMass
    step=canvas.data.sPerStep
    mf=flowRate*step #mass of fuel burned during this timestep

    if (canvas.data.fuelMass-mf) >= 0:
        deltaVRocket=thrusterDir*physics.deltaVRocket(m0,mf,vEff)
        if state=="active": canvas.data.fuelMass-=mf #don't use fuel in levelWon
        return deltaVRocket      
    else:
        canvas.data.outOfFuel=True
        return 0.0

#calculates the change in velocity that the ship will undergo in the x- and y-
# directions based on the net gravitational force exerted on it by all objects
def deltaVGrav():
    sPerStep=canvas.data.sPerStep
    G=canvas.data.G
    density=canvas.data.objectDensity
    exShip,eyShip=canvas.data.exShip,canvas.data.eyShip
    m=canvas.data.dryMass+canvas.data.fuelMass
    
    forceXTotal = forceYTotal = 0.0
    for object in canvas.data.objects:
        (exObj,eyObj,radObj,color) = canvas.data.objects[object]
        M = utility.massFromRad(radObj,density)
        d = utility.distance(exShip,eyShip,exObj,eyObj)
        theta = utility.angle(exShip,eyShip,exObj,eyObj)
        gravForce = physics.gravForce(G,M,m,d)
        (forceX,forceY) = utility.polarToCartesian(gravForce,theta)
        forceXTotal += forceX
        forceYTotal += forceY

    deltaVX = physics.vFromForce(forceXTotal,m,sPerStep)
    deltaVY = physics.vFromForce(forceYTotal,m,sPerStep)

    return (deltaVX,deltaVY)

#shift the color of light coming from the ship's window based on the
# relativistic doppler effect
def dopplerShift():
    properFreq = canvas.data.properFrequency
    
    #shift the light from the ship
    canvas.data.shiftedFrequency = shiftedFreq = \
            physics.dopplerShift(properFreq,canvas.data.beta)
    canvas.data.colors["ship1"] = freqToColor.colorize(shiftedFreq)
    
    #shift the light from the ghost
    if canvas.data.ghost:
        try:
            sat=100 #intensity of window-light; for ghost is below default(255)
            shiftedFreqGhost = \
                        physics.dopplerShift(properFreq,canvas.data.betaGhost)
            canvas.data.colors["ghost1"] = \
                                    freqToColor.colorize(shiftedFreqGhost,sat)
        except:
            pass
            #ghost hasn't be found yet

################################################################################
############################### zooming ########################################
################################################################################

def timeZoomToPerform(press):
    canvas.data.timeZoomToPerform=canvas.data.timeZooms[press]

def spaceZoomToPerform(press):
    canvas.data.spaceZoomToPerform=canvas.data.spaceZooms[press]

def timeZoom(zoomFactor):
    potentialSPerStep=canvas.data.sPerStep*zoomFactor
    if (potentialSPerStep>canvas.data.maxSPerStep)\
       or (potentialSPerStep<canvas.data.minSPerStep):
        pass #don't zoom if the zoom would make time too slow or fast
    else:
        canvas.data.sPerStep=potentialSPerStep

def spaceZoom(zoomFactor):
    potentialMPerPixel=canvas.data.mPerPixel*zoomFactor
    if (potentialMPerPixel>canvas.data.maxMPerPixel)\
       or (potentialMPerPixel<canvas.data.minMPerPixel):
        pass
    else:
        #record scales before the zoom for use by zoomFixedStars
        oldMPerPixel=canvas.data.mPerPixel

        #zoom the screen
        canvas.data.mPerPixel=potentialMPerPixel

        #zoom the fixed stars' earth-coords so their screenCoords don't change
        zoomFixedStars(oldMPerPixel)

#Since the fixed stars, unlike other space-objects, move side to side but do
# not zoom, their screen-coordinates must be kept constanct during a space-zoom.
# A quick way to do this is to translate the stars' earth-coordinates to screen-
# coordinates using the pre-zoom scale and then to translate these back to
# earth-coordinates using the post-zoom scale
def zoomFixedStars(oldMPerPixel):
    oldData1=(canvas.data.exShip,canvas.data.eyShip,canvas.data.sxShip,\
              canvas.data.syShip,oldMPerPixel)
    newData1=(canvas.data.exShip,canvas.data.eyShip,canvas.data.sxShip,\
            canvas.data.syShip,canvas.data.mPerPixel)

    zoomed=set() #temporary set
    
    for oldStar in canvas.data.fixedStars:
        (oldEx,oldEy,rad,color)=oldStar
        (sx,sy)=space.eCoordsToSCoords((oldEx,oldEy),oldData1)
        (newEx,newEy)=space.sCoordsToECoords((sx,sy),newData1)
        newStar=(newEx,newEy,rad,color)
        zoomed.add(newStar)
        
    canvas.data.fixedStars=zoomed
        
def autoZoom():
    pass

################################################################################
############################### objectives #####################################
################################################################################
    
def checkObjectives():
    aprxRadShip=canvas.data.properRadShip # to simplify calculations in this
        # funtion, ignore relativistic dilation of the ship -- if it is going
        # fast enough to be significantly dilated, the user won't notice
    ship=(canvas.data.exShip,canvas.data.eyShip,aprxRadShip,None)
    objects=canvas.data.objects
   
    for object in objects:
        if canvas.data.state=="active":
            #checks to see if the ship has made it to any objective-objects
            if object in canvas.data.objectsToVisit:
                if utility.inOrbit(ship,objects[object]):
                    canvas.data.objectsVisited.add(object)
                    checkIfLevelWon()
            
        #checks to see if the ship has crashed into any objects (it is
        # intentionally possible for the player to win and to explode in
        # the same timestep)
        if utility.touching(ship,objects[object]):
            if canvas.data.state=="active": failLevel()
            explode()

#advances to the next level -- only runs once per game between any two levels
def nextLevel():
    try:
        canvas.data.level+=1
        canvas.data.highScores[canvas.data.level]=None
        canvas.data.highScoreMoves[canvas.data.level]=dict()
        canvas.data.levelAlreadyAttempted=False
        canvas.data.levelWonAlready=False
        initLevel()

    #initLevel will attempt to draw objective and objects for the new level
    # from a dictionary -- if the last level has already been reached and there
    # are no more levels to load, initLevel will raise an exception
    except:
        winGame()

#checks to see if all objective-objects have been visited
def checkIfLevelWon():
    if len(canvas.data.objectsToVisit)==len(canvas.data.objectsVisited):
        winLevel()

################################################################################
############################### redraw functions ###############################
################################################################################

def redrawAll(state):
    canvas.delete(ALL)
    drawBackground()
    if(state=="startScreen"):
        drawStartScreen()
    elif(state=="active"):
        drawActive()
    elif(state=="paused"):
        drawPaused()
    elif(state=="levelWon"):
        drawLevelWon()
    elif(state=="levelFailed"):
        drawLevelFailed()
    elif(state=="gameWon"):
        drawGameWon()
    elif(state=="controls"):
        drawControls()

################################################################################

def drawBackground():
    backColor=canvas.data.colors["back"]
    canWidth=canvas.data.canWidth
    canHeight=canvas.data.canHeight
    canvas.create_rectangle(0,0,canWidth,canHeight,fill=backColor)
    
################################################################################

def drawFrame():
    colors=canvas.data.colors
    frame0,frame1,title=colors["frame0"],colors["frame1"],colors["title"]
    canWidth=canvas.data.canWidth
    gameLeft,gameRight,gameTop,gameBottom=canvas.data.gameLeft,\
                canvas.data.gameRight,canvas.data.gameTop,canvas.data.gameBottom

    canvas.create_rectangle(0,0,gameLeft,gameBottom,fill=frame0)
    canvas.create_rectangle(0,0,canWidth,gameTop,fill=frame0)
    canvas.create_rectangle(gameRight,0,canWidth,gameBottom,fill=frame0)

    canvas.create_line(gameLeft,0,gameLeft,gameBottom,fill=frame1,width=4)
    canvas.create_line(gameRight,0,gameRight,gameBottom,fill=frame1,width=4)
    canvas.create_line(0,gameTop,canWidth,gameTop,fill=frame1,width=4)

    canvas.create_text(canWidth/2,gameTop/2,text="Lichtgeschwindigkeit",
                       font="dotum 32",fill=title)

################################################################################


def drawStartScreen():
    drawFixedStars()
    drawFrame()
    drawStartButtons()

##########################

#draws the buttons at startup for selecting game-mode at startup 
def drawStartButtons():
    colors=canvas.data.colors
    button0,button1,button2,select = colors["button0"],colors["button1"],\
                                     colors["button2"],colors["buttonSelect"]
    canWidth,gameTop = canvas.data.canWidth,canvas.data.gameTop
    spacing = canvas.data.buttonSpacing
    buttonWidth,buttonHeight = canvas.data.canWidth/5.0,spacing/2.0
    selection = canvas.data.buttonSelection

    position=5 #the first button will be in the fourth button-space from the top
    for button in canvas.data.startButtons:
        background = select if selection==(position-5) else button0
        top=gameTop+position*spacing
        colors=(background,button1,button2)
        drawButton(top,buttonWidth,button,colors)
        
        position += 1
        
#draws the a button, in the center of the screen, usable at multiple point in
# the game
def drawButton(top,width,label,colors=None):
    if colors==None: colors=canvas.data.buttonDefaults #if no colors are
                                                       # specified, use defaults
    (background,edge,text)=colors
    canWidth=canvas.data.canWidth
    spacing=canvas.data.buttonSpacing
    labelLines=label.count("\n")+1
    buttonHeight=labelLines * spacing/4.0 #assuming one button-space is four
                                          # lines of text high
    buffer=spacing/10.0 #space between the button's top and the label's top
    
    #draw background
    canvas.create_rectangle(canWidth/2-width/2,top,canWidth/2+width/2,
                            top+buttonHeight+2*buffer,fill=background)
    #draw edge
    canvas.create_rectangle(canWidth/2-width/2,top,canWidth/2+width/2,
                            top+buttonHeight+2*buffer,fill=None,outline=edge,
                            width=2)
    #draw text
    canvas.create_text(canWidth/2,top+buffer,anchor=N,
                       text=label,font="dotum 16 bold",fill=text)

################################################################################

def drawActive():
    drawSpace()
    drawShips()
    drawFrame()
    drawHUD()
    if canvas.data.instructionNumber>0: drawInstructions()
    elif canvas.data.outOfFuel: drawOutOfFuel()

#########################
    
def drawShips():
    #ghost (highscore) ship
    if canvas.data.ghost and canvas.data.state=="active": drawGhost()
    
    #player's ship
    if not (canvas.data.outOfFuel or canvas.data.state=="paused"):
        drawThrusters()
    drawCapsule()
    if canvas.data.moveArrow: drawMoveArrow()

def drawCapsule():
    colors=canvas.data.colors
    drawShip(colors["ship0"],colors["ship1"],colors["ship2"],
             canvas.data.sxShip,canvas.data.syShip,
             canvas.data.rzdBodyPoints,canvas.data.rzdWindowPoints)

def drawGhost():
    colors=canvas.data.colors
    drawShip(colors["ghost0"],colors["ghost1"],colors["ghost2"],
             canvas.data.sxGhost,canvas.data.syGhost,
             canvas.data.rzdBodyPointsGhost,canvas.data.rzdWindowPointsGhost)
    
def drawShip(color0,color1,color2,sx,sy,bodyPoints,windowPoints):
    #halo
    radHaloShip=canvas.data.radHaloShip
    canvas.create_oval((sx-radHaloShip,sy-radHaloShip),
                       (sx+radHaloShip,sy+radHaloShip),
                       fill=None,outline=color0)    
    #capsule
    canvas.create_polygon(bodyPoints,fill=color0,outline=color2)
    
    #capsule window
    canvas.create_polygon(windowPoints,fill=color1,outline=color2)

def drawThrusters():
    sxShip,syShip=canvas.data.sxShip,canvas.data.syShip
    mPerPixel=canvas.data.mPerPixel
    properRadShip=canvas.data.properRadShip
    zRadShip=properRadShip/mPerPixel
    thrustersOn=canvas.data.thrustersOn
    zThrusterWidth=canvas.data.thrusterWidth/canvas.data.mPerPixel
    flameColor=canvas.data.colors["flame"]

    for moveDir in thrustersOn:
        if thrustersOn[moveDir]:
            (xDir,yDir)=moveDir #the thruster corresponds to which movement
                                    #direction?
            xThrust,yThrust=-1*xDir,yDir #thruster will point opposite the 
                                         #direction of movement, though yMove
                                         #is flipped again to account for
                                         #tKinter's coordinate system
            xLen,yLen=2*zRadShip*xThrust,2*zRadShip*yThrust
            canvas.create_line((sxShip,syShip),(sxShip+xLen,syShip+yLen),
                               fill=flameColor,width=zThrusterWidth)
        #now turn the thruster off 
        canvas.data.thrustersOn[moveDir]=False

#superimposed on ship, shows direction of movement
def drawMoveArrow():
    sx,sy=canvas.data.sxShip,canvas.data.syShip
    rad=canvas.data.moveArrowRad
    direction=canvas.data.moveDirection
    drawArrow(sx,sy,rad,direction,canvas.data.colors["moveArrow"])

############################

def drawSpace():
    drawFixedStars()
    drawObjects()

def drawFixedStars():
    for star in canvas.data.fixedStarsToDraw:
        (sx,sy,rad,color)=star
        canvas.create_oval((sx-rad,sy-rad),(sx+rad,sy+rad),fill=color)

def drawObjects():
    for object in canvas.data.objectsToDraw:
        (sx,sy,rad,color)=object
        radHalo=canvas.data.radHaloObject
        #draw halo
        canvas.create_oval((sx-radHalo,sy-radHalo),(sx+radHalo,sy+radHalo),
                           fill=None,outline=color)
        #draw object
        canvas.create_oval((sx-rad,sy-rad),(sx+rad,sy+rad),fill=color)
        
##########################

def drawHUD():
    drawLeftSidebar()
    drawRightSidebar()

def drawLeftSidebar():
    colors=canvas.data.colors
    sidebar0,sidebar1,completeColor,button0=colors["sidebar0"],\
            colors["sidebar1"],colors["complete"],colors["button0"]
    xBuffer,gameTop,sideSpacing=canvas.data.xBuffer,canvas.data.gameTop,\
                                                    canvas.data.sideSpacing
    def leftSideText(position,text,color):
        canvas.create_text((xBuffer,gameTop+sideSpacing*position),
                           anchor=NW,fill=color,font="dotum 10",text=text)
    
    def drawFuelMeter():
        #draw the meter's label
        leftSideText(1,"Fuel Remaining:",sidebar0)
        
        #draw the meter's frame
        frameWidth = canvas.data.frameWidth
        cFrame = frameWidth/2.0
    
        canvas.create_rectangle(cFrame-frameWidth/4.0, gameTop+3*sideSpacing,
                                cFrame+frameWidth/4.0, gameTop+11*sideSpacing,
                                outline=sidebar0, width=2)

        #now draw the bar that indicates fuel left
        fuelFraction = canvas.data.fuelMass/canvas.data.initFuelMass
        initMeterHeight = 7.5*sideSpacing
        meterHeight = fuelFraction*initMeterHeight
        meterBottom = gameTop+10.75*sideSpacing
        
        canvas.create_rectangle(cFrame-frameWidth/5.0, meterBottom-meterHeight,
                                cFrame+frameWidth/5.0, meterBottom,
                                fill=None,outline=sidebar1,width=2)
    def drawObjectives():
        #draw objective header
        leftSideText(14,"Objectives:",sidebar0)

        #draw individual objectives
        position=15       
        for obj in canvas.data.objectsToVisit:
            if obj in canvas.data.objectsVisited:
                color=completeColor
                text="  You got to \n  %s!" % obj
            else:
                color=sidebar1
                text="  Get to \n  %s!" % obj
            leftSideText(position,text,color)
            position+=2 #each objective two spaces lower than the last

    def drawWonAlready():
        #draw highscore
        highScore=canvas.data.highScores[canvas.data.level]
        leftSideText(25,"Best Earth-Time: %s" % highScore,sidebar0)

        #draw message
        leftSideText(26,
            "Press Enter at any\ntime to move on to\nthe next level",sidebar1)
            
    drawFuelMeter() 
    drawObjectives()
    if canvas.data.levelWonAlready: drawWonAlready()


def drawRightSidebar():
    colors=canvas.data.colors
    sidebar0,sidebar1=colors["sidebar0"],colors["sidebar1"]
    xBuffer,gameLeft,gameRight,gameTop,sideSpacing,canWidth=\
                canvas.data.xBuffer,canvas.data.gameLeft,canvas.data.gameRight,\
                canvas.data.gameTop,canvas.data.sideSpacing,canvas.data.canWidth
    closest,closestDistance=canvas.data.closest,canvas.data.closestDistance
    closestData=canvas.data.objects[closest]
    exShip,eyShip=canvas.data.exShip,canvas.data.eyShip
    
    sPerStep,mPerPixel=canvas.data.sPerStep,canvas.data.mPerPixel
    fuel=canvas.data.fuelMass

    def rightSideText(position,text,color):
        canvas.create_text((gameRight+xBuffer,gameTop+sideSpacing*position),
                           anchor=NW,fill=color,font="dotum 10",text=text)

    def drawClosest():
        closeColor=closestData[3]
        rightSideText(1,"Closest Object",sidebar0)
        rightSideText(2, "%s:  " % closest, closeColor)
        rightSideText(3,"%s m" % utility.sciNotation(closestDistance),\
                      closeColor)
        
    def drawCoords(): 
        #xLy=exShip/canvas.data.mPerLy # (in lightyears)
        #yLy=eyShip/canvas.data.mPerLy # (in lightyears)
        rightSideText(9,"X: %s m" % utility.sciNotation(exShip),sidebar0)
        rightSideText(10,"Y: %s m" % utility.sciNotation(eyShip),sidebar0)

    def drawSpeedometer():
        vX,vY = canvas.data.vX,canvas.data.vY
        rightSideText(12,"X Spd: %s m/s" % utility.sciNotation(vX),sidebar0)
        rightSideText(13,"Y Spd: %s m/s" % utility.sciNotation(vY),sidebar0)

    def drawZooms():
        rightSideText(15,"Timestep: %s s" % utility.sciNotation(sPerStep),\
                      sidebar0)
        rightSideText(16,"m/Pixel: %s" % utility.sciNotation(mPerPixel),\
                      sidebar0)
        
    def drawClocks():
        earthClock=utility.clockTime(canvas.data.earthSeconds)
        rightSideText(19,"Earth-Time Elapsed:\n  "+earthClock,sidebar0)
        
        shipClock=utility.clockTime(canvas.data.shipSeconds)
        rightSideText(21,"Ship-Time Elapsed:\n  "+shipClock,sidebar0)

    def drawClosestArrow():
        exClosest,eyClosest,color=closestData[0],closestData[1],closestData[3]
        closestDirection=utility.angle(exShip,eyShip,exClosest,eyClosest)
        
        sx,sy=(gameRight+canWidth)/2.0,gameTop+6*sideSpacing
        rad=canvas.data.closestArrowRad

        drawArrow(sx,sy,rad,closestDirection,color)

    #draw physic information that may not interest most users
    def drawRelativityStats():
        beta,gamma = canvas.data.beta,canvas.data.gamma
        rightSideText(25,"Relativity:", sidebar1)        
        rightSideText(26,"  Beta: %s" % utility.sciNotation(beta),sidebar0)
        rightSideText(27,"  Gamma: %s" % utility.sciNotation(gamma),sidebar0)

        frequency = None
        try: frequency = canvas.data.shiftedFrequency
        except: frequency = canvas.data.properFrequency
        rightSideText(28,"  Window-Light:\n    %s THz" % \
                      utility.sciNotation(frequency),sidebar0)

    drawClosest()
    drawClosestArrow()
    drawCoords()
    drawSpeedometer()
    drawZooms()
    drawClocks()

    if canvas.data.relativityStats:
        drawRelativityStats()
        

#draws an arrow centered at sx,sy pointing in a direction given as an angle in
# radians
def drawArrow(sx,sy,rad,direction,color):
    xRad=rad*math.cos(direction)
    yRad=-1*rad*math.sin(direction) #flipped to account for
                                    # tKinter's inversion
    canvas.create_line(sx-xRad,sy-yRad, sx+xRad,sy+yRad, fill=color,arrow=LAST)

################################################################################

#draws a one-line title to the center of the screen
def drawHeader(headerText):
    sidebar0 = canvas.data.colors["sidebar0"]
    centerSpacing,gameTop = canvas.data.centerSpacing,canvas.data.gameTop

    canvas.create_text(canvas.data.canWidth/2,gameTop+centerSpacing,anchor=N,
                       text=headerText,font="dotum 32 bold",fill=sidebar0)
    
#draws multiple lines of text to the center of the screen -- often accompanied
# by a header
def drawBody(bodyText):
    sidebar0 = canvas.data.colors["sidebar0"]
    centerSpacing,gameTop = canvas.data.centerSpacing,canvas.data.gameTop

    canvas.create_text(canvas.data.canWidth/2,
                       gameTop+(spaces*centerSpacing),anchor=N,text=bodyText,
                       font="dotum 12",fill=sidebar0)

    #spaces = 4 #the non-header messages begin in the fourth center-space
    #for line in bodyText:
    #    canvas.create_text(canvas.data.canWidth/2,
    #                       gameTop+(spaces*centerSpacing),anchor=N,text=line,
    #                       font="dotum 12",fill=sidebar0)
    #    spaces+=1

################################################################################

#these functions draw a level's instructions, or part of them, to the center of
# the screen
def drawInstructions():
    #draw title
    top=canvas.data.gameTop+0.5*canvas.data.buttonSpacing
    buttonWidth=canvas.data.canWidth/4.0
    text=canvas.data.instructions[0]
    drawButton(top,buttonWidth,text)

    #draw body
    top=canvas.data.gameTop+1.5*canvas.data.buttonSpacing
    buttonWidth=canvas.data.canWidth/2.0
    text=canvas.data.instructions[canvas.data.instructionNumber]
    drawButton(top,buttonWidth,text)
    
################################################################################

def drawOutOfFuel():
    top,spacing,canWidth = \
            canvas.data.gameTop,canvas.data.buttonSpacing,canvas.data.canWidth

    drawButton(top+spacing,canWidth/4.0,"You're out of fuel!")
    drawButton(top+2*spacing,canWidth/4.0,"""I suggest you pause and restart,
mein Freund.""")

################################################################################

def drawPaused():
    drawSpace()
    drawShips()
    drawFrame()
    drawHUD()
    if canvas.data.explainControls:
        drawControlsPicture()
    elif canvas.data.instructionNumber>0:
        drawInstructions()
    else:
        drawPausedText()

def drawPausedText():
    top,spacing,canWidth = \
            canvas.data.gameTop,canvas.data.buttonSpacing,canvas.data.canWidth

    drawButton(top+spacing,canWidth/8.0,"Game Paused.")
    drawButton(top+2*spacing,canWidth/7.0,"""(Q)uit
(R)estart
View (c)ontrols
View (i)nstructions
Un(p)ause""")


################################################################################

#draw the picture of the controls
def drawControlsPicture():
    canWidth,gameTop,centerSpacing = \
            canvas.data.canWidth,canvas.data.gameTop,canvas.data.centerSpacing
    
    canvas.create_image(canWidth/2,gameTop+centerSpacing,anchor=N,
                        image=canvas.data.controlsImage)

################################################################################

def drawLevelFailed():
    drawSpace()
    drawFrame()
    drawHUD()
    if canvas.data.exploding: drawExplosion()
    drawLevelFailedText()
    
def drawLevelFailedText():
    top,spacing,canWidth = \
            canvas.data.gameTop,canvas.data.buttonSpacing,canvas.data.canWidth

    drawButton(top+spacing,canWidth/4.0,
               "You crashed, %s!" % canvas.data.currentPutDown)
    drawButton(top+2*spacing,canWidth/3.0,"Press 'r' to try again.")

def drawExplosion():
    expColor=canvas.data.colors["explosion"]
    radExp=canvas.data.radExplosion
    sx,sy=canvas.data.sxShip,canvas.data.syShip
    canvas.create_oval((sx-radExp,sy-radExp),(sx+radExp,sy+radExp),
                       fill=expColor)

################################################################################

def drawLevelWon():
    drawSpace()
    drawFrame()
    drawHUD()
    if not canvas.data.exploded: drawShips()
    if canvas.data.exploding: drawExplosion()
    drawLevelWonText()

def drawLevelWonText():
    top,spacing,canWidth = \
            canvas.data.gameTop,canvas.data.buttonSpacing,canvas.data.canWidth

    if canvas.data.newHighScore:
        drawButton(top+spacing,canWidth/4.0,
                   "A new high score? %s!" % canvas.data.currentCompliment)
    else:
        drawButton(top+spacing,canWidth/4.0,
                   "%s! Level Passed!" % canvas.data.currentCompliment)

    drawButton(top+2*spacing,canWidth/3.0,
             """Press enter to advance to the next level
or 'r' to replay this one.""")
    
################################################################################

def drawGameWon():
    drawFixedStars()
    drawFrame()
    drawGameWonText()

def drawGameWonText():
    top,spacing,canWidth = \
            canvas.data.gameTop,canvas.data.buttonSpacing,canvas.data.canWidth

    drawButton(top+spacing,canWidth/4.0,"You Won Doktor Einstein!")
    drawButton(top+2*spacing,canWidth/3.0,
"""Total Time:\n%f seconds
Press Enter to play again! Aufwiedersehen!""" % canvas.data.totalScore)

################################################################################

def drawControls():
    drawFixedStars()
    drawFrame()
    drawControlsPicture()
    drawControlsText()

def drawControlsText():
    top,spacing,canWidth = \
            canvas.data.gameTop,canvas.data.buttonSpacing,canvas.data.canWidth

    drawButton(top+6*spacing,canWidth/3.0,
               "Press Enter to return to the main menu.")

    
################################################################################
############################# keypress handlers ################################
################################################################################

#records the keypresses that occur during a timestep -- rather than action on
# these immediately, it sends the to processPresses to be acted on at the end
# of the timestep. it takes care to not add a press to a set if it is already
# in that set
def recordPresses(event):
    press=event.keysym
    
    #add holdable presses (w,a,s, and d, which correspond to engines)
    if press in canvas.data.movements\
       and press not in canvas.data.holdablePresses:
        canvas.data.holdablePresses.add(press)

    #add all other presses
    if press not in canvas.data.presses:
        canvas.data.presses.add(press)
        
#this will make sure that held keys stay in canvas.data.presses, while
# released keys are removed (idea from Raphael Segal)
def recordReleases(event):
    release=event.keysym
    canvas.data.holdablesReleased.add(release)

#works in conjunction with recordReleases -- because recordReleases happens
# throughout the timestep, while removePresses happens only after,
# all keyPresses will be acted on at least once
def removePresses():
    #remove all presses that should not be held (all that are not w,a,s,d)
    canvas.data.presses.clear()
    
    #remove holdable presses if they have been released
    for release in canvas.data.holdablesReleased:
        if release in canvas.data.holdablePresses:
            canvas.data.holdablePresses.remove(release)
    canvas.data.holdablesReleased.clear()

################################################################################

#acts on the keypresses recorded by recordPresses during the most recent
# timestep
def processPresses(state):
    allPresses = canvas.data.presses.union(canvas.data.holdablePresses)
    for press in allPresses:
        #print "keypress processed: ", press
        if(state=="startScreen"):
            processPressesStartScreen(press)
        elif(state=="active"):
            processPressesActive(press)
        elif(state=="paused"):
            processPressesPaused(press)
        elif(state=="levelFailed"):
            processPressesLevelFailed(press)
        elif(state=="levelWon"):
            processPressesLevelWon(press)
        elif(state=="gameWon"):
            processPressesGameWon(press)
        elif(state=="controls"):
            processPressesControls(press)
    removePresses()

def processPressesStartScreen(press):
    if press=="Return":
        buttonSelected()
    elif press=="Up":
        #select the next button up -- if at topmost button, go to bottom
        canvas.data.buttonSelection = (canvas.data.buttonSelection-1) % \
                                      len(canvas.data.startButtons)
    elif press=="Down":
        #select the next button down -- if at lowest button, go to top
        canvas.data.buttonSelection = (canvas.data.buttonSelection+1) % \
                                      len(canvas.data.startButtons)
def processPressesActive(press):
    if press in canvas.data.movements:
        thrusterOn(press)
    elif press in canvas.data.timeZooms:
        timeZoomToPerform(press)
    elif press in canvas.data.spaceZooms:
        spaceZoomToPerform(press)
    elif press=="p":
        pauseGame()
    elif press=="c":
        #toggle control explanations
        canvas.data.explainControls = not canvas.data.explainControls
        canvas.data.instructionNumber = 0 #the two can't coexist
        pauseGame()
    elif press=="i":
        #move through instructions
        canvas.data.instructionNumber = \
            (canvas.data.instructionNumber+1) % len(canvas.data.instructions)
        canvas.data.explainControls = False
        pauseGame()
    elif press=="q":
        #pause instead of quitting directly from "active"
        pauseGame()
    elif press=="r":
        #pause instead of restarting directly from "active"
        pauseGame()
    if press=="Return" and canvas.data.levelWonAlready:
        #on subsequent plays of the level, the user doesn't have to re-win
        nextLevel()
    elif press=="1":
        #toggle the high-score ghost
        canvas.data.ghost= not canvas.data.ghost
    elif press=="2":
        #toggle move arrow superimposed on the shp
        canvas.data.moveArrow = not canvas.data.moveArrow
    elif press=="3":
        #toggle relativity stats on the sidebar
        canvas.data.relativityStats = not canvas.data.relativityStats

    #cheat for presentation
    elif press =="Escape":
        nextLevel()

#music below:        
    #elif press=="4":
        #start/stop music
        #canvas.data.music = not canvas.data.music
        #updateMusic()
    #elif press=="5":
        #start song if no song, switch song if song playing
        #if not canvas.data.music: canvas.data.music=True
        #updateMusic()

def processPressesPaused(press):
    if press=="p" or press=="Return":
        unpauseGame()
    elif press=="q":
        #quit to main menu, but not if it's on an instructions screen
        if canvas.data.instructionNumber>0:
            canvas.data.instructionNumber=0
        else:
            initStartScreen()
    elif press=="r":
        #restart level, but not if it's on an instructions screen
        if canvas.data.instructionNumber>0:
            canvas.data.instructionNumber=0
        else:
            if not canvas.data.levelAlreadyAttempted and canvas.data.level>1:
                canvas.data.level -=1 #go back to the previous level
            initLevel()
    elif press in canvas.data.movements:
        pass #don't even turn on thrusters when the game is paused
    else:
        processPressesActive(press)

def processPressesLevelFailed(press):
    if press=="r":
        initLevel() #restart the level
    elif press=="p":
        pass #don't allow pausing from "levelFailed"
    elif (press in canvas.data.timeZooms) or (press in canvas.data.spaceZooms):
        processPressesActive(press) #still allow zooming

def processPressesLevelWon(press):
    if press=="r":
        initLevel()
    elif press not in {'c','i','p','q','1'}:
        processPressesActive(press) #still allow most funtions form "active"

def processPressesGameWon(press):
    if press=="Return":
        initStartScreen() #return to the main menu

def processPressesControls(press):
    if press=="Return":
        initStartScreen() #return to the main menu

################################################################################
########################### main function call #################################
################################################################################

playLightSpeed()

################################################################################
################################ comments ######################################
################################################################################

#put picture at startup
#make the game fill the screen
#the stars vibrate if you're going too fast??

#if you can't "move" fixed stars by zooming in, moving, then zooming make out,
# then you're fine

#make the title fancy!

#possibly change checkobjectives so that an object is orbiting if it actually
# would be orbiting by gravitational calculations

#you pass through planets if you're going to fast...maybe draw lines between
# timesteps to detect collisions?

# maybe fix so ghost is drawn after win??
"""Make instructions in tuples and allow moving between elements to make
    instructions less dense"""
""" dilate halo? """
""" background behind paused text? """ 
# make highscores based on more than just time
# display the zooming factor...maybe in sliding bars like osmos does?
# get rid of global canvas?

#allow player to change G and c in a sandbox mode

""" change fuel mass between levels """
""" make the sun muuuuuch further away """
