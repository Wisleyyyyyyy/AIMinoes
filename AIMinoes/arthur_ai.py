import pygame
from copy import deepcopy

import numpy as np

class ArthurAI:
    type = None
    key = None
    events = []

    def __init__(self, type, key):
        self.type = type
        self.key = key

    #Count holes
    def countHoles(self,gameArea):
        totalCoveredHoles = 0
        #Using gamearea array, store columns instead of rows in a seperate array
        gamearea_columns = [[0 for i in range(20)]
                            for j in range (10)]

        for y, row in enumerate(gameArea):
            for x, value in enumerate(row):
                gamearea_columns[x][y] = value

        #Count number of holes
        for x, col in enumerate(gamearea_columns):
            filled = 0
            for y, value in enumerate(col):
                if value > 0:
                    filled = 1
                if value == 0 and filled == 1:
                    totalCoveredHoles += 1
                        
        return totalCoveredHoles

    #Count Sum of differences of adjacent column heights
    def countSumDiffAdjHeights(self, gameArea):
        totalDiff = 0

        #Using gamearea array, store columns instead of rows in a seperate array
        gamearea_columns = [[0 for i in range(20)]
                            for j in range (10)]

        for y, row in enumerate(gameArea):
            for x, value in enumerate(row):
                gamearea_columns[x][y] = value

        columnHeights = [0 for y in range(10)]

        #Find column heights
        for x, col in enumerate(gamearea_columns):
            for y, value in enumerate(col):
                if value > 0:
                    columnHeights[x] = np.abs(20-y)
                    break

        columnHeights_difference = [0 for y in range(9)]
        for column, height in enumerate(columnHeights):
            if(column < 9):
                columnHeight_difference = np.abs(height - columnHeights[column+1])
                columnHeights_difference[column] = columnHeight_difference
        
        for difference in columnHeights_difference:
            totalDiff += difference

        return totalDiff

    #Get all possible actions for current piece
    def getActions(self, currentpiece):
        pieceRotations = [0, 90, 180, 270] #4 Rotations
        pieceMoves = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5] #11 Moves
        actions = [] #44 Possible Rotations*Moves
        for rot in range(len(pieceRotations)):
            for move in range(len(pieceMoves)):
                actions.append((pieceRotations[rot],pieceMoves[move]))
        return actions

    #Store valid actions and values
    def actionsValues(self, gamearea, currentpiece):
        actions = self.getActions(currentpiece)

        actionValues = {}

        for action in actions:
            gamearea_copy = deepcopy(gamearea)  
            piece_copy = deepcopy(currentpiece) 
            rotation = action[0]
            move = action[1]

            rotationsCompleted = 0
            
            timesToRotate = 0

            #Rotate Piece
            if(rotation > 0):
                timesToRotate = rotation / 90
            if(rotationsCompleted != timesToRotate):
                for i in range((int(timesToRotate))):
                    center = piece_copy[1]
                    for ii in range(4):
                        x = piece_copy[ii].y - center.y
                        y = piece_copy[ii].x - center.x
                        piece_copy[ii].x = center.x - x
                        piece_copy[ii].y = center.y + y
                    rotationsCompleted += 1
            #When Piece Rotation is complete, Move piece
            if(rotationsCompleted == timesToRotate):
                toMoveRight = 0
                toMoveLeft = 0
                if(move > 0):
                    toMoveRight = move
                elif(move < 0):
                    toMoveLeft = np.abs(move)

                if(toMoveRight > 0):
                    for i in range(toMoveRight):
                        for ii in range(4):
                            piece_copy[ii].x += 1
                elif(toMoveLeft > 0):
                    for i in range(toMoveLeft):
                        for ii in range(4):
                            piece_copy[ii].x -= 1

                mostRightPiece = 0
                mostLeftPiece = 69

                for j in range(4):
                    if(piece_copy[j].x > mostRightPiece):
                        mostRightPiece = piece_copy[j].x
                for jj in range(4):
                    if(piece_copy[jj].x < mostLeftPiece):
                        mostLeftPiece = piece_copy[jj].x

                #Valid move if piece ends up within gamearea
                if(mostRightPiece < 10 and mostLeftPiece > -1):
                    #Drop piece_copy to the bottom of gamearea
                    for h in range(20):
                        for j in range(4):
                            piece_copy[j].y += 1
                        
                        for ii in range(4):
                            for jj in range(20):
                                #If piece_copy goes below the bottom of gamearea, 
                                #bring it back into the gamearea
                                if(piece_copy[ii].y > 19):
                                    for kk in range(4):
                                        piece_copy[kk].y -= 1
                        for ee in range(4):
                            if (piece_copy[ee].y > 0):
                                if (gamearea_copy[piece_copy[ee].y][piece_copy[ee].x] == 1):
                                    #If collided with fixed pieces on the board
                                    #move piece_copy up
                                    for kk in range(4):
                                            piece_copy[kk].y -= 1

                    #Add piece_copy to gamearea_check
                    for k in range(4):
                        gamearea_copy[piece_copy[k].y][piece_copy[k].x] = 1

                    # #Check if by putting the piece in this position, does it complete a line
                    # #if it does, priortize and make this the best action
                    linescleared = 0
                    for y, row in enumerate(gamearea_copy):
                        blocksFilled = 0
                        for x, value in enumerate(row):
                            if value == 1:
                                blocksFilled += 1
                            #If line can be completed, this action will be the best action
                            if blocksFilled == 10:
                                linescleared += 1

                    #If no line can be completed, store values with action as the key
                    holes = self.countHoles(gamearea_copy)
                    heightDiff = self.countSumDiffAdjHeights(gamearea_copy)

                    actionValues[action] = (holes,heightDiff,linescleared)

        return actionValues
           
    #Return Action that gives the best outcome
    def bestAction(self, gamearea, currentpiece):

            bestAction = None
            leastHoles = 6969
            leastHeightDiff = 6969
            
            #Find action that generates least holes and 
            #least sum of differences of adjacent column heights 
            actionsValues = self.actionsValues(gamearea, currentpiece)
            for action in actionsValues:
                if(actionsValues[action][0] < leastHoles or \
                   actionsValues[action][0] == leastHoles and \
                   actionsValues[action][1] < leastHeightDiff):
                   leastHoles = actionsValues[action][0]
                   leastHeightDiff = actionsValues[action][1]
                   bestAction = action

                if(actionsValues[action][2] > 0):
                    bestAction = action
                    break

            return bestAction
