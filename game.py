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

# Create Direction emnum
class Direction(): 
    up = 1
    down = 2
    left = 3
    right = 4
    none = 5

    # Returns an int
    @staticmethod
    def getOppositeDirection(inputDirecion : int) -> int:
        if(type(inputDirecion) != int):
            raise Exception("ERROR: invalid arg Direction, not an int")
        
        if(inputDirecion == Direction.up):
            return Direction.down
        elif(inputDirecion == Direction.down):
            return Direction.up
        elif(inputDirecion == Direction.left):
            return Direction.right
        elif(inputDirecion == Direction.right):
            return Direction.left
        
    # Returns a string
    @staticmethod
    def DirectionToString(inputDirecion : int) -> str:
        if(type(inputDirecion) != int):
            raise Exception("ERROR: invalid arg Direction, not an int")
        if(inputDirecion == Direction.up):
            return "up"
        elif(inputDirecion == Direction.down):
            return "down"
        elif(inputDirecion == Direction.left):
            return "left"
        elif(inputDirecion == Direction.right):
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
moveKeyDelay = 100 # How many milliseconds betwen each move
moveSnakeDelay = 100 # how many milliseconds between each snake move in snake's current Direction 

# Divide map into invisible GameMap. Each segment of GameMap is a tile.
# Has its own coordinate system. E.g. (1,2) will be second tile on x and third tile on y start from bottom-left. Only positive values go from, note: this means range(0, 9) inlusive, on x, is 10
# (-1 to -10) on x is 10. Same applies to Y
class GameMap():

    errorOnCreation = False
    tileSize: int = 0 # An int. Tile size of x and y for each tile should be square
    rows = 0 # How many rows there are
    rowSize = 0 # How many tiles there are, per row
    rowsUpdated = True # changed to True whenever row count is changed. Start as True to get initial rows
    level = 1 # what level the game is on 
    end = False # end the game bool
    endReason : str = "" # Reason for ending
    gameEndedTextFontSize = 64

    #when GameMap gets intiated. -> [type] is the return. : [type] gives a hint of parameter type
    def __init__(self, tileSize: int) -> None:
        #type check
        if (type(tileSize) != int):
            print("ERROR: tile size is not an int")
            self.errorOnCreation = True
            return None
        
        self.tileSize = tileSize # Set the til size.

    #Updates how many rows are possible
    def UpdateRows(self, screenSizeX : int, screenSizeY : int):
        if(self.rowsUpdated == True):
            self.rowSize = screenSizeX // self.tileSize
            self.rows = screenSizeY // self.tileSize # do a simple floor division

    # Ends a game
    def EndGame(self, reason : str):
        self.end = True # Stops certaining things from updating and rendering
        self.endReason = reason

    # Renders the end game text and reason
    def RenderEndGame(self, screen : pygame.surface.Surface) -> None:
        screenSizeXY : tuple = screen.get_size()
        # Render dark screen with alpha
        alphaSurface = pygame.Surface((screenSizeXY[0], screenSizeXY[1])) # width and height must be a tuple
        alphaSurface.fill((16,16,16))
        alphaSurface.set_alpha(18) # set alpha, int from 0-255
        screen.blit(alphaSurface, (0,0)) # render at (0,0)

        # Display game ended text
        gameEndedText = "Game over"
        gameEndedTextFontSize = self.gameEndedTextFontSize
        gameEndedTextObject = pygame.font.SysFont("Arial Nova", gameEndedTextFontSize)
        gameEndedTextSurface = gameEndedTextObject.render(gameEndedText, True, (221, 50, 50))
        gameEndedTextSize = gameEndedTextSurface.get_size()
        
        gameEndedTextlocation = (screenSizeXY[0] / 2 - gameEndedTextSize[0] / 2,screenSizeXY[1] / 2 - gameEndedTextSize[1] / 2) # Centred in middle of screen
        # Display game ended reason text
        gameEndedReasonText = self.endReason
        gameEndedReasonFontSize = 16
        gameEndedReasonObject = pygame.font.SysFont("Arial Nova", gameEndedReasonFontSize)
        gameEndedReasonSurface = gameEndedReasonObject.render(gameEndedReasonText, True, (207, 55, 55))
        gameEndedReasonSize = gameEndedReasonSurface.get_size()
        gameEndedReasonlocation = (screenSizeXY[0] / 2 - gameEndedReasonSize[0] / 2, gameEndedTextlocation[1] + gameEndedTextSurface.get_height() + 10) # Centred in middle of screen on x and y of game Ended text + padding

        screen.blit(gameEndedTextSurface, gameEndedTextlocation) # render text to screen
        screen.blit(gameEndedReasonSurface, gameEndedReasonlocation) # render text to screen
        

    # returns tile coordinates which real coordihnates are in. Must be a tuple
    @staticmethod
    def realToTileCoords(realCoords : tuple, tileSize: int) -> tuple:
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
    def tileCoordsToReal(tileCoord : tuple, tileSize: int) ->tuple:
       if (type(tileCoord) != tuple):
           raise Exception("ERROR: tileCoord is not a tuple")
       
       realCoord : tuple = (0,0) # initiate

       if(tileCoord[0] < 0): # x negative
           realCoord = (tileCoord[0] * tileSize, realCoord[1])
       elif(tileCoord[0] > 0): # x positive
           realCoord = (tileCoord[0] * tileSize - 1, tileCoord[1])
			 
       if(tileCoord[1] < 0): # y negative
           realCoord = (realCoord[0],tileCoord[1] * tileSize)
       elif(tileCoord[1] > 0): # y positive
           realCoord =  (realCoord[0], tileCoord[1] * tileSize - 1)

       return realCoord
        
# Mainly used as player controller. Handles all stuuff to do with snake
class snake():
    length = 1 # start as length 1
    snakeTilePositions = [(0,0)] # the positions of the snake tile
    snakeTileDirections = [Direction.up] # a list of all snake tile directions, not used in rendering
    currentDirection : int = Direction.up # the current Direction of snake, as int. Default to up
    colour = (116, 149, 189)
    screen : pygame.surface = None # initalise
    gameMap = None # initialise
    firstSnakeRectTilePos : tuple = (0,0) # initalise. This in real coords it is the first, snake tile, position
    updatedPosition : bool = False # default to false, whenever you update snake position set to true
    tileSize = 0 # intialise
    lengthTextPadding = (10,10) # Padding pixels from top-left to give tjhe length text
    lengthTextFontSize = 32 # font size of the length text
    lastUpdatedLength = 1 # start at 1 so no additional length is added

    # constrcutor must have screen and GameMap and tilesiaze arg
    def __init__(self,screen : pygame.surface, gameMap : GameMap, tileSize : int ) -> None:
        # -- Start location

        #floor the / 2 because it avoids decimals 
        startLocation = (screenSize // 2, screenSize // 2) # make starting pos the middle
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
    def MoveSnakeInCurrentDirection(self) -> None:
        currentDirection = self.currentDirection
        positionsLength = len(self.snakeTilePositions)
        lastSnakeRectTilePos = self.snakeTilePositions[positionsLength - 1] # Get the last value in the list
        newRectPosition = (0,0) # initialise
        tileSize = self.tileSize

        if(currentDirection == Direction.up): # moved up
            newRectPosition = (lastSnakeRectTilePos[0], lastSnakeRectTilePos[1] - tileSize)
        elif(currentDirection == Direction.down): # moved down
            newRectPosition = (lastSnakeRectTilePos[0], lastSnakeRectTilePos[1] + tileSize)
        elif(currentDirection == Direction.right): # moved right
            newRectPosition = (lastSnakeRectTilePos[0] + tileSize, lastSnakeRectTilePos[1])
        elif(currentDirection == Direction.left): # moved left
            newRectPosition = (lastSnakeRectTilePos[0] - tileSize, lastSnakeRectTilePos[1])


        self.snakeTilePositions.pop(0) # get rid of first elemenet
        self.snakeTilePositions.append(newRectPosition) # append new one to back of list
        firstDirection = self.snakeTileDirections[0] # get the first element direction before removal
        self.snakeTileDirections.pop(0) # get rid of first elemenet
        self.snakeTileDirections.append(firstDirection) # append new one to back of list

    # Gets a new real tile coord based on old real tile coord.
    def GetNewRealTileBasedOnDirection(self,oldTile : tuple, direction : Direction) -> tuple:
        newRectPosition = (0,0) # initialise
        tileSize = self.tileSize

        if(direction == Direction.up): # moved up
            newRectPosition = (oldTile[0], oldTile[1] - tileSize)
        elif(direction == Direction.down): # moved down
            newRectPosition = (oldTile[0], oldTile[1] + tileSize)
        elif(direction == Direction.right): # moved right
            newRectPosition = (oldTile[0] + tileSize, oldTile[1])
        elif(direction == Direction.left): # moved left
            newRectPosition = (oldTile[0] - tileSize, oldTile[1])

        return newRectPosition

    # must be called each frame, displays the character
    def RenderSnake(self) -> None:
        # print("rendering")
        # pygame.draw.rect(screen, self.colour, pygame.Rect(0,0,100,100))
        # type check
        screen = self.screen
        tileSize = gameMap.tileSize;
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
    def RenderLengthText(self) -> None:
        lengthTextFontSize = self.lengthTextFontSize
        lengthText = "Length: "+str(self.length) # string text to render
        lengthTextObject = pygame.font.SysFont("Arial Nova",lengthTextFontSize)
        lengthTextSurface = lengthTextObject.render(lengthText, True, "white")
        padding = self.lengthTextPadding
        lengthTextlocation = (padding[0],padding[1]) # top left (0,0) + padding. (0,0) can be omitted
        self.screen.blit(lengthTextSurface, lengthTextlocation) # render text to screen
        pass

        
    lastDirectionChangeTime = 0 # in millis
    # changes snake Direction
    def ChangeDirection(self, moveDirection : int) -> None:
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
        if(Direction.getOppositeDirection(self.currentDirection) != moveDirection and self.currentDirection != moveDirection):
            # move snake
            # print(Direction.DirectionToString(Direction.getOppositeDirection(self.currentDirection)))
            # print(Direction.DirectionToString(moveDirection))
            self.currentDirection = moveDirection
        else:    
            print("WARN: Tried to go in opposite Direction with snake or same Direction allready going")
            pass
        
        
        """
        firstSnakeTilePosition = self.firstSnakeRectTilePos
        # Move Snake
        if(moveDirection == Direction.up): # moved up
            self.firstSnakeRectTilePos = (firstSnakeTilePosition[0], firstSnakeTilePosition[1]-tileSize)
        elif(moveDirection == Direction.down): # moved down
            self.firstSnakeRectTilePos = (firstSnakeTilePosition[0], firstSnakeTilePosition[1]+tileSize)
        elif(moveDirection == Direction.left): # moved left
            self.firstSnakeRectTilePos = (firstSnakeTilePosition[0]-tileSize, firstSnakeTilePosition[1])
        elif(moveDirection == Direction.right): # moved right
            self.firstSnakeRectTilePos = (firstSnakeTilePosition[0]+tileSize, firstSnakeTilePosition[1])
        """
        return
    
    lastMoveTime = 0 # in millis

    def CheckIfSnakeIsTouchingSelf(self):
        snakeTilePositions : list = self.snakeTilePositions
        for snakeTilePosition in snakeTilePositions:
            # if more than 1 occurence or (first tile appears no more than twice and updated length != the length)
            if(snakeTilePositions.count(snakeTilePosition) > 1 ):
                # print("Count: "+ str(snakeTilePositions.count(snakeTilePosition)))
                # print("snake is touching self, end")
                self.gameMap.EndGame("Snake head touched body")

    # moves the snake in the Direction it is currently facing. Intended to be called each frame. Not dependent on frames. Render arg is optional, will render after moving if time limit doesn'tt exceed 
    # returns True if success
    
    def UpdateSnake(self) -> bool:#, render = True, screen : pygame.surface = None, tileSize : int = None):
        #print(self.snakeTilePositions)
        self.CheckIfSnakeIsTouchingSelf() # check

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

        # the Direction the snake is facing
        # currentDirection = self.currentDirection
        
        # Get first tile pos, before move
        firstTilePos = self.snakeTilePositions[0]
        # Get first tile direction, before move
        firstTileDirection = self.snakeTileDirections[0]
        
        # Move the snake
        self.MoveSnakeInCurrentDirection()

        snakeTilePositionsLen = len(self.snakeTilePositions)
        screenSizeXY = screen.get_size() # get the screen size
        lastSnakeTilePos = self.snakeTilePositions[snakeTilePositionsLen - 1]
        # check if snake is out of screen bounds
        if((lastSnakeTilePos[0] < 0 or lastSnakeTilePos[0] > screenSizeXY[0]) or (lastSnakeTilePos[1] > screenSizeXY[1] or lastSnakeTilePos[1] < 0)):
            #print("snake is out of bounds, end")
            self.gameMap.EndGame("Snake head is out of screen bounds")

        # if length updated
        if(self.lastUpdatedLength != self.length):
            lengthDifference = self.length - self.lastUpdatedLength # Difference between old and new length
            lastSnakeTilePos = firstTilePos # setup for loop
            lastSnakeTileDirection = firstTileDirection
            for lengthIndex in range(0,lengthDifference):
                newTilePosition = (0,0) # default to 0,0
                newDirection = Direction.getOppositeDirection(lastSnakeTileDirection) # default to last

                if (lengthIndex != 0): # If not first iteration
                    # new tile pos is 
                    newTilePosition = self.GetNewRealTileBasedOnDirection(lastSnakeTilePos, Direction.getOppositeDirection(firstTileDirection))
                else: # first iteration
                    newTilePosition = firstTilePos # all u need

                #  Add tile pos to snake
                self.snakeTilePositions.insert(0,newTilePosition)
                #  Add tile direction to snake
                self.snakeTileDirections.insert(0,newDirection)

                # setup next frame 
                lastSnakeTilePos = newTilePosition
                lastSnakeTileDirection = newDirection
                self.lastUpdatedLength += 1
            
        
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
    def GetSnakePosTiles(self) -> list:
        endList = [] # init
        for realPos in self.snakeTilePositions:
            endList.append(GameMap.realToTileCoords(realPos, tileSize))
        return endList


# controls all fruit on map
class FruitController():

    fruitLocations = [] # Real fruit coords
    fruitLengthReward = 1 # how much length a snake gains for eating a fruit
    screen : pygame.surface = None
    gameMap : GameMap = None
    fruitColour = (241,74,74) # in rgb 
    amnountOfFruitPerLevel = 1 # how much much fruit is the amnt per level
    amnountOfFruitEatenThisLevel : int = 0 # How much fruit has been eaten this level
    loadedFruitsForLevel : int = 0 # 0 means no loaded level. It means what level was the last fruit load

    # Consrecutor
    def __init__(self, screen : pygame.surface, gameMap : GameMap) -> None:
        self.screen = screen
        self.gameMap = gameMap

    # Returns a list of the fruit positions turned into tiles
    def getFruitPosTiles(self) -> list: 
        endList = [] # init
        for realPos in self.fruitLocations:
            endList.append(GameMap.realToTileCoords(realPos, tileSize))
        return endList

    # delete fruit will delete the fruit automatically
    def checkIfSnakeTouchingFruit(self, inputSnake : snake, deleteFruit: bool = True) -> bool:
        fruitTiles = self.getFruitPosTiles() # Get fruits as tiles
        snakeTiles = inputSnake.GetSnakePosTiles() # Get snake as tiles
        if snakeTiles[len(snakeTiles)-1] in fruitTiles: # check for a match with leading end of snake tile and all fruit tiles
            if(deleteFruit == True):
                fruitTileIndex = fruitTiles.index(snakeTiles[len(snakeTiles)-1]) # get fruit tile index
                self.fruitLocations.pop(fruitTileIndex)
            return True

    #spawns a fruit on the map, really just stores positional data. You need to render all fruits to see changes. Pass in tiee coords. not real ones
    def SpawnFruit(self, fruitTilePosition : tuple) -> bool:
        realTilePosition = GameMap.tileCoordsToReal(fruitTilePosition, tileSize)
        self.fruitLocations.append(realTilePosition)

    # Updates fruits, intended to be called each frame
    def updateFruits(self, inputSnake: snake)-> None:

        #screen = self.screen
        gameMap = self.gameMap
        #tileSize = gameMap.tileSize

        snakeIsTouchingFruit = self.checkIfSnakeTouchingFruit(playerSnake, True) # delet fruit automatcally

        amnountOfFruitPerLevel = self.amnountOfFruitPerLevel

        if(snakeIsTouchingFruit == True):
            playerSnake.length += self.fruitLengthReward
            self.amnountOfFruitEatenThisLevel += 1 # ate one fruit

        if(self.amnountOfFruitEatenThisLevel == amnountOfFruitPerLevel):
            gameMap.level += 1 # increment level by 1
            self.amnountOfFruitEatenThisLevel = 0 # reset amount of fruits eaten per level
            print("Moving to next level:"+str(gameMap.level))
        elif(self.amnountOfFruitEatenThisLevel > amnountOfFruitPerLevel):
            print("WARN: The player ate more fruits than allowed for level")

        # get range of tiles not in snake
        generationRanges = [] # each list in the list is a range (tuple) where fruits can generate. If empty list they can't generate in this row
        snakeTiles = inputSnake.GetSnakePosTiles()
        # fruitTiles = self.getFruitPosTiles()
        # generate lists for each row
        gameMap.UpdateRows(screenSizeX=screenSize, screenSizeY=screenSize) # if rows have not been calculated
        totalRows = gameMap.rows # Get total possible rows as an int
        rowSize = gameMap.rowSize # How many tiles there r per row
        

        if(self.loadedFruitsForLevel != gameMap.level):
            for rowIndex in range(0,totalRows):
                if(not (rowIndex == 1 or rowIndex == totalRows)):
                    rowRanges : list = [] # intialise the row ranges
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
                            if (lastColumnIntersect+1 != rowSize and (columnIndex == 1 or columnIndex == rowSize)): # if last intersecting column + 1 is not the end 
                                rowRanges.append((lastColumnIntersect+1,rowSize))
                            # else, leave list empty
                        elif((not (nextTile in snakeTiles)) and (tempTile in snakeTiles)): # not last column and next tile is not intersecting and this column  is intersectingg
                            if(firstIntersectRecorded == True): # if first recorded intersect
                                firstIntersectRecorded = False
                                rowRanges.append((1, interesctingColumn-1)) # start at 1
                            else: # not first
                                rowRanges.append((lastColumnIntersect+1, interesctingColumn-1)) # from last intersect to current
                        
                        
                    # Row doesn't intersect with snake
                    # print(rowDoesIntersectWithSnake)
                    if(rowDoesIntersectWithSnake == False):
                        rowRanges = [(1,rowSize)]

                    generationRanges.append(rowRanges) # add a list for each row

                """
                willRowSpawnFruit = getRandomChanceResult(self.fruitSpawnChance)

                if(willRowSpawnFruit):
                    #choose a random range
                    rowRangeLength = len(endList) # length of list of elements in row range list. W
                    chosenRowRange : tuple = endList[random.randint(0,rowRangeLength - 1)] # a tuple of potential ranges
                    fruitTilePosition = (rowIndex, random.randint(chosenRowRange[0],chosenRowRange[1])) # the  chosen tile for fruit'
                    self.SpawnFruit(fruitTilePosition) # add the fruit to map
                """
                # end of row for loop
            
            # all of the chosen row indexes 
            chosenRowindexes = [] 

            #range is eclusive
            for index in range(0, amnountOfFruitPerLevel):
                #choose a random range
                genRangesLength = len(generationRanges)
                chosenRowIndex = random.randint(0, genRangesLength - 1)
                chosenRowindexes.append(chosenRowIndex)

            # loop thru all rows
            for chosenRowIndex in chosenRowindexes: 
                rowRangeList = generationRanges[chosenRowIndex]
                rowRangeLength = len(rowRangeList) # length of list of elements in row range list. W
                chosenRowRange : tuple = rowRangeList[random.randint(0,rowRangeLength - 1)] # a tuple of potential ranges
                fruitTilePosition = (chosenRowIndex, random.randint(chosenRowRange[0],chosenRowRange[1])) # the chosen tile for fruit'
                self.SpawnFruit(fruitTilePosition) # add the fruit to map


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
        

tileSize = 20
gameMap = GameMap(tileSize)

if (gameMap.errorOnCreation):
    print("!! There was an error creating the map !!")

inpCoords = (30,19) # input coordinates
print("input coords: (" + str(inpCoords[0]) + ", " + str(inpCoords[1]) +")")
tileCoords = GameMap.realToTileCoords(inpCoords, tileSize)
print(tileCoords)
realCoords = (GameMap.tileCoordsToReal(tileCoords, tileSize))
print(realCoords)
playerSnake = snake(screen, gameMap, tileSize)
fruitController = FruitController(screen, gameMap)
gameControls = controls.WASD

def handlePlayerMovement(moveDirection : int):
    print("Moving in Direction " + Direction.DirectionToString(moveDirection))
    playerSnake.ChangeDirection(moveDirection) # type checking is done in function

# Handle key down, pass in the pressed key event as input. Is oj
def hanldKeysDown(event: pygame.event) -> None:
    print("Called key down function") # Is only called once regardless of keys down
    
    if (not (type(event) == pygame.event.Event and type(event.type == pygame.KEYDOWN))):
        raise Exception("Didn't pass in pygame event object which is a key down event.type")
    
    keysPressed = pygame.key.get_pressed()

    moveDirection : Direction = None # initalise. Should be Direction enum

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
            moveDirection = Direction.up
        if(aState == True):
            totalPressed += 1
            moveDirection = Direction.left
        if(sState == True):
            totalPressed += 1
            moveDirection = Direction.down
        if(dState == True):
            totalPressed += 1
            moveDirection = Direction.right

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
            moveDirection = Direction.up
        if(downState == True):
            totalPressed += 1
            moveDirection = Direction.down
        if(leftState == True):
            totalPressed += 1
            moveDirection = Direction.left
        if(rightState == True):
            totalPressed += 1
            moveDirection = Direction.right

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

    if(gameMap.end == False):
        playerSnake.UpdateSnake() # update the snake and move if enough time has passed. Func retunrs True if success
    # render snake below text in case player decides to go under text
    playerSnake.RenderSnake()
    if(gameMap.end == False):
        fruitController.updateFruits(playerSnake)
    fruitController.renderFruits()
    if(gameMap.end == False):
        playerSnake.RenderLengthText()
    else: # ended ==  True
        gameMap.RenderEndGame(screen) 


    # flip() the display to put your work on screen
    pygame.display.flip()
    
    clock.tick(75)  # limits FPS 

print("closing")
pygame.quit()
