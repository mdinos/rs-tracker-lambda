# 839812, Marcus Wharton
# Python Assignment, December 2016

# Patchworks 1 and 2.
# valid colours are red, green, blue, orange, pink, brown
# valid sizes are 5, 7, 9

# get inputs, size and 3 colours
# are inputs valid
# if yes, proceed
# if no, ask again
# draw each patch in the required places

from graphics import *

def getInputs():
    haveValidColours = False
    while not haveValidColours:
        colours = input("Please enter 3 valid colours seperated by spaces: ")
        colours = colours.lower()
        if areColoursValid(colours) and areColoursDifferent(colours):
            haveValidColours = True
            
    while True:
        size = input("Please enter a valid size for the patchwork: ")
        if isSizeValid(size):
            size = int(size)
            break
        
    colours = [colours.split()[0], colours.split()[1], colours.split()[2]]
    return colours, size

def areColoursDifferent(colours):
    if colours.split()[0] != colours.split()[1] and colours.split()[0] != \
                           colours.split()[2] and colours.split()[1] != \
                           colours.split()[2]:
        return True
    else:
        print("Colours must be unique.")
        return False
        
def areColoursValid(colours):
    validColours = ['red', 'green', 'blue', 'orange', 'pink', 'brown']
    for i in range(3):
        colour = colours.split()[i]
        if colour not in validColours:
            print("Invalid colours!")
            return False
    else:
        return True

def isSizeValid(size):
    validSizes = ['5', '7', '9']
    if size in validSizes:
        return True
    else:
        print("Please enter a valid size, 5, 7 or 9.")
        return False

def drawPatchOne(x, y, colour, win):
    for j in range(3):
        for i in range(4):
            sail = Polygon(Point(x + (i * 25), y + 20 + (j * (100 / 3))),
                           Point(x + 12.5 + (i * 25), y + (j * (100 / 3))),
                           Point(x + 25 + (i * 25), y + 20 + (j * (100 / 3))))
            sail.draw(win)
            if j == 0 or j == 2:
                sail.setFill(colour)
        for i in range(4):
            mast = Line(Point(x + 12.5 + (25 * i), y + 20 + (j * (100 / 3))),
                        Point(x + 12.5 + (25 * i), y + 25 + (j * (100 / 3))))
            mast.draw(win)
        for i in range(4):
            hull = Polygon(Point(x + (i * 25), y + 25 + (j * (100 / 3))),
                           Point(x + 5 + (i * 25), y + 30 + (j * (100 / 3))),
                           Point(x + 20 + (i * 25), y + 30 + (j * (100 / 3))),
                           Point(x + 25 + (i * 25), y + 25 + (j * (100 / 3))))
            hull.draw(win)
            if j == 1:
                hull.setFill(colour)
                           
def drawPatchTwo(x, y, colour, win):
    for i in range(10):
        line = Line(Point(x + (i * 10), y), Point(x + 100, y + 10 + (i * 10)))
        line.setFill(colour)
        line.draw(win)

        line2 = Line(Point(x, y + (i * 10)), Point(x + 10 + (i * 10), y + 100))
        line2.setFill(colour)
        line2.draw(win)

def drawPatchwork(size, colours):
    win = GraphWin('Patchwork', size * 100, size * 100)
    # drawing all patch #1s
    for m in range(size):
        if m == 0 or m == (size - 1):
            colour = colours[0]
        else:
            colour = colours[2]
        drawPatchOne(m * 100, m * 100, colour, win)
    # drawing top and left hand patches
    for m in range(1, size):
        if m % 2 != 0:
            colour = colours[1]
        else:
            colour = colours[0]
        drawPatchTwo(m + (m * 100), 0, colour, win)
        drawPatchTwo(0, m + (m * 100), colour, win)
    # drawing bottom and right hand patches
    for m in range(1, size - 1):
        if m % 2 == 0:
            colour = colours[0]
        else:
            colour = colours[1]
        drawPatchTwo(m * 100, (size - 1) * 100, colour, win)
        drawPatchTwo((size - 1) * 100, m * 100, colour, win)
        # drawing central patches
        colour = colours[2]
        for n in range(1, size - 1):
            if n != m:
                drawPatchTwo(m * 100, n * 100, colour, win)

def main():
    colours, size = getInputs()
    drawPatchwork(size, colours)

main()
