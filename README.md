# MathsJam-Stuff
Resources used in MathsJam talks

## Fret2025
Fret2025 are a couple of resources used in a talk I did at the 2025 MathsJam UK event, describing the geometry of a fret rocker.
**Guitar Fret Calculator.xlsx** is a spreadsheet for calculating the fret spacing on a guitar. Additional columns and tables show the width between frets and calculates the size range for a fret rocker

**ConvexPoly.py** is a small graphical utility for drawing convex polygons with fixed side lengths. It requires the pygame libraries to be installed.
Define your lengths in the polyLine list, e.g.:

`polyLen=[70.7,67.0,63.4,60.1,57.0]`

You can also define the `lineWidth` by changing the variable value.

There are the following key funtions:
 * Cursor keys - pan screen
 * m - Merge two points. When one point is on top of another, it will change to be magenta. This action can not be undone.
 * s - Export as an OpenSCAD file to render for 3D printing
