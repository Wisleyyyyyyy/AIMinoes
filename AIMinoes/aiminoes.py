import pygame
from copy import deepcopy
from random import choice

import numpy as np

import torch
import torch.nn as nn

SCREEN_HEIGHT = 800
SCREEN_WIDTH = 1200
GAMEAREA_HEIGHT = 700
GAMEAREA_WIDTH = 350
FPS = 120
BLOCKSIZE = 35

TOPLEFT_X = (SCREEN_WIDTH - GAMEAREA_WIDTH) // 2

#AIMinoes class
class AIMinoes:
    def __init__(self):
        self.display = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.textFont = pygame.font.SysFont('freesansbold.ttf', 46)

        self.text_NextPiece = self.textFont.render('Next Piece', True, pygame.Color('red'))
        self.text_NextPiece_Rect = self.text_NextPiece.get_rect()
        self.text_NextPiece_Rect.x = SCREEN_WIDTH - (SCREEN_WIDTH // 3)
        self.text_NextPiece_Rect.y = BLOCKSIZE

        self.text_Score = self.textFont.render('Score', True, pygame.Color('red'))
        self.text_Score_Rect = self.text_Score.get_rect()
        self.text_Score_Rect.x = SCREEN_WIDTH - (SCREEN_WIDTH // 3)
        self.text_Score_Rect.y = SCREEN_HEIGHT//2

        self.text_Linescleared = self.textFont.render('Lines Cleared', True, pygame.Color('red'))
        self.text_Linescleared_Rect = self.text_Linescleared.get_rect()
        self.text_Linescleared_Rect.x = SCREEN_WIDTH - (SCREEN_WIDTH // 3)
        self.text_Linescleared_Rect.y = SCREEN_HEIGHT//2 + 100

        self.text_Efficiency = self.textFont.render('Efficiency', True, pygame.Color('red'))
        self.text_Efficiency_Rect = self.text_Efficiency.get_rect()
        self.text_Efficiency_Rect.x = SCREEN_WIDTH - (SCREEN_WIDTH // 3)
        self.text_Efficiency_Rect.y = SCREEN_HEIGHT//2 + 200

        #Initialize grid
        self.grid = [pygame.Rect(x * BLOCKSIZE + TOPLEFT_X, y * BLOCKSIZE,
                    BLOCKSIZE, BLOCKSIZE)
                    for x in range(GAMEAREA_WIDTH//BLOCKSIZE)
                    for y in range(GAMEAREA_HEIGHT//BLOCKSIZE)]

        #Initialize Coordinates of Pieces
        self.long_piece_coordinates = [(-2,0),(-1,0),(0,0),(1,0)]
        self.l_piece_coordinates = [(-1,-1),(0,0),(0,-1),(0,1)]
        self.j_piece_coordinates = [(-1,1),(-1,0),(-1,-1),(-1,-2)]
        self.z_piece_coordinates = [(-1,1),(-1,0),(0,0),(0,-1)]
        self.s_piece_coordinates = [(-1,-1),(-1,0),(0,0),(0,1)]
        self.t_piece_coordinates = [(-1,0),(0,0),(0,-1),(0,1)]
        self.box_piece_coordinates = [(-1,-1),(0,0),(-1,0),(0,-1)]


        self.pieces_coordinates = [self.long_piece_coordinates, self.l_piece_coordinates,
                                   self.j_piece_coordinates, self.z_piece_coordinates,
                                   self.s_piece_coordinates, self.t_piece_coordinates,
                                   self.box_piece_coordinates]
        self.piece_ids = [0, 1, 2, 3, 4, 5, 6]   

        self.pieces = [[pygame.Rect(x + (GAMEAREA_WIDTH//BLOCKSIZE) // 2, y + 1, 1, 1)
                for x, y in piece_coordinates]
                for piece_coordinates in self.pieces_coordinates]
        self.piece_rect = pygame.Rect(0, 0, BLOCKSIZE - 2, BLOCKSIZE - 2)

        #Inital Score
        self.score = 0
        self.lineclear = 0
        self.totalLinescleared = 0
        self.totalPiecesUsed = 0
        self.efficiency = 0
        self.scores = {0:0,
                1:40,
                2:100,
                3:300,
                4:1200}
        self.reward = 0
        self.pieceLanded = False
        self.actionComplete = False
        self.newPiece = True
        
        self.DIFFICULTY = 1
        self.DROPTIMER = 0
        self.DROPACCELERATION = 1

        #Start with random piece
        self.pieceid = choice(self.piece_ids)
        self.piece = deepcopy(self.pieces[self.pieceid])
        self.nextpieceid = choice(self.piece_ids)
        self.next_piece = deepcopy(self.pieces[self.nextpieceid])
        #Default piece rotation
        self.pieceRotation = 0
        #Initialize Empty Game Area
        self.gameArea = [[0 for i in range(GAMEAREA_WIDTH//BLOCKSIZE)]
                    for j in range (GAMEAREA_HEIGHT//BLOCKSIZE)]

    #Draw Text objects
    def drawTextObjects(self):
        
        self.display.blit(self.text_NextPiece,self.text_NextPiece_Rect)
        self.display.blit(self.text_Score,self.text_Score_Rect)
        self.display.blit(self.textFont.render(str(self.score),True,
                            pygame.Color('white')),
                            ((SCREEN_WIDTH - (SCREEN_WIDTH // 3)),
                            ((SCREEN_HEIGHT//2)+BLOCKSIZE)))
        self.display.blit(self.text_Linescleared,self.text_Linescleared_Rect)
        self.display.blit(self.textFont.render(str(self.totalLinescleared),True,
                            pygame.Color('white')),
                            ((SCREEN_WIDTH - (SCREEN_WIDTH // 3)),
                            ((SCREEN_HEIGHT//2)+BLOCKSIZE + 100)))   

        self.display.blit(self.text_Efficiency,self.text_Efficiency_Rect)
        self.display.blit(self.textFont.render(str(self.efficiency),True,
                            pygame.Color('white')),
                            ((SCREEN_WIDTH - (SCREEN_WIDTH // 3)),
                            ((SCREEN_HEIGHT//2)+BLOCKSIZE + 200)))                                       


                            
    #Draw game area
    def drawGamearea(self):
        #Draw game area background
        pygame.draw.rect(self.display,(0,0,0),(TOPLEFT_X,0,
                        GAMEAREA_WIDTH,GAMEAREA_HEIGHT))
        #Draw game area
        for y, row in enumerate(self.gameArea):
            for x, value in enumerate(row):

                if value > 0:
                    self.piece_rect.x = x * BLOCKSIZE + TOPLEFT_X
                    self.piece_rect.y = y * BLOCKSIZE
                    pygame.draw.rect(self.display,pygame.Color('white'),self.piece_rect)

    #Draw piece
    def drawPiece(self):
        for i in range(4):
            self.piece_rect.x = self.piece[i].x * BLOCKSIZE + TOPLEFT_X
            self.piece_rect.y = self.piece[i].y * BLOCKSIZE
            pygame.draw.rect(self.display, pygame.Color('red'), self.piece_rect)

    #Draw next piece
    def drawNextPiece(self):
        #Draw next piece area background
        pygame.draw.rect(self.display,(0,0,0),(TOPLEFT_X*2,SCREEN_HEIGHT//8,
                        BLOCKSIZE*6,BLOCKSIZE*6))
        for i in range(4):
            self.piece_rect.x = self.next_piece[i].x * BLOCKSIZE + (TOPLEFT_X*2) - BLOCKSIZE*2
            self.piece_rect.y = self.next_piece[i].y * BLOCKSIZE + SCREEN_HEIGHT//5
            pygame.draw.rect(self.display, pygame.Color('red'), self.piece_rect)

    #Check collision
    def checkCollision(self,i):
        if self.piece[i].x < 0 or self.piece[i].x > (GAMEAREA_WIDTH//BLOCKSIZE) - 1:
            return False
        elif (self.piece[i].y > (GAMEAREA_HEIGHT//BLOCKSIZE) - 1
        or self.gameArea[self.piece[i].y][self.piece[i].x]):
            return False
        return True

    #Drop Piece
    def dropPiece(self):
        self.DROPACCELERATION = 20

    #Forces piece to drop faster for training/graph generating purposes
    def dropPieceInstantly(self):
        self.DROPACCELERATION = 1000

    #Reset drop speed
    def resetDropSpeed(self):
        self.DROPACCELERATION = 1

    #Move piece left
    def moveLeft(self):
        old_piece = deepcopy(self.piece)
        for i in range(4):
            self.piece[i].x -= 1
            if not self.checkCollision(i):
                self.piece = deepcopy(old_piece)
                break

    #Move piece right
    def moveRight(self):
        old_piece = deepcopy(self.piece)
        for i in range(4):
            self.piece[i].x += 1
            if not self.checkCollision(i):
                self.piece = deepcopy(old_piece)
                break

    #Rotate piece Clockwise
    def rotatePieceClockwise(self):

        if(self.pieceRotation < 270):
            self.pieceRotation += 90
        else:
            self.pieceRotation = 0

        center = self.piece[1]
        old_piece = deepcopy(self.piece)
        for i in range(4):
            x = self.piece[i].y - center.y
            y = self.piece[i].x - center.x
            self.piece[i].x = center.x - x
            self.piece[i].y = center.y + y
            if not self.checkCollision(i):
                self.piece = deepcopy(old_piece)
                if(self.pieceRotation == 0):
                    self.pieceRotation = 270
                else:
                    self.pieceRotation -= 90
                break

    #Play Action
    def playAction(self, action):
        
        rotation = action[0]
        move = action[1]

        timesToRotate = 0
        if(rotation > 0):
            timesToRotate = rotation / 90

        for i in range((int(timesToRotate))):
            center = self.piece[1]
            for ii in range(4):
                x = self.piece[ii].y - center.y
                y = self.piece[ii].x - center.x
                self.piece[ii].x = center.x - x
                self.piece[ii].y = center.y + y
        
        toMoveRight = 0
        toMoveLeft = 0
        if(move > 0):
            toMoveRight = move
        elif(move < 0):
            toMoveLeft = np.abs(move)

        if(toMoveRight > 0):
            for i in range(toMoveRight):
                for ii in range(4):
                    self.piece[ii].x += 1
        elif(toMoveLeft > 0):
            for i in range(toMoveLeft):
                for ii in range(4):
                    self.piece[ii].x -= 1

        self.actionComplete = True
   
    #Check for line completions, add to score
    def checkLines(self):
        self.lineclear = 0
        lastLine = (GAMEAREA_HEIGHT//BLOCKSIZE) - 1

        for row in range((GAMEAREA_HEIGHT//BLOCKSIZE)-1, -1, -1):
            count = 0
            for i in range(GAMEAREA_WIDTH//BLOCKSIZE):
                if self.gameArea[row][i]:
                    count += 1
                self.gameArea[lastLine][i] = self.gameArea[row][i]
            if count < (GAMEAREA_WIDTH//BLOCKSIZE):
                lastLine -= 1
            else:
                self.DIFFICULTY += 0.01
                self.lineclear += 1
                self.totalLinescleared += 1

        #Add to score
        self.score += self.scores[self.lineclear]

    #Check if game has ended
    def checkGameEnd(self, gameArea):
        for y, row in enumerate(gameArea):
            for x, value in enumerate(row):
                if gameArea[0][x] == 1:
                    return True
        return False

    #Reset Game
    def reset(self):
        #Reset everything
        #Reset game area
        for y, row in enumerate(self.gameArea):
            for x, value in enumerate(row):
                self.gameArea[y][x] = 0
        #Reset Score
        self.score = 0
        self.totalLinescleared = 0
        self.totalPiecesUsed = 0
        self.efficiency = 0
        #Reset Difficulty
        self.DIFFICULTY = 1
        #Reset piece & next_piece
        self.piece = deepcopy(choice(self.pieces))
        self.next_piece = deepcopy(choice(self.pieces))
        self.pieceLanded = False
        self.actionComplete = False
        self.newPiece = True
        return self.getStateValues(self.gameArea)

    #Count holes
    def countHoles(self, gameArea):
        totalHoles = 0
        #Using gamearea array, store columns 
        #instead of rows in a seperate array
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
                    totalHoles += 1
                        
        return totalHoles    
        
    #Count Sum of differences of adjacent column heights
    def countSumDiffAdjHeights(self, gameArea):
        totalDiff = 0

        #Using gamearea array, store columns 
        #instead of rows in a seperate array
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
   
    #Count total height
    def countTotalHeight(self, gameArea):
        totalHeight = 0
        #Using gamearea array, store columns 
        #instead of rows in a seperate array
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
        for column, height in enumerate(columnHeights):
            totalHeight += height

        return totalHeight
   
    #Count lines cleared
    def countLinesCleared(self, gameArea):
        linescleared = 0
        for y, row in enumerate(gameArea):
            blocksFilled = 0
            for x, value in enumerate(row):
                if value == 1:
                    blocksFilled += 1
                if blocksFilled == 10:
                    linescleared += 1
        return linescleared

    #Return reward
    def getReward(self):
                
        reward = 1 
        match self.lineclear:
            case 0:
                reward = 1
            case 1:
                reward = 40
            case 2:
                reward = 100
            case 3:
                reward = 300
            case 4: 
                reward = 1200
        done = self.checkGameEnd(self.gameArea)
        if(done):
            reward = -10

        return reward, done
        
    #Return state values
    def getStateValues(self, gameArea):
        holes = self.countHoles(gameArea)
        bumpiness = self.countSumDiffAdjHeights(gameArea)
        totalHeight = self.countTotalHeight(gameArea)
        linesCleared = self.countLinesCleared(gameArea)

        return torch.FloatTensor([holes,bumpiness,totalHeight, linesCleared])

    #Return next states
    def getNextStates(self, gameArea, piece):
        nextStates = {}

        pieceRotations = [0, 90, 180, 270] #4 Rotations
        pieceMoves = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5] #11 Moves
        actions = [] #44 Possible Rotations*Moves
        for rot in range(len(pieceRotations)):
            for move in range(len(pieceMoves)):
                actions.append((pieceRotations[rot],pieceMoves[move]))

        for action in actions:
            gamearea_copy = deepcopy(gameArea)  
            piece_copy = deepcopy(piece) 
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
                    for h in range(GAMEAREA_HEIGHT//BLOCKSIZE):
                        for j in range(4):
                            piece_copy[j].y += 1
                        
                        for ii in range(4):
                            for jj in range(GAMEAREA_HEIGHT//BLOCKSIZE):
                                #If piece_copy goes below the bottom of gamearea, 
                                #bring it back into the gamearea
                                if(piece_copy[ii].y > GAMEAREA_HEIGHT//BLOCKSIZE - 1):
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
                    nextStates[(rotation,move)] = self.getStateValues(gamearea_copy)

        return nextStates

    #Update
    def update(self):
        #Controls
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        #Draw game area
        self.drawGamearea()
        #Draw Text objects
        self.drawTextObjects()
        #Draw current piece
        self.drawPiece()
        #Draw next piece
        self.drawNextPiece()

        #Drop pieces according to DIFFICULTY
        self.DROPTIMER += self.DIFFICULTY * self.DROPACCELERATION
        old_piece = deepcopy(self.piece)
        if self.DROPTIMER > 69:
            self.DROPTIMER = 0
            for i in range(4):
                self.piece[i].y += 1
                #If collided
                if not self.checkCollision(i):
                    for ii in range(4):
                        self.gameArea[old_piece[ii].y][old_piece[ii].x] = 1
                    self.pieceRotation = 0
                    self.piece = self.next_piece
                    self.pieceid = self.nextpieceid
                    self.nextpieceid = choice(self.piece_ids)
                    self.next_piece = deepcopy(self.pieces[self.nextpieceid])
                    self.score += 1
                    self.totalPiecesUsed += 1
                    self.pieceLanded = True
                    self.actionComplete = False
                    self.newPiece = True
                    self.resetDropSpeed()
                    break

        #Check for line clear
        self.checkLines()

        #Update efficiency score
        if(self.totalLinescleared > 0):
            self.efficiency = round(self.score / (self.totalLinescleared + self.totalPiecesUsed), 2)

        pygame.display.update()
        self.clock.tick(FPS)
