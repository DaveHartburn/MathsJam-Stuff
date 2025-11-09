#!/usr/bin/python

# Produce a convex polygon from a list of lengths, given in mm. It will scale
# to the screen size.
#
# Dave Hartburn May 2024

import pygame,math

# List of lengths
#polyLen=[72,45,30]
polyLen=[70.7,67.0,63.4,60.1,57.0,54.0,51.2,48.5,46.0,43.7,41.5,39.3,37.4,35.5,33.7,32.1,30.5,29.0,27.6]

autoSolve=0      # 0 - Plot points in a line
                 # 1 - Auto-drag last point to first. May result in concave shape
                 # 2 - Try to solve by algorithm

screenFactor=0.9        # Window will be size of first desktop x this factor
# List of colours to display segments
COLS = [
(255,255,255),(0,255,0),(0,0,255),(255,255,0),(0,255,255),(192,192,192),
(128,128,128),(128,0,0),(128,128,0),(0,128,0),(128,0,128),(0,128,128),(0,0,128)
]
pointCol=(200,200,200)
selectedCol=(200,0,0)
BG = (0,0,0)
FPS = 100
pointRad=10         # Radius for all points
marg=50             # Margin from origin, for initial point placement
panStep=5           # How much to pan the screen by with cursor keys
lineWidth=5         # How wide to draw lines

# Lists of points and lines
points=[]
lines=[]

activePoint = None
dragPoint = None    # Point which we are dragging the active point over

# #################### Classes #################################
class Point:
    # Defines a point with a coordinate, colour and label
    # Fixed is a boolean. If True, the point can not be moved when dragging a line
    def __init__(self, coord, colour=(255,255,255), label="", fixed=False):
        self.coord=coord
        self.fixed=fixed
        self.colour=colour
        self.label=label
        self.rad=pointRad
        self.lines=[]       # A list of lines connected to this point
        self.rect=None
        self.locked=False
        self.dragOver=False      # Flag if we are currently dragging the mouse over

        #print("New point created ", self.coord)

    def move(self, newcoord):
        if not self.fixed and not self.locked:
            self.coord=newcoord
            # Mark this point as locked - it has moved. If we recurse through a loop
            # we dont want the other points to pull this one
            self.locked=True
            # Do any attached lines have fixed line lengths?
            for l in self.lines:
                if l.fixLength:
                    # This line should not shrink. Find the other point
                    op=l.otherPoint(self)
                    # Only move if it is not locked
                    if op.locked == False:
                        # Work out new coordinate. Find the direct angle to the other point
                        # and pull/push it to the correct length along that line
                        xdiff=op.coord[0]-self.coord[0]
                        ydiff=op.coord[1]-self.coord[1]
                        # Avoid division by zero
                        if xdiff==0:
                            xdiff=0.000001
                        ang=math.atan2(ydiff, xdiff)
                        #print(math.degrees(ang))
                        # Calculate new x and y offsets
                        xo=l.length*math.cos(ang)
                        yo=l.length*math.sin(ang)
                        # Move other point relative to self
                        op.move((self.coord[0]+xo, self.coord[1]+yo))


            # Done, unlock point
            self.locked=False
    # End of move

    def forceMove(self,xoff,yoff):
        # Forces a move of the point, ignoring all other restraints such as line length
        # Moves my offset. Should only be used by pan function for a global move
        nc=(self.coord[0]+xoff, self.coord[1]+yoff)
        self.coord=nc

    def draw(self, surface):
        # Draw the point on a surface
        self.rect=pygame.draw.circle(surface, self.colour, self.coord, self.rad)
        # Are we being dragged over?
        if self.dragOver:
            pygame.draw.circle(surface, (255,0,255), self.coord, self.rad*2, 1)

    def addLine(self,line):
        self.lines.append(line)

    def clicked(self, event):
        if self.rect.collidepoint(event.pos):
            return True
        else:
            return False

    def setColour(self, col):
        self.colour=col

    def whatLines(self):
        # Debugging function, lists lines connected to this point
        i=0
        for l in self.lines:
            print("Line {}, length {}, fixLength {}".format(i,l.length, l.fixLength))
            i+=1
# End of class Point

class LineSegment:
    # Line segment joining two points A to B
    def __init__(self, A, B, colour=(0,255,0), fixLength=False, w=1):
        self.A=A
        self.B=B
        self.colour=colour
        self.fixLength=fixLength    # If true, the line can not be stretched
        self.width=w
        self.angleR=0        # Holding values
        self.angleD=0        # R = radians, D = degrees
        self.length=0
        self.recalc()
        self.origLength=self.length

        # Register self with the two points
        A.addLine(self)
        B.addLine(self)

    def recalc(self):
        # Recalculate both angle and length
        xdiff=self.B.coord[0]-self.A.coord[0]
        ydiff=self.B.coord[1]-self.A.coord[1]

        # Calculate the angle described by the line A-B, relative to the positive x axis.
        if(xdiff==0):
            # Avoid division by zero
            xdiff=0.000001
        self.angleR=math.atan2(ydiff,xdiff)
        if(self.angleR<0):
            self.angleR=2*math.pi + self.angleR
        self.angleD=math.degrees(self.angleR)

        # Calculate length
        self.length=math.sqrt(xdiff*xdiff+ydiff*ydiff)
        #print("Length=", self.length)
    # End of recalc

    def getAngles(self):
        # Return a tuple of radians, degrees
        return (self.angleR, self.angleD)

    def draw(self, surface):
        pygame.draw.line(surface, self.colour, self.A.coord, self.B.coord, self.width)

    def otherPoint(self, p):
        # When we are dragging the end of a line, what is the other point to p?
        if self.A==p:
            return self.B
        else:
            return self.A

    def replacePoint(self, P, N):
        # Replace point P with point N
        if self.A == P:
            self.A=N
        elif self.B == P:
            self.B=N
# End of class LineSegment



# Pygame overhead
pygame.init()
desksize=pygame.display.get_desktop_sizes()
WIDTH=int(desksize[0][0]*screenFactor)
HEIGHT=int(desksize[0][1]*screenFactor)
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Convex Polygon")
# Init fonts
pygame.font.init()
labelFont = pygame.font.Font('freesansbold.ttf',28)
clock = pygame.time.Clock()

# Work out scale. The longest length should fill 80% of the screen
if(WIDTH<HEIGHT):
    minScreen=WIDTH
else:
    minScreen=HEIGHT
maxLength=0
tLen=0      # Total length
for l in polyLen:
    tLen+=l
    if l>maxLength:
        maxLength=l
print("Longest length is ", maxLength)
scale=(minScreen*0.8)/maxLength
print("80% scale method is scale of ", scale)
# Assume a circle
d=tLen/math.pi
scale=(minScreen*0.8)/d
print("Scale based on circumferance is ", scale)
# ********* Functions ************

def drawScreen():
    # Update the display
    screen.fill(BG)

    for l in lines:
        l.draw(screen)

    for p in points:
        p.draw(screen)

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

def plotConvexPolt():
    global points

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


def mergePoints(A, B):
    # Replace point B with point A
    if A == None or B == None:
        return
    #print("Merging points")
    for l in B.lines:
        #print("  Found a line")
        l.replacePoint(B, A)
        A.lines.append(l)
    # Destroy old point
    points.remove(B)

def pan(keys):
    # Pan the screen, move all the points
    global points
    x=0
    y=0
    if keys[pygame.K_UP]:
        y=-panStep
    if keys[pygame.K_DOWN]:
        y=panStep
    if keys[pygame.K_LEFT]:
        x=-panStep
    if keys[pygame.K_RIGHT]:
        x=panStep
    for p in points:
        p.forceMove(x,y)

def openSCADexport():
    print("Copy this into an openSCAD model. If you have not joined up your line to make a polygon, this will get messy!")
    polyStr="polygon( points = ["
    pcount=1
    #pathStr="paths [ ["
    for p in points:
        x=int(p.coord[0]/scale)
        y=int(p.coord[1]/scale)
        if pcount>1:
            polyStr+=", [{},{}]".format(x,y)
            #pathStr+=",p{}".format(pcount)
        else:
            polyStr+="[{},{}]".format(x,y)
            #pathStr+="p{}".format(pcount)

        pcount+=1

    print("linear_extrude(3) {",polyStr, "]);}")

def debugFunction():
    # Ad-hoc debugging function
    print("*** Debug ****")
    i=0
    for i in range(len(lines)):
        print("  Line {}, length {}".format(i, lines[i].length))
        if lines[i].fixLength:
            print("    This line is fixed")
    print("*** End of Debug ***")
# ********* End of functions *****

# Structures set up
x=marg
y=marg

# Point placement
if autoSolve==2:
    # Attempt to solve with algorithm
    np=len(polyLen)
    if np<3:
        print("You need at least 3 shapes to plot a shape")
        autoSolve=0
    elif np==3:
        # Does this form a valid triangle?
        longest=0
        sum=0
        for l in polyLen:
            sum+=l
            if l>longest:
                longest=l
        if (sum-longest)<longest:
            print("This is not a valid triangle")
            autoSolve=0
    # Handled errors, continue or drop through
    if autoSolve==2:
        plotConvexPoly()

if autoSolve<2:
    # Plot in a line
    # Place point at origin
    p=Point((x,y), colour=pointCol)
    points.append(p)
    lastPoint=p
    c=0     # Track colours

    for i in range(len(polyLen)):
        # Work out position for next point

        x=x+polyLen[i]*scale

        # Create new point
        p=Point((x,y), colour=pointCol)
        points.append(p)
        # Draw point between this and last, if present
        if lastPoint != None:
            l=LineSegment(lastPoint, p, colour=COLS[c], fixLength=True, w=lineWidth)
            lines.append(l)
            c+=1
            if c>len(COLS)-1:
                c=0
        lastPoint=p

    # "Cheat" way to solve. Just move last point to first point, merge and see what happens
    if autoSolve==1:
        # Last point is still set from above
        # This doesn't work well placing the last on the first with them all on a line
        # move it to the lower middle of the screen
        lastPoint.move((WIDTH/2, HEIGHT*0.6))
        # If we move it directly to where the first point is, the first point is likely to move
        # We need to loop
        while points[0].coord!=lastPoint.coord:
            lastPoint.move(points[0].coord)
        mergePoints(lastPoint, points[0])
# End of if autosolve 0,1




# Main loop
# No interactive functionality, just keep it on screen until quit
drawScreen()
running = True
while running:
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        running = False
    elif event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            # Left click
            for p in points:
                if p.clicked(event):
                    activePoint=p
                    p.setColour(selectedCol)
                    #p.whatLines()
    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1 and activePoint!=None:
            activePoint.setColour(pointCol)
            activePoint=None
    elif event.type == pygame.MOUSEMOTION:
        # We are dragging if there is an active point
        if activePoint != None:
            activePoint.move(event.pos)
            # Are we over another point?
            dragPoint = None
            for p in points:
                # Icnore active point
                if p != activePoint:
                    if p.rect.collidepoint(event.pos):
                        p.dragOver=True
                        dragPoint=p
                    else:
                        p.dragOver=False
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
            running=False
        elif event.key == pygame.K_m:
           # Merge points
           mergePoints(activePoint, dragPoint)
        elif event.key == pygame.K_d:
            # Debug
            debugFunction()
        elif event.key == pygame.K_s:
            openSCADexport()
    #else:
    #    print(event)
    # Are cursor keys held down?
    keys=pygame.key.get_pressed()
    pan(keys)

    drawScreen()
    clock.tick(FPS)
pygame.quit()
