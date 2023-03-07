import pygame

import torch
import torch.nn as nn

from random import random, randint, sample
import numpy as np
from collections import deque
from model import DQN

import os
import shutil

#AIMinoes (Game)
from aiminoes import AIMinoes

SCREEN_HEIGHT = 800
SCREEN_WIDTH = 1200
FPS = 120

LEARNINGRATE = 0.001
MEMORYSIZE = 30000
NUM_EPOCH = 3000
EPSILON_START = 1
EPSILON_END = 0.003
EPSILON_DECAY = 2000
BATCHSIZE = 512
GAMMA = 0.99

#Tommy Trains Class
class TommyTrains:
    def __init__(self):
        self.display = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.quit = False
        self.titleFont = pygame.font.SysFont('freesansbold.ttf', 82)
        self.text_AIMinoes = self.titleFont.render('AIMinoes',True,
                                                    pygame.Color('red'))
        self.text_AIMinoes_Rect = self.text_AIMinoes.get_rect()
        self.text_AIMinoes_Rect.x = 0

        self.text_Training = self.titleFont.render('Training',True,
                                                pygame.Color('red'))
        self.text_Training_Rect = self.text_Training.get_rect()
        self.text_Training_Rect.x = 0
        self.text_Training_Rect.y = 100

        self.text_Tommy = self.titleFont.render('Tommy',True,
                                                pygame.Color('red'))
        self.text_Tommy_Rect = self.text_Tommy.get_rect()
        self.text_Tommy_Rect.x = 0
        self.text_Tommy_Rect.y = 180

        self.model = DQN()
        self.game = AIMinoes()
        self.quit = False

        self.numGames = 0

    #Buttons
    def button(self,msg,x,y,w,h,ic,ac,action=None):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if x+w > mouse[0] > x and y+h > mouse[1] > y:
            pygame.draw.rect(self.display, ac,(x,y,w,h))

            if click[0] == 1 and action != None:
                action()         
        else:
            pygame.draw.rect(self.display, ic,(x,y,w,h))

        smallText = pygame.font.SysFont('freesansbold.ttf', 30)
        textSurf = smallText.render(msg,True,pygame.Color('red'))
        textRect = textSurf.get_rect()
        textRect.center = ( (x+(w/2)), (y+(h/2)) )
        self.display.blit(textSurf, textRect)

    #Draw Text objects
    def drawTextObjects(self):
        self.display.blit(self.text_AIMinoes,self.text_AIMinoes_Rect)
        self.display.blit(self.text_Training,self.text_Training_Rect)
        self.display.blit(self.text_Tommy,self.text_Tommy_Rect)
        

        self.textFont = pygame.font.SysFont('freesansbold.ttf', 46)
        self.text_Games = self.textFont.render('Games: ' + str(self.numGames), True, pygame.Color('red'))
        self.text_Games_Rect = self.text_Games.get_rect()
        self.text_Games_Rect.x = 0
        self.text_Games_Rect.y = SCREEN_HEIGHT//2 + 100

        self.display.blit(self.text_Games,self.text_Games_Rect)

    #Update
    def update(self):
        self.display.fill('grey')
        self.drawTextObjects()
        #Manual Quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        #Back to Menu button
        self.button("Back to Menu",900,700,200,50,'black','pink',self.BackToMenu)

        self.game.update()

        pygame.display.update()
        self.clock.tick(FPS)
    
    def train(self):
        torch.manual_seed(69)

        optim = torch.optim.Adam(self.model.parameters(), lr=LEARNINGRATE)
        criterion = nn.MSELoss()

        state = self.game.reset()

        replayMemory = deque(maxlen=MEMORYSIZE)
        epoch = 0

        while epoch < NUM_EPOCH and self.quit == False:
            self.update()   
            if(self.game.newPiece == True):
                nextSteps = self.game.getNextStates(self.game.gameArea,self.game.piece)
                # Exploration or exploitation
                epsilon = EPSILON_END + (max(EPSILON_DECAY - epoch, 0) * (
                        EPSILON_START - EPSILON_END) / EPSILON_DECAY)

                r = random()
                randomAction = r <= epsilon
                nextActions, nextStates = zip(*nextSteps.items())
                nextStates = torch.stack(nextStates)
                self.model.eval()
                with torch.no_grad():
                    predictions = self.model(nextStates)[:, 0]
                self.model.train()
                if randomAction:
                    index = randint(0, len(nextSteps) - 1)
                else:
                    index = torch.argmax(predictions).item()

                nextState = nextStates[index, :]
                action = nextActions[index]
                
                self.game.newPiece = False

            if(self.game.actionComplete):
                self.game.dropPieceInstantly()
            else:
                self.game.playAction(action)

            reward, done = None, None

            if(self.game.pieceLanded):
                reward, done = self.game.getReward()
                replayMemory.append([state, reward, nextState, done])
                self.game.pieceLanded = False

            if done:
                finalScore = self.game.score
                state = self.game.reset()
                self.numGames += 1
            else:
                state = nextState
                continue
            if len(replayMemory) < MEMORYSIZE / 10:
                continue
            epoch += 1
            batch = sample(replayMemory, min(len(replayMemory), BATCHSIZE))
            stateBatch, rewardBatch, nextStateBatch, doneBatch = zip(*batch)
            stateBatch = torch.stack(tuple(state for state in stateBatch))
            rewardBatch = torch.from_numpy(np.array(rewardBatch, dtype=np.float32)[:, None])
            nextStateBatch = torch.stack(tuple(state for state in nextStateBatch))

            qValues = self.model(stateBatch)
            self.model.eval()
            with torch.no_grad():
                nextPredictionBatch = self.model(nextStateBatch)
            self.model.train()

            yBatch = torch.cat(
            tuple(reward if done else reward + GAMMA * prediction for reward, done, prediction in
                zip(rewardBatch, doneBatch, nextPredictionBatch)))[:, None]


            optim.zero_grad()
            loss = criterion(qValues, yBatch)
            loss.backward()
            optim.step()

            print("Epoch: {}, Epsilon: {}, Score: {}, ReplayMemory: {}".format(
            epoch,
            epsilon,
            finalScore,
            len(replayMemory)))

            #Save model every 100th iteration of training
            if epoch > 0 and epoch % 100 == 0:
                torch.save(self.model, "{}/Tommy_{}".format("models", epoch))


    #Return To Main Menu
    def BackToMenu(self):
        self.quit = True
 
