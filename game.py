thisFolder = "/python-programming/snake game/"
import pygame # pygame renderer for 2D
import math
import numpy # for tuple math
import time
import random

def getCurrentMillisecondTime():
    return round(time.time() * 1000)

# enter a chance and if number between 1-100. Chance input is intended to be a decimal less than 1. Chance is timesed by 100. Returns true if success, false if not 
def getRandomChanceResult(chance : float) -> bool:
    randomNum = random.randint(1,100)
    chance = chance * 100.0
    if(chance <= randomNum):
        return True
    else:
        return False
    
def checkOccurences():
    pass

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
screenSize = 719 # will be two sets of screen size, a square
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
    rows = 0 # How many rows there are
    rowSize = 0 # How many tiles there are, per row
    rowsUpdated = True # changed to True whenever row count is changed. Start as True to get initial rows
    level = 1 # what level the game is on 

    #when grid gets intiated. -> [type] is the return. : [type] gives a hint of parameter type
    def __init__(self, tileSize: int) -> None:
        #type check
        if (type(tileSize) != int):
            print("ERROR: tile size is not an int")
            self.errorOnCreation = True
            return None
        
        self.tileSize = tileSize # Set the til size.

    #Updates how many rows are possible
    def updateRows(self, screenSizeX : int, screenSizeY : int):
        if(self.rowsUpdated == True):
            self.rowSize = screenSizeX // self.tileSize
            self.rows = screenSizeY // self.tileSize # do a simple floor division

    # returns tile coordinates which real coordihnates are in. Must be a tuple
    @staticmethod
    def realToTileCoords(realCoords : tuple) -> tuple:
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
    @staticmethod
    def tileCoordsToReal(tileCoord : tuple) ->tuple:
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
    snakeTilePositions = [(0,0)] # the positions of the snake tile
    currentDirection : int = direction.up # the current direction of snake, as int. Default to up
    colour = (116, 149, 189)
    screen : pygame.surface = None # initalise
    gameMap = None # initialise
    firstSnakeRectTilePos : tuple = (0,0) # initalise. This in real coords it is the first, snake tile, position
    updatedPosition : bool = False # default to false, whenever you update snake position set to true
    tileSize = 0 # intialise
    lengthTextPadding = (10,10) # Padding pixels from top-left to give tjhe length text
    lengthTextFontSize = 32 # font size of the lngth text
    lastUpdatedLength = 1 # start at 1 so no additional length is added
    # constrcutor must have screen and grid and tilesiaze arg
    def __init__(self,screen : pygame.surface, gameMap : grid, tileSize : int ) -> None:
        # -- Start location
        startLocation =  (screenSize/2, screenSize/2) # make starting pos the middle
        if (startLocation[0] > 0 and startLocation[0] % 2 == 0 ): # if even and positive on x
            startLocation = (startLocation[0] -1, startLocation[1]) # same location -1 on x
        if (startLocation[1] > 0 and startLocation[1] % 2 == 0 ): # if even and positive on y
            startLocation = (startLocation[0],startLocation[1] -1) # same location -1 on y
        self.snakeTilePositions[0] = startLocation # set it
        # -- More init
        self.tileSize = tileSize
        self.screen = screen
        self.gameMap = gameMap

    # move the snake in self.currentDirection ny removing on tile and adding another
    def moveSnakeInCurrentDirection(self) -> None:
        currentDirection = self.currentDirection
        positionsLength = len(self.snakeTilePositions)
        lastSnakeRectTilePos = self.snakeTilePositions[positionsLength - 1] # Get the last value in the list
        newRectPosition = (0,0) # initialise

        if(currentDirection == direction.up): # moved up
            newRectPosition = (lastSnakeRectTilePos[0], lastSnakeRectTilePos[1] - tileSize)
        elif(currentDirection == direction.down): # moved down
            newRectPosition = (lastSnakeRectTilePos[0], lastSnakeRectTilePos[1] + tileSize)
        elif(currentDirection == direction.right): # moved right
            newRectPosition = (lastSnakeRectTilePos[0] + tileSize, lastSnakeRectTilePos[1])
        elif(currentDirection == direction.left): # moved left
            newRectPosition = (lastSnakeRectTilePos[0] - tileSize, lastSnakeRectTilePos[1])
        self.snakeTilePositions.pop(0) # get rid of first elemenet
        self.snakeTilePositions.append(newRectPosition) # append new one to front of list

    # must be called each frame, displays the character
    def renderSnake(self) -> None:
        # print("rendering")
        # pygame.draw.rect(screen, self.colour, pygame.Rect(0,0,100,100))
        # type check
        if (type(screen) != pygame.surface.Surface):
            raise Exception("ERROR: didn't pass a valid screen arg")
        if (type(tileSize) != int):
            raise Exception("ERROR: didn't pass a valid tileSize arg")
        firstSnakeRectTilePosition = self.snakeTilePositions[0] # set this
        # Set to false
        if(self.updatedPosition == True):
                self.updatedPosition = False

        # second number is the stop exclusive
        for lengthIndex in range(0,len(self.snakeTilePositions)):
            
            # Don't use match/case  because it is not supported below python 3.10
            rectPosition = self.snakeTilePositions[lengthIndex] # Get the position applied to this omdex
            


            # print("Snake index: "+str(lengthIndex)+" with position ("+str(rectPosition[0])+","+str(rectPosition[1])+")")
            snakeRect = pygame.Rect(rectPosition[0], rectPosition[1], tileSize, tileSize)

            # print("drawing a rect")
            pygame.draw.rect(screen, self.colour, snakeRect)

            # setup next move
            
    # renders the length of the snake text
    def renderLengthText(self) -> None:
        lengthTextFontSize = self.lengthTextFontSize
        lengthText = "Length: "+str(self.length) # string text to render
        lengthTextObject = pygame.font.SysFont("Arial Nova",lengthTextFontSize)
        lengthTextSurface = lengthTextObject.render(lengthText, True, "white")
        padding = self.lengthTextPadding
        lengthTextlocation = (padding[0],padding[1]) # top left (0,0) + padding. (0,0) can be omitted
        self.screen.blit(lengthTextSurface, lengthTextlocation) # render text to screen
        pass

        
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

    def checkIfSnakeIsTouchingSelf(self):
        snakeTilePositions : list = self.snakeTilePositions
        for snakeTilePosition in snakeTilePositions:
            # if more than 1 occurence or (first tile appears no more than twice and updated length != the length)
            if(snakeTilePositions.count(snakeTilePosition) > 1 ):
                print("snake is touching self, end")

    # moves the snake in the direction it is currently facing. Intended to be called each frame. Not dependent on frames. Render arg is optional, will render after moving if time limit doesn'tt exceed 
    # returns True if success
    
    def updateSnake(self) -> bool:#, render = True, screen : pygame.surface = None, tileSize : int = None):
        print(self.snakeTilePositions)
        self.checkIfSnakeIsTouchingSelf() # check

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
        # currentDirection = self.currentDirection
        

        

        # 1. if length updated
        if(self.lastUpdatedLength != self.length):
            # Get last tile pos
            lastTilePos = self.snakeTilePositions[0]
            # 2. Add last tile pos
            self.snakeTilePositions.append(lastTilePos)
            # 3. setup next frame
            self.lastUpdatedLength = self.length
        
        # 4. Move the snake
        self.moveSnakeInCurrentDirection()
            
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
    
    # returns a list of all snake tiles
    def getSnakePosTiles(self) -> list:
        endList = [] # init
        for realPos in self.snakeTilePositions:
            endList.append(grid.realToTileCoords(realPos))
        return endList


# controls all fruit on map
class FruitController():
    fruitLocations = [] # Real fruit coords
    fruitLengthReward = 1 # how much length a snake gains for eating a fruit
    screen : pygame.surface = None
    gameMap : grid = None
    fruitColour = (241,74,74) # in rgb 
    fruitSpawnChance : float = 10/5184 # chance for a fruit to spawn in a tile
    loadedFruitsForLevel = 0 # 0 means no loaded level

    # Consrecutor
    def __init__(self, screen : pygame.surface, gameMap : grid) -> None:
        self.screen = screen
        self.gameMap = gameMap

    # Returns a list of the fruit positions turned into tiles
    def getFruitPosTiles(self) -> list: 
        endList = [] # init
        for realPos in self.fruitLocations:
            endList.append(grid.realToTileCoords(realPos))
        return endList

    # delete fruit will delete the fruit automatically
    def checkIfSnakeTouchingFruit(self, inputSnake : snake, deleteFruit: bool = True) -> bool:
        fruitTiles = self.getFruitPosTiles() # Get fruits as tiles
        snakeTiles = inputSnake.getSnakePosTiles() # Get snake as tiles
        if snakeTiles[len(snakeTiles)-1] in fruitTiles: # check for a match with leading end of snake tile and all fruit tiles
            if(deleteFruit == True):
                fruitTileIndex = fruitTiles.index(snakeTiles[len(snakeTiles)-1]) # get fruit tile index
                self.fruitLocations.pop(fruitTileIndex)
            return True

    #spawns a fruit on the map, really just stores positional data. You need to render all fruits to see changes
    def SpawnFruit(self, fruitTilePosition : tuple) -> bool:
        realTilePosition = grid.tileCoordsToReal(fruitTilePosition)
        self.fruitLocations.append(realTilePosition)

    # Updates fruits, intended to be called each frame
    def updateFruits(self, inputSnake: snake)-> None:

        screen = self.screen
        gameMap = self.gameMap
        tileSize = gameMap.tileSize

        snakeIsTouchingFruit = self.checkIfSnakeTouchingFruit(playerSnake, True) # delete automatcally

        if(snakeIsTouchingFruit == True):
            playerSnake.length += self.fruitLengthReward

        # get range of tiles not in snake
        generationRanges = [] # each list in the list is a range (tuple) where fruits can generate. If empty list they can't generate in this row
        snakeTiles = inputSnake.getSnakePosTiles()
        fruitTiles = self.getFruitPosTiles()
        # generate lists for each row
        gameMap.updateRows(screenSizeX=screenSize, screenSizeY=screenSize) # if rows have not been calculated
        totalRows = gameMap.rows # Get total possible rows as an int
        rowSize = gameMap.rowSize # How many tiles there r per row
        
        if(self.loadedFruitsForLevel != gameMap.level):
            for rowIndex in range(0,totalRows):
                endList = []
                rowDoesIntersectWithSnake = False
                firstIntersectRecorded = True # bool of whether the first ineterse
                # loop throuugh columns of row
                lastColumnIntersect = 1 # initialised, the column of intersect 
                for columnIndex in range(0, rowSize+1): # range exclusive
                    tempTile = (rowIndex, columnIndex)
                    nextTile = (rowIndex, columnIndex + 1) # next tile, it is handled if last column
                    interesctingColumn : int = columnIndex # init
                    if (tempTile in snakeTiles ):
                        interesctingColumn = columnIndex
                        rowDoesIntersectWithSnake = True
                        lastColumnIntersect = interesctingColumn
                        
                    if(columnIndex == rowSize): #  last index
                        interesctingColumn = columnIndex
                        if (lastColumnIntersect+1 != rowSize): # if last intersecting column + 1 is not the end 
                            endList.append((lastColumnIntersect+1,rowSize))
                        # else, leave list empty
                    elif((not (nextTile in snakeTiles)) and (tempTile in snakeTiles)): # not last column and next tile is not intersecting and this column  is intersectingg
                        if(firstIntersectRecorded == True): # if first recorded intersect
                            firstIntersectRecorded = False
                            endList.append((1, interesctingColumn-1)) # start at 1
                        else: # not first
                            endList.append((lastColumnIntersect+1, interesctingColumn-1)) # from last intersect to current
                        
                        
                # Row doesn't intersect with snake
                # print(rowDoesIntersectWithSnake)
                if(rowDoesIntersectWithSnake == False):
                    endList = [(1,rowSize)]

                generationRanges.append(endList) # add a list for each row

                willRowSpawnFruit = getRandomChanceResult(self.fruitSpawnChance)

                if(willRowSpawnFruit):
                    #choose a random range
                    rowRangeLength = len(endList) # length of list of elements in row range list. W
                    chosenRowRange : tuple = endList[random.randint(0,rowRangeLength - 1)] # a tuple of potential ranges
                    fruitTilePosition = (rowIndex, random.randint(chosenRowRange[0],chosenRowRange[1])) # the  chosen tile for fruit'
                    self.SpawnFruit(fruitTilePosition) # add the fruit to map


                # end of row for loop
            self.loadedFruitsForLevel = gameMap.level # finally set loaded fruits        
            

    # Render all fruits on the map
    def renderFruits(self) -> None:
        for realFruitPosition in self.fruitLocations:        
            fruitRect = pygame.Rect(realFruitPosition[0], realFruitPosition[1], tileSize, tileSize)
            # print("drawing a rect")
            pygame.draw.rect(screen, self.fruitColour, fruitRect)

        #print("---Gen range start---")
        #print(generationRange)
        #print("---Gen range end---")
        

tileSize = 10
gameMap = grid(tileSize)

if (gameMap.errorOnCreation):
    print("!! There was an error creating the map !!")

inpCoords = (30,19) # input coordinates
print("input coords: (" + str(inpCoords[0]) + ", " + str(inpCoords[1]) +")")
tileCoords = grid.realToTileCoords(inpCoords)
print(tileCoords)
realCoords = (grid.tileCoordsToReal(tileCoords))
print(realCoords)
playerSnake = snake(screen, gameMap, tileSize)
fruitController = FruitController(screen, gameMap)
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
    # render snake below text in case player decides to go under text
    playerSnake.renderSnake()
    fruitController.updateFruits(playerSnake)
    fruitController.renderFruits()
    playerSnake.renderLengthText()

    # flip() the display to put your work on screen
    pygame.display.flip()
    
    clock.tick(75)  # limits FPS 

print("closing")
pygame.quit()
