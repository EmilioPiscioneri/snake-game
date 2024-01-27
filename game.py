thisFolder = "/python-programming/snake game/"
import pygame # pygame renderer for 2D
import math
import numpy # for tuple math
# Create direction emnum
enum = enumerate # make enum enumerate which is the same thing
class direction(enum): 
    up = 1
    down = 2
    left = 3
    right = 4
    none = 5
# make controls enum
class controls(enum):
    WASD = 1
    arrowKeys = 2

pygame.init()
screenSize = 720 # will be two sets of screen size, a square
screen = pygame.display.set_mode((screenSize, screenSize)) # screen is a surface
clock = pygame.time.Clock()
running = True



# Mainly used as player controller. Handles all stuuff to do with snake
class snake():
    length = 1 # start as length 1
    directions = [direction.none] #each direction of the length
    # must be called each frame, displays the character
    def render(self):
        # second number is the stop
        for lengthIndex in range(0, self.length):
            # Don't use match/case  because it is not supported below python 3.10
            directionForThisIndex = self.directions[lengthIndex] # Get the direction applied to last length
            #go through the direcions
            if(directionForThisIndex == direction.up): # moved up
                pass
            elif(directionForThisIndex == direction.down): # moved down
                pass
            elif(directionForThisIndex == direction.right): # moved right
                pass
            elif(directionForThisIndex == direction.left): # moved left
                pass
            elif(directionForThisIndex == direction.none): #starting move
                pass

# Divide map into invisible grid. Each segment of grid is a tile.
# Has its own coordinate system. E.g. (1,2) will be second tile on x and third tile on y start from bottom-left. Only positive values go from 0,tiles negtaive goes -1,-tleSize -1
# on x and y axis.
class grid():

    errorOnCreation = False
    tileSize: int = 0 # An int. Tile size of x and y for each tile should be square

    #when grid gets intiated. -> [type] is the return. : [type] gives a hint of parameter type
    def __init__(self, tileSize: int) -> None:
        #type check
        if (type(tileSize) != int):
            print("ERROR: tile size is not an int")
            self.errorOnCreation = True
            return None
        
        self.tileSize = tileSize # Set the tile size.

    # returns tile coordinates which real coordihnates are in. Must be a tuple
    def realToTileCoords(self, realCoords : tuple) -> tuple:
        #type check
        if (type(realCoords) != tuple):
            raise Exception("ERROR: realCoords is not a tuple")
        
        # // is floor divison. This means the result pf the division is rounded down to nearest whole number always.
        # do floor for positive numbers and ceil for negative 
        # do tilesize + 1 becuase it needs to from -1 to -tileSize -1

        tileCoords : tuple = (0,0) # default to 0,0

        if realCoords[0] < 0: # x negative
            tileCoords = (math.ceil(realCoords[0] / (tileSize+1)), realCoords[1])
        if realCoords[0] > 0: # x positive
            tileCoords = (realCoords[0] // tileSize, realCoords[1])

        if realCoords[1] < 0: # y negative
            tileCoords = (tileCoords[0], math.ceil(realCoords[1] / (tileSize+1)))
        elif realCoords[1] > 0: # y positive
            tileCoords = (tileCoords[0], realCoords[1] // tileSize)


        return tileCoords

    # Returns tile coords converted to real
    def tileCoordsToReal(self, tileCoord : tuple) ->tuple:
        realCoord = numpy.multiply(tileCoord, tileSize)

        return realCoord
        



tileSize = 10
gameMap = grid(tileSize)

if (gameMap.errorOnCreation):
    print("!! There was an error creating the map !!")
tileCoords = gameMap.realToTileCoords((15,15))
print(tileCoords)
realCoords = (gameMap.tileCoordsToReal(tileCoords))
print(realCoords)
playerSnake = snake()
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("Got quit event")
            running = False

    # fill screen with dark grey
    screen.fill((40,44,49))
    
    playerSnake.render()

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(75)  # limits FPS 

print("closing")
pygame.quit()