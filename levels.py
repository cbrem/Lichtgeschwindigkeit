#levels.py

#for each level, "objects" is a dict containing the the object to be drawn; each
# object name is the key to a tuple containing:
# (x distance from earth, y distance from earth, radius, color);
# "objectives" is a set of the objects that the player must reach;
# "instructions" will be shown at the start of the level
def load(levelNumber):
    levels=dict()

    objects={"Earth":(0.0,0.0,60.0,"steel blue")}
    objectives=set(["Earth"])
    instructions=("Welcome to Lichtgeschwindigkeit!",
"""(That's 'light-speed' for you Americans.)
For the first level, try to fly to Earth using W, A, S, and D.
Press 'c' at any point to find out about more controls.
Press Enter to begin!""")
    levels[1]=(objects,objectives,instructions)

    objects={
            "Earth":(0.0,0.0,60.0,"steel blue"),
            "The Moon":(0.0,-100.0,10.0,"gray"),
            }
    objectives=set(["The Moon"])
    instructions=("The Heads-Up Display",
"""Wondering about the numbers on the sides of the screen?
Wonder no more!
On your left is a fuel gauge and the objectives for this level.
On your right is your position, speed, and a few other things.
(Keep in mind that these values are measured relative to Earth).
Now press Enter and try to get to the moon!""")
    levels[2]=(objects,objectives,instructions)


    objects={
            "Earth":(0.0,0.0,60.0,"steel blue"),
            "The Moon":(0.0,-100.0,10.0,"gray"),
            "Mars":(1000.0,1000.0,40.0,"red")
            }
    objectives=set(["Mars"])
    instructions=("Time For Some Physics",
"""Did you feel the Earth's gravitational pull?
You did? Prima! Let's move onto some cooler physics.

As you may or may not have guessed,
this game is largely about special relativity.
How so? Why don't you fly to Mars to find out!
Keep an eye on your ship's window?
(Hint: Try zooming out -- it's the red one.)""")
    levels[3]=(objects,objectives,instructions)
                
    objects={
            "Earth":(0.0,0.0,60.0,"steel blue"),
            "The Moon":(0.0,-100.0,10.0,"gray"),
            "Mars":(1000.0,1000.0,40.0,"red"),
            "Alpha Centauri A":(10000.0,0.0,500.0,"white"),
            "Alpha Centauri B":(10000.0,1000.0,400.0,"yellow"),
            "Proxima Centauri":(9000.0,-300.0,200.0,"red")
            }
    objectives=set(["Proxima Centauri"])
    instructions=("Finally, Some Relativity",
"""Did you see the window color change?
If you didn't, just press 'r' to play the level again.
If you did, wunderbar!
What you saw was the relativistic Doppler Effect.
Press 'i' to hear more.""",
"""In this game, though the camera is on the ship,
your relativistic point of view is that of an observer on Earth.
As the ship flies away from you, it emits light which,
from the ship's point of view, has a constant frequency.
However, the frequency of light that you receive changes
based on whether the ship is approaching or receeding from Earth.""",
"""You've probably heard that light always travels at the same speed.
In this game, that speed is set to 1000 m/s.
(This is less than the real value, but don't worry --
the same effects apply,only on a more visible scale!)""",
"""Anyway, since the ship's velocity relative to Earth can't be added
to the velocity of light (the light can't be "boosted" toward Earth
by the movement of the ship, because that would change its speed!),
the ship's movement instead changes the light's frequency.
That's why an observer on Earth sees the light change color.""",
"""When the ship is moving away from the Earth, light from it
decreases in frequency, moving toward (and possibly past) the
red edge of the visible spectrum. This phenomenon is therefore
called 'redshifting.' When the ship is approaching the Earth,
light from it increases in frequency toward the blue/violet edge
of the spectrum. This phenomenon is called 'blue shifting.'""",
"""Okay, that was a lot, but I hope you got it all.""",
"""Ready for more? Try flying to Proxima Centauri (the red star).
Try to go as fast as you can, and keep an eye on your ship's shape.
Press Enter to try it!""")
    levels[4]=(objects,objectives,instructions)

    objects={
            "Earth":(0.0,0.0,60.0,"steel blue"),
            "The Moon":(0.0,-100.0,10.0,"gray"),
            "Mars":(1000.0,1000.0,40.0,"red"),
            "Alpha Centauri A":(10000.0,0.0,500.0,"white"),
            "Alpha Centauri B":(10000.0,1000.0,400.0,"yellow"),
            "Proxima Centauri":(9000.0,-300.0,200.0,"red"),
            "Betelgeuse":(0.0,20000.0,1000.0,"orange")
            }
    objectives=set(["Betelgeuse"])
    instructions=("Doppler, Lorentz, Limits, Oh My!",
"""Did you see your ship's length decrease? Wasn't it cool?!
If you didn't see it, press 'r' to try again, and look harder!
Otherwise, press 'i' to hear about what that was!""",
"""That was Lorentz Contraction!
When you, a stationary observer, see an object go fast enough,
you will also see its length decrease. The entire object doesn't
shrink, but its dimension parallel to its direction of motion does.""",
"""In truth, Lorentz Contraction occurs at all speeds, but it only
becomes noticable by human observers at very high speeds.
The same is true for the other relativistic effects addressed here!""",
"""Okay, so you've made it to the last level in this brief tutorial.
Would you mind watching two things for me this time? Really? Danke!""",
"""This time, try to get to Betelgeuse.
But once you get there, don't just stop!
Keep flying, and try to go as fast as you can!
I bet you Pluto that your speed, which you can watch on the right,
will never go over the speed of light (1000 m/s)!""",
"""Also, keep an eye on the clocks in the bottom-right --
would you have guessed that going close to the speed of light
would cause the clock on the ship to slow down (according to an
observer watching form Earth?) Well it does! Now get to Betelgeuse!""")
    levels[5]=(objects,objectives,instructions)

    objects={
            "The Sun":(-2500,-100.0,300.0,"yellow"),
            "Mercury":(-500,50.0,20.0,"brown"),
            "Venus":(-300,-200.0,50.0,"orange"),
            "Earth":(0.0,0.0,60.0,"steel blue"),
            "The Moon":(0.0,-100.0,10.0,"gray"),
            "Mars":(1000.0,1000.0,40.0,"red"),
            "Alpha Centauri A":(10000.0,0.0,350.0,"white"),
            "Alpha Centauri B":(10000.0,1000.0,300.0,"yellow"),
            "Proxima Centauri":(9000.0,-300.0,150.0,"red"),
            "Betelgeuse":(0.0,20000.0,1000.0,"orange")
            }
    objectives=set(["Mercury","Venus","Earth","Mars","The Sun"])
    instructions=("Tour of the System",
                  "Visit all of the planets -- don't get pulled in by the Sun!",
"""Also, if you're feeling adventurous, try pressing
1 after a level-win to race the ghost of your best time!
Or press 3 to toggle information about relativistic constants!
Now get going, explore!""")
    levels[5]=(objects,objectives,instructions)

    objects={
            "The Sun":(-2500,-100.0,300.0,"yellow"),
            "Mercury":(-500,50.0,20.0,"brown"),
            "Venus":(-300,-200.0,50.0,"orange"),
            "Earth":(0.0,0.0,60.0,"steel blue"),
            "The Moon":(0.0,-100.0,10.0,"gray"),
            "Mars":(1000.0,1000.0,40.0,"red"),
            "Alpha Centauri A":(10000.0,0.0,350.0,"white"),
            "Alpha Centauri B":(10000.0,1000.0,300.0,"yellow"),
            "Proxima Centauri":(9000.0,-300.0,150.0,"red"),
            "Pandora":(12500.0,100.0,30.0,"blue"),
            "Other Earth":(12300.0,0.0,60.0,"green"),
            "Betelgeuse":(0.0,20000.0,1000.0,"orange"),
            "Barnard's Star":(-10000.0,10000.0,200.0,"red")
            }
    objectives=set(["Venus","Barnard's Star","Betelgeuse","Other Earth"])
    instructions=("Tour of the Galaxy!",
                  "There are so many stars to see -- see them all!")
    levels[7]=(objects,objectives,instructions)

    return levels.get(levelNumber)
