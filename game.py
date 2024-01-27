thisFolder = "/python-programming/snake game/"
import pygame # pygame renderer for 2D
import math
import numpy # for tuple math
import time

def getCurrentMillisecondTime():
    return round(time.time() * 1000)


# Create direction emnum
class direction(): 
    up = 1
    down = 2
    left = 3
    right = 4
    none = 5

    # Returns an int
    @staticmethod
    def getOppositeDirection(inputDirecion : int) -> int:
        if(type(inputDirecion) != int):
            raise Exception("ERROR: invalid arg direction, not an int")
        
        if(inputDirecion == direction.up):
            return direction.down
        elif(inputDirecion == direction.down):
            return direction.up
        elif(inputDirecion == direction.left):
            return direction.right
        elif(inputDirecion == direction.right):
            return direction.left
        
    # Returns a string
    @staticmethod
    def directionToString(inputDirecion : int) -> str:
        if(type(inputDirecion) != int):
            raise Exception("ERROR: invalid arg direction, not an int")
        if(inputDirecion == direction.up):
            return "up"
        elif(inputDirecion == direction.down):
            return "down"
        elif(inputDirecion == direction.left):
            return "left"
        elif(inputDirecion == direction.right):
            return "right"

# make controls enum
class controls():
    WASD = 1
    arrowKeys = 2

pygame.init()
screenSize = 720 # will be two sets of screen size, a square
screen = pygame.display.set_mode((screenSize, screenSize)) # screen is a surface
clock = pygame.time.Clock()
running = True
moveKeyDelay = 200 # How many milliseconds betwen each move
moveSnakeDelay = 100 # how many milliseconds between each snake move

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
        
        self.tileSize = tileSize # Set the til size.

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
           tileCoords = (math.ceil(realCoords[0] / (tileSize)), realCoords[1])
       if realCoords[0] > 0: # x positive
           tileCoords = (realCoords[0] // tileSize, realCoords[1])
       if realCoords[1] < 0: # y negative
           tileCoords = (tileCoords[0], math.ceil(realCoords[1] / (tileSize)))
       elif realCoords[1] > 0: # y positive
           tileCoords = (tileCoords[0], realCoords[1] // tileSize)

       return tileCoords

    # Returns tile coords converted to real
    def tileCoordsToReal(self, tileCoord : tuple) ->tuple:
       if (type(tileCoord) != tuple):
           raise Exception("ERROR: tileCoord is not a tuple")
       
       realCoord : tuple = (0,0) # initiate

       if(tileCoord[0] < 0): # x negative
           realCoord = (tileCoord[0] * 10, realCoord[1])
       elif(tileCoord[0] > 0): # x positive
           realCoord = (tileCoord[0] * 10 - 1, tileCoord[1])
			 
       if(tileCoord[1] < 0): # y negative
           realCoord = (realCoord[0],tileCoord[1] * 10)
       elif(tileCoord[1] > 0): # y positive
           realCoord =  (realCoord[0], tileCoord[1] * 10 - 1)

       return realCoord
        
# Mainly used as player controller. Handles all stuuff to do with snake
class snake():
    length = 1 # start as length 1
    directions = [direction.up] # each applied direction to next move
    currentDirection : int = direction.up # the current direction of snake, as int. Default to up
    colour = (116, 149, 189)
    screen : pygame.surface = None # initalise
    gameMap = None # initialise
    firstSnakeRectTilePos : tuple = (0,0) # initalise. This in real coords it is the first, snake tile, position
    updatedPosition : bool = False # default to false, whenever you update snake position set to true

    # constrcutor must have screen and grid arg
    def __init__(self,screen : pygame.surface, gameMap : grid ) -> None:
        self.lastSnakeRectTilePos = (screenSize/2, screenSize/2)
        self.firstSnakeRectTilePos = self.lastSnakeRectTilePos
        self.screen = screen
        self.gameMap = gameMap

    # must be called each frame, displays the character. pass in screen and size of each tile in real pixels. 
    def renderSnake(self, screen: pygame.surface.Surface, tileSize : int) -> None:
        # print("rendering")
        # pygame.draw.rect(screen, self.colour, pygame.Rect(0,0,100,100))
        # type check
        if (type(screen) != pygame.surface.Surface):
            raise Exception("ERROR: didn't pass a valid screen arg")
        if (type(tileSize) != int):
            raise Exception("ERROR: didn't pass a valid tileSize arg")
        lastDirection = direction.none # initiate var
        lastSnakeRectTilePos = self.firstSnakeRectTilePos
        firstSnakeRectTilePosition = None # initiate var
        # second number is the stop exclusive
        for lengthIndex in range(0,len(self.directions)):
            if(lengthIndex == 0):
                firstSnakeRectTilePosition = lastSnakeRectTilePos
            
            # Don't use match/case  because it is not supported below python 3.10
            directionForThisIndex = self.directions[lengthIndex] # Get the direction applied to last length
            #go through the direcions
            rectPosition = None # initliase
            
            #print(lastSnakeRectTilePos)
            
            if(directionForThisIndex == direction.up or lastDirection == direction.up): # moved up
                rectPosition = (lastSnakeRectTilePos[0], lastSnakeRectTilePos[1] - tileSize)
            elif(directionForThisIndex == direction.down or lastDirection == direction.down): # moved down
                rectPosition = (lastSnakeRectTilePos[0], lastSnakeRectTilePos[1] + tileSize)
            elif(directionForThisIndex == direction.right or lastDirection == direction.right): # moved right
                rectPosition = (lastSnakeRectTilePos[0] + tileSize, lastSnakeRectTilePos[1])
            elif(directionForThisIndex == direction.left or lastDirection == direction.left): # moved left
                rectPosition = (lastSnakeRectTilePos[0] - tileSize, lastSnakeRectTilePos[1])

            #rectPosition = (rectPosition[0], -1 * rectPosition[1])

            # print("Snake index: "+str(lengthIndex)+" with position ("+str(rectPosition[0])+","+str(rectPosition[1])+")")
            snakeRect = pygame.Rect(rectPosition[0], rectPosition[1], tileSize, tileSize)

            # print("drawing a rect")
            pygame.draw.rect(screen, self.colour, snakeRect)

            # at end of the loop, setup next iteration
            lastDirection = directionForThisIndex
            lastSnakeRectTilePos = rectPosition # setup position
            # setup next move
            if(lengthIndex == len(self.directions) - 1 and self.updatedPosition == True):
                self.firstSnakeRectTilePos = firstSnakeRectTilePosition
                self.updatedPosition = False

        
    lastDirectionChangeTime = 0 # in millis
    # changes snake direction
    def changeDirection(self, moveDirection : int) -> None:
        # Check if enough time has passed
        currentTimeInMilliseconds = getCurrentMillisecondTime()
        timeDifferenceInMillis = currentTimeInMilliseconds - self.lastDirectionChangeTime # time diifference netween current and last move in milliseconds
        if((timeDifferenceInMillis <= moveKeyDelay) or (self.lastDirectionChangeTime > 0 and timeDifferenceInMillis <= moveKeyDelay)):
            print("WARN: not enough time has passed between snake movements, skipping. Time difference is " + str(timeDifferenceInMillis)+" and delay is "+ str(moveKeyDelay))
            # now assign last move time to new move time
            self.lastDirectionChangeTime = currentTimeInMilliseconds
            return
        # now assign last move time to new move time
        self.lastDirectionChangeTime = currentTimeInMilliseconds
    
        # type check
        if(type(moveDirection) != int):
            raise Exception("ERROR: Didn't pass in an int")

        # check for going back in opposite directopm
        if(direction.getOppositeDirection(self.currentDirection) != moveDirection and self.currentDirection != moveDirection):
            # move snake
            # print(direction.directionToString(direction.getOppositeDirection(self.currentDirection)))
            # print(direction.directionToString(moveDirection))
            self.currentDirection = moveDirection
        else:    
            print("WARN: Tried to go in opposite direction with snake or same direction allready going")
            pass
        
        
        """
        firstSnakeTilePosition = self.firstSnakeRectTilePos
        # Move Snake
        if(moveDirection == direction.up): # moved up
            self.firstSnakeRectTilePos = (firstSnakeTilePosition[0], firstSnakeTilePosition[1]-tileSize)
        elif(moveDirection == direction.down): # moved down
            self.firstSnakeRectTilePos = (firstSnakeTilePosition[0], firstSnakeTilePosition[1]+tileSize)
        elif(moveDirection == direction.left): # moved left
            self.firstSnakeRectTilePos = (firstSnakeTilePosition[0]-tileSize, firstSnakeTilePosition[1])
        elif(moveDirection == direction.right): # moved right
            self.firstSnakeRectTilePos = (firstSnakeTilePosition[0]+tileSize, firstSnakeTilePosition[1])
        """
        return
    
    lastMoveTime = 0 # in millis

    # moves the snake in the direction it is currently facing. Intended to be called each frame. Not dependent on frames. Render arg is optional, will render after moving if time limit doesn'tt exceed 
    # returns True if success
    def updateSnake(self) -> bool:#, render = True, screen : pygame.surface = None, tileSize : int = None):
        # Check if enough time has passed
        currentTimeInMilliseconds = getCurrentMillisecondTime()
        timeDifferenceInMillis = currentTimeInMilliseconds - self.lastMoveTime # time diifference netween current and last move in milliseconds
        if((timeDifferenceInMillis <= moveSnakeDelay) or (self.lastMoveTime > 0 and timeDifferenceInMillis <= moveSnakeDelay)):
            # print("WARN: not enough time has passed between snake movements, skipping. Time difference is " + str(timeDifferenceInMillis)+" and delay is "+ str(moveSnakeDelay))
            # Didn't move, don't assign
            # self.lastMoveTime = currentTimeInMilliseconds
            return
        # now assign last move time to new move time
        self.lastMoveTime = currentTimeInMilliseconds

        # the direction the snake is facing
        currentDirection = self.currentDirection

        self.directions.append(currentDirection) # append is only slightly slower
        self.updatedPosition = True

        """
        if (render == True):
            if (type(screen) != pygame.surface.Surface):
                print(type(screen))
                raise Exception("ERROR: didn't pass a valid screen arg")
            if (type(tileSize) != int):
                raise Exception("ERROR: didn't pass a valid tileSize arg")
            self.render(screen, tileSize)
        """

        return True





tileSize = 10
gameMap = grid(tileSize)

if (gameMap.errorOnCreation):
    print("!! There was an error creating the map !!")

inpCoords = (30,19) # input coordinates
print("input coords: (" + str(inpCoords[0]) + ", " + str(inpCoords[1]) +")")
tileCoords = gameMap.realToTileCoords(inpCoords)
print(tileCoords)
realCoords = (gameMap.tileCoordsToReal(tileCoords))
print(realCoords)
playerSnake = snake(screen, gameMap)

gameControls = controls.WASD

def handlePlayerMovement(moveDirection : int):
    print("Moving in direction " + direction.directionToString(moveDirection))
    playerSnake.changeDirection(moveDirection) # type checking is done in function

# Handle key down, pass in the pressed key event as input. Is oj
def hanldKeysDown(event: pygame.event) -> None:
    print("Called key down function") # Is only called once regardless of keys down
    
    if (not (type(event) == pygame.event.Event and type(event.type == pygame.KEYDOWN))):
        raise Exception("Didn't pass in pygame event object which is a key down event.type")
    
    keysPressed = pygame.key.get_pressed()

    moveDirection : direction = None # initalise. Should be direction enum

    AtLeastOneKeyPressed = False

    # if controls are wasd
    if(gameControls == controls.WASD):
        # if pressed, is True
        wState = keysPressed[pygame.K_w]
        aState = keysPressed[pygame.K_a]
        sState = keysPressed[pygame.K_s]
        dState = keysPressed[pygame.K_d]

        # check if more than 1 are pressed
        totalPressed = 0

        if(wState == True):
            totalPressed += 1
            moveDirection = direction.up
        if(aState == True):
            totalPressed += 1
            moveDirection = direction.left
        if(sState == True):
            totalPressed += 1
            moveDirection = direction.down
        if(dState == True):
            totalPressed += 1
            moveDirection = direction.right

        if(totalPressed > 1):
            print("WARN: More than one movement key pressed, skipping")
            return
        if (totalPressed > 0):
            AtLeastOneKeyPressed = True
            
    # if controls are arrow keys
    elif(gameControls == controls.arrowKeys):
        # if pressed, is True
        upState = keysPressed[pygame.K_UP]
        downState = keysPressed[pygame.K_DOWN]
        leftState = keysPressed[pygame.K_LEFT]
        rightState = keysPressed[pygame.K_RIGHT]

        # check if more than 1 are pressed
        totalPressed = 0

        if(upState == True):
            totalPressed += 1
            moveDirection = direction.up
        if(downState == True):
            totalPressed += 1
            moveDirection = direction.down
        if(leftState == True):
            totalPressed += 1
            moveDirection = direction.left
        if(rightState == True):
            totalPressed += 1
            moveDirection = direction.right

        if(totalPressed > 1):
            print("WARN: More than one movement key pressed, skipping")
            return
        if (totalPressed > 0):
            AtLeastOneKeyPressed = True
    if(AtLeastOneKeyPressed == True):
        handlePlayerMovement(moveDirection)
    
        
def handleKeyUp(event: pygame.event) -> None:
    pass

# Handle key up, pass in the pressed key event as input
while running:
    # fill screen with dark grey
    screen.fill((40,44,49))
    
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("Got quit event")
            running = False
        elif event.type == pygame.KEYDOWN: # handle key down
            hanldKeysDown(event) # pass in key event and call func
        elif event.type == pygame.KEYUP: # handle key up
            handleKeyUp(event) # pass in key event

    playerSnake.updateSnake() # update the snake and move if enough time has passed. Func retunrs True if success
    playerSnake.renderSnake(screen,tileSize)
        

    # flip() the display to put your work on screen
    pygame.display.flip()
    
    clock.tick(75)  # limits FPS 

print("closing")
pygame.quit()
