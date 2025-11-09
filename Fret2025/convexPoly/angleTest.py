#!/usr/bin/python

# angleTest.py - Early version of convex polygon. Defines the classes and other
# mechanisms used. Produced to check I was measuring angles correctly.

# Produce a convex polygon from a list of lengths, given in mm. It will scale
# to the screen size.
#
# Dave Hartburn May 2024

import pygame,math

# List of lengths
polyLen=[1,1,1,1]

screenFactor=0.9        # Window will be size of first desktop x this factor
# List of colours to display segments
COLS = [
(255,255,255),(0,255,0),(0,0,255),(255,255,0),(0,255,255),(192,192,192),
(128,128,128),(128,0,0),(128,128,0),(0,128,0),(128,0,128),(0,128,128),(0,0,128)
]
COL_CLICK=(128,128,128)
COL_A=(200,200,200)
COL_B=(200,200,50)
COL_C=(50,200,50)
BG = (0,0,0)
FPS = 100
pointRad=10         # Radius for all points


# #################### Classes #################################
class Point:
    # Defines a point with a coordinate, colour and label
    # Fixed is a boolean. If True, the point can not be moved when dragging a line
    def __init__(self, coord, fixed, colour, label):
        self.coord=coord
        self.fixed=fixed
        self.colour=colour
        self.label=label
        self.rad=pointRad
        print("New point created ", self.coord)

    def move(self, newcoord):
        if not self.fixed:
            self.coord=newcoord

    def draw(self, surface):
        # Draw the point on a surface
        pygame.draw.circle(surface, self.colour, self.coord, self.rad)

# End of class Point

class LineSegment:
    # Line segment joining two points A to B
    def __init__(self, A, B):
        self.A=A
        self.B=B
        self.angleR=0        # Holding values
        self.angleD=0        # R = radians, D = degrees
        self.length=0
        self.recalc()

    def recalc(self):
        # Recalculate both angle and length
        print("Hello, recalculating line")
        self.recalcAngle()
    
    def recalcAngle(self):
        # Calculate the angle described by the line A-B, relative to the positive x axis.
        # Return a tuple of radians, degrees
        xdiff=self.B.coord[0]-self.A.coord[0]
        ydiff=self.B.coord[1]-self.A.coord[1]
        if(xdiff==0):
            # Avoid division by zero
            xdiff=0.000001
        self.angleR=math.atan2(ydiff,xdiff)
        if(self.angleR<0):
            self.angleR=2*math.pi + self.angleR
        self.angleD=math.degrees(self.angleR)
        
    def getAngles(self):
        return (self.angleR, self.angleD)
    
    def draw(self, surface):
        pygame.draw.line(surface, COL_A, self.A.coord, self.B.coord, 1)

# End of class LineSegment



# Pygame overhead
pygame.init()
desksize=pygame.display.get_desktop_sizes()
WIDTH=int(desksize[0][0]*screenFactor)
HEIGHT=int(desksize[0][1]*screenFactor)
print(WIDTH,HEIGHT)
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Convex Polygon")
# Init fonts
pygame.font.init()
labelFont = pygame.font.Font('freesansbold.ttf',28)
clock = pygame.time.Clock()
mousePos = Point((0,0), False, (255,255,255),"Mouse")

pointA=None
pointB=None
lineA=None
lineB=None
mouseLine=None

# Work out scale. Fudge for now
scale=50

# ********* Functions ************

def drawScreen():
    # Update the display
    screen.fill(BG)
    #drawSegments()
    # What state of line drawing and measuring are we in?
    if(pointA==None):
        # No pointA, mouse pointer is a circle for A
        pygame.draw.circle(screen, COL_A, mousePos.coord, pointRad)
    elif(pointA!=None and pointB==None):
        # Only a point A, rubber band to mouse pointer
        #pygame.draw.circle(screen, pointA.colour, pointA.coord, pointRad)
        pointA.draw(screen)
        # Mouse pointer is a circle to B
        pygame.draw.circle(screen, COL_B, mousePos.coord, pointRad)
        # Draw line to mouse
        mouseLine.draw(screen)
        # Add label
        txt="{:.2f}°".format(mouseLine.angleD)
        angLab = labelFont.render(txt, 1, (0,0,255))
        screen.blit(angLab,(mousePos.coord[0]+30, mousePos.coord[1]+30))
    elif(pointA!=None and pointB!=None):
        # Draw lines
        lineA.draw(screen)
        # Draw points
        pointA.draw(screen)
        pointB.draw(screen)
        # Point under mouse pointer
        pygame.draw.circle(screen, COL_C, mousePos.coord, pointRad)
        # Draw line to mouse
        mouseLine.draw(screen)
        # Add label
        lineAngles=angleBetweenLines(lineA, mouseLine, True)
        txt="{:.2f}°".format(lineAngles[1])
        angLab = labelFont.render(txt, 1, (0,0,255))
        screen.blit(angLab,(mousePos.coord[0]+30, mousePos.coord[1]+30))

    pygame.display.flip()
# End of draw screen

def calcLineAngle(A, B):
    # Calculate the angle described by the line A-B, relative to the positive x axis.
    # Return a tuple of radians, degrees
    xdiff=A[0]-B[0]
    ydiff=A[1]-B[1]
    if(xdiff==0):
        # Avoid division by zero
        xdiff=0.000001
    angR=math.atan2(ydiff,xdiff)
    if(angR<0):
        angR=2*math.pi + angR
    ang=math.degrees(angR)
    return (angR, ang)
# End of calcLineAngle

def angleBetweenLines(A, B, smallest):
    # Reports the angle between two lines as a tuple, (radians, degrees)
    # If 'smallest' is false, it will report the clockwise angle. If it is true,
    # it will report the smallest angle between the two. I.e. 330 degrees or 30 degrees
    angA=A.getAngles()
    angB=B.getAngles()
    diff=(angB[0]-angA[0], angB[1]-angA[1])
    if smallest == False:
        rtn=diff
    else:
        if diff[1]>180:
            diff=(2*math.pi-diff[0], 360-diff[1])
        elif diff[1]<0:
            diff=(-1*diff[0], -1*diff[1])
        rtn=diff
    return rtn

def drawSegments():
    screen.fill(BG)
    #print(coords)
    # Draw each segment
    numCoords=len(coords)
    startCoord=coords[0]
    lastCoord=coords[0]
    for i in range(1,numCoords):
        #print(i)
        pygame.draw.line(screen, (255,255,255), lastCoord, coords[i],3)
        lastCoord=coords[i]
    #drawStar()
    
# End of drawSegments

def drawStar():
    # Temporary function while I work out my angle definitions - where is the zero angle, where is 45 etc?
    # Define origin
    origin=(WIDTH/2,HEIGHT/2)   # Middle of the screen
    l = 300     # Length of line
    for i in range(0,360,15):
        #print(i)
        x=origin[0]+math.cos(math.radians(i))*l
        y=origin[1]+math.sin(math.radians(i))*l
        pygame.draw.line(screen,(0,255,0),origin,(x,y),3)
        angLab = labelFont.render(str(i), 1, (0,0,255))
        screen.blit(angLab,(x,y))

# End of draw star
    


def trianglePoint(A, B, l, i):
    # Calculates the third point of a triangle which is of line length l from point B at an angle of i to the line AB

    # Calculate angle of AB to the X axis
    xdiff=B[0]-A[0]
    ydiff=B[1]-A[1]
    print("Point diff=",xdiff,ydiff)
    ABangR=math.atan(ydiff/xdiff)       # Angle in radians
    ABangD=math.degrees(ABangR)         # Angle in degrees
    print("Angle=",ABangD)
    CangD=ABangD+i
    print("C angle = ", CangD)
    Cx=B[0]+l*math.cos(math.radians(CangD))
    Cy=B[1]+l*math.sin(math.radians(CangD))
    return(Cx,Cy)
# End of trianglePoint

def handleClick(event):
    # Deal with mouse clicks, called on button 
    global pointA, pointB, mouseLine, lineA
    print(event)
    if(event.button==1):
        # Left button clicked
        if(pointA==None): # Set point A
            pointA=Point(event.pos, False, COL_A, "A")
            # Set line between A and mouse pointer
            mouseLine=LineSegment(pointA, mousePos)
        else:
            print("Setting point B")
            # Setting point B
            pointB=Point(event.pos, False, COL_B, "B")
            lineA=LineSegment(pointB, pointA)   # We flip the line direction B to A, rather
                # than A to mouse, as we are making a triangle A, B, mouse.
            mouseLine=LineSegment(pointB, mousePos)
    elif(event.button==3):
        # Right button clicked, reset both points
        pointA=None
        pointB=None
        lineA=None
# End of handleClick

def mouseMove(event):
    # Update the mouse position tracker
    global mousePos
    mousePos.move(event.pos)
    if mouseLine != None:
        mouseLine.recalcAngle()


# ********* End of functions *****

# Calculate point coordinates
coords=[]
# First segment is horizontal line along the top of the screen
bottomMarg=20
scaledLength=polyLen[0]*scale
coordA=((WIDTH-scaledLength)/2,bottomMarg)
#coords.append(coordA)
#coords.append((coordA[0]+scaledLength, bottomMarg))

# Triangle test
# A to B is a line at 30 degrees to the virtical (clockwise) and 300 pixels long
coordA=(300,150)
coordB=(500,100)
coords.append(coordA)
coords.append(coordB)
# Calculate C, line of length 150 at an angle of 70 degrees to the line A-B
coordC=trianglePoint(coordA,coordB,200,30)
print(coordC)
coords.append(coordC)




# Main loop
# No interactive functionality, just keep it on screen until quit
drawScreen()
running = True
while running:
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        running = False
    elif event.type == pygame.MOUSEBUTTONDOWN:
        handleClick(event)
    elif event.type == pygame.MOUSEMOTION:
        mouseMove(event)
    #else:
    #    print(event)

    drawScreen()
    clock.tick(FPS)
pygame.quit()