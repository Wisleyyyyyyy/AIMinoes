import pygame

import torch
import torch.nn as nn

import os

#AIMinoes (Game)
from aiminoes import AIMinoes

SCREEN_HEIGHT = 800
SCREEN_WIDTH = 1200
FPS = 120

#Tommy Plays Class
class TommyPlays:
    def __init__(self):
        self.display = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.quit = False
        self.titleFont = pygame.font.SysFont('freesansbold.ttf', 82)
        self.text_AIMinoes = self.titleFont.render('AIMinoes',True,
                                                    pygame.Color('red'))
        self.text_AIMinoes_Rect = self.text_AIMinoes.get_rect()
        self.text_AIMinoes_Rect.x = 0

        self.text_Tommy = self.titleFont.render('Tommy',True,
                                                pygame.Color('red'))
        self.text_Tommy_Rect = self.text_Tommy.get_rect()
        self.text_Tommy_Rect.x = 0
        self.text_Tommy_Rect.y = 100

        self.text_Plays = self.titleFont.render('Plays',True,
                                                pygame.Color('red'))
        self.text_Plays_Rect = self.text_Plays.get_rect()
        self.text_Plays_Rect.x = 0
        self.text_Plays_Rect.y = 180

        self.game = AIMinoes()
        self.quit = False

        #Load most trained model
        self.epoch = 0
        self.model = None
        while True:
            self.epoch += 100
            if(os.path.exists("{}/Tommy_{}".format("models", self.epoch))):
                self.model = torch.load("{}/Tommy_{}".format("models", self.epoch), 
                                        map_location=lambda storage, loc: storage)
            else:
                self.epoch -= 100
                break  


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
        self.display.blit(self.text_Tommy,self.text_Tommy_Rect)
        self.display.blit(self.text_Plays,self.text_Plays_Rect)

        self.textFont = pygame.font.SysFont('freesansbold.ttf', 46)
        self.text_ModelLoaded = self.textFont.render('Model (Training Iterations): ' + "{}".format(self.epoch), True, pygame.Color('red'))
        self.text_ModelLoaded_Rect = self.text_ModelLoaded.get_rect()
        self.text_ModelLoaded_Rect.x = 0
        self.text_ModelLoaded_Rect.y = SCREEN_HEIGHT//2 + 300

        self.display.blit(self.text_ModelLoaded,self.text_ModelLoaded_Rect)


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
    
    def play(self):
        torch.manual_seed(69)

        self.model.eval()

        self.update()  
        if(self.game.newPiece == True):
            nextSteps = self.game.getNextStates(self.game.gameArea,self.game.piece)
            
            nextActions, nextStates = zip(*nextSteps.items())
            nextStates = torch.stack(nextStates)
            predictions = self.model(nextStates)[:, 0]
            index = torch.argmax(predictions).item()

            action = nextActions[index]
            
            self.game.newPiece = False

        if(self.game.actionComplete):
            self.game.dropPiece()
        else:
            self.game.playAction(action)

        done = None

        if(self.game.pieceLanded):
            _, done = self.game.getReward()
            self.game.pieceLanded = False

        if done:
            self.game.reset()
        


    #Return To Main Menu
    def BackToMenu(self):
        self.quit = True

