import pygame

import torch
import torch.nn as nn

import os
import numpy as np

import matplotlib.pyplot
matplotlib.use("Agg")

import matplotlib.backends.backend_agg as agg

from matplotlib.ticker import MaxNLocator

import pylab

#AIMinoes (Game)
from aiminoes import AIMinoes

SCREEN_HEIGHT = 800
SCREEN_WIDTH = 1200
FPS = 120

#Tommy Graph Class
class TommyGraph:
    def __init__(self):
        self.display = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.quit = False
        self.titleFont = pygame.font.SysFont('freesansbold.ttf', 82)
        self.text_AIMinoes = self.titleFont.render('AIMinoes',True,
                                                    pygame.Color('red'))
        self.text_AIMinoes_Rect = self.text_AIMinoes.get_rect()
        self.text_AIMinoes_Rect.x = 0

        self.descFont = pygame.font.SysFont('freesansbold.ttf', 50)
        self.text_Generate = self.descFont.render('Generate',True,
                                             pygame.Color('red'))
        self.text_Generate_Rect = self.text_Generate.get_rect()
        self.text_Generate_Rect.x = 0
        self.text_Generate_Rect.y = 100

        self.text_Performance = self.descFont.render('Performance',True,
                                                pygame.Color('red'))
        self.text_Performance_Rect = self.text_Performance.get_rect()
        self.text_Performance_Rect.x = 0
        self.text_Performance_Rect.y = 180

        self.text_Graph = self.descFont.render('Graph (Tommy)',True,
                                                pygame.Color('red'))
        self.text_Graph_Rect = self.text_Graph.get_rect()
        self.text_Graph_Rect.x = 0
        self.text_Graph_Rect.y = 260

        self.game = AIMinoes()
        self.quit = False

        self.modelNumGames = 0

        #Load and start with least trained model
        self.epoch = 100
        self.model = None
        if(os.path.exists("{}/Tommy_{}".format("models", self.epoch))):
            self.model = torch.load("{}/Tommy_{}".format("models", self.epoch), map_location=lambda storage, loc: storage)
        self.modelEfficiencies = []

        #Performance Graph    
        self.plotTrainingsModelReceived = []
        self.plotAverageEfficiency = []

        self.fig = pylab.figure(figsize=[6, 6],
                   dpi=70,
                   )
        self.ax = self.fig.gca()
        self.ax.set_title('Performance Graph (Tommy)')
        self.ax.set_xlabel('Model (Training Iterations)')
        self.ax.set_ylabel('Average Efficiency')
        
        self.ax.set_yticklabels([])
        self.ax.set_xticklabels([])

        self.canvas = agg.FigureCanvasAgg(self.fig)
        self.canvas.draw()
        self.renderer = self.canvas.get_renderer()
        self.raw_data = self.renderer.tostring_rgb()
        self.graph = pygame.image.fromstring(self.raw_data, self.canvas.get_width_height(), "RGB")
        
        self.genComplete = False

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
        self.display.blit(self.text_Generate,self.text_Generate_Rect)
        self.display.blit(self.text_Performance,self.text_Performance_Rect)
        self.display.blit(self.text_Graph,self.text_Graph_Rect)

        
        self.descSmallFont = pygame.font.SysFont('freesansbold.ttf', 35)
        self.text_Trainings = self.descSmallFont.render('Model (Training Iterations): {}'.format(self.epoch),True,
                                             pygame.Color('red'))
        self.text_Trainings_Rect = self.text_Trainings.get_rect()
        self.text_Trainings_Rect.x = 420
        self.text_Trainings_Rect.y = 720

        self.text_NumGames = self.descSmallFont.render('Games: {}'.format(self.modelNumGames),True,
                                             pygame.Color('red'))
        self.text_NumGames_Rect = self.text_NumGames.get_rect()
        self.text_NumGames_Rect.x = 420
        self.text_NumGames_Rect.y = 750
        self.display.blit(self.text_Trainings,self.text_Trainings_Rect)
        self.display.blit(self.text_NumGames,self.text_NumGames_Rect)

    #Draw Performance Graph
    def drawPerformanceGraph(self):
        self.display.blit(self.graph,(0,360))

    #Draw Graph Generation complete prompt
    def drawGenComplete(self):
        self.promptFont = pygame.font.SysFont('freesansbold.ttf', 20)
        self.text_GenComplete = self.promptFont.render('Graph Generation Complete',True,
                                                    pygame.Color('red'))
        self.text_GenComplete_Rect = self.text_GenComplete.get_rect()
        self.text_GenComplete_Rect.x = 80
        self.text_GenComplete_Rect.y = 360

        self.display.blit(self.text_GenComplete,self.text_GenComplete_Rect)

    #Update
    def update(self):
        self.display.fill('grey')
        self.drawTextObjects()
        self.drawPerformanceGraph()

        if(self.genComplete):
            #Display graph generation complete prompt
            self.drawGenComplete()

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
            self.game.dropPieceInstantly()
        else:
            self.game.playAction(action)

        done = None

        if(self.game.pieceLanded):
            _, done = self.game.getReward()
            self.game.pieceLanded = False

        if (done or self.game.totalLinescleared >= 100):

            self.modelNumGames += 1
            self.modelEfficiencies.append(self.game.efficiency)
            
            self.game.reset()

            
        #Each trained model will run for 50 games before moving on to the next trained model
        #The results will then be averaged and plotted onto a graph
        #After every trained model has run for 50 games each, the graph will be saved
        if(self.modelNumGames == 50 and self.genComplete == False):
            #Close previous graph
            matplotlib.pyplot.close()
            #Update Values
            self.plotTrainingsModelReceived.append(self.epoch)
            self.plotAverageEfficiency.append(np.mean(self.modelEfficiencies))
            #Update Performance Graph 
            self.fig = pylab.figure(figsize=[6, 6],
                   dpi=70,
                   )
            self.ax = self.fig.gca()
            self.ax.set_title('Performance Graph (Tommy)')
            self.ax.set_xlabel('Model (Training Iterations)')
            self.ax.set_ylabel('Average Efficiency')
            self.ax.xaxis.set_major_locator(MaxNLocator(integer=True))

            self.ax.plot(self.plotTrainingsModelReceived,self.plotAverageEfficiency, 
                         label='Average Efficiency',color='red')
            #Legend
            legend = self.ax.legend(loc='upper right', facecolor='grey', framealpha=1)

            self.canvas = agg.FigureCanvasAgg(self.fig)
            self.canvas.draw()
            self.renderer = self.canvas.get_renderer()
            self.raw_data = self.renderer.tostring_rgb()
            self.graph = pygame.image.fromstring(self.raw_data, self.canvas.get_width_height(), 
                                                 "RGB")

            #Write data to text file
            with open('graphs/Tommy_PerformanceData.txt','a') as f:
                f.write('Model (Training Iterations): {}, Average Efficiency: {}'.format(self.epoch,
                                                          round(np.mean(self.modelEfficiencies)),2))
                f.write('\n')
            f.close()

            #Reset values
            self.modelNumGames = 0
            self.modelEfficiencies = []

            #Move on to next model
            self.epoch += 100
            if(os.path.exists("{}/Tommy_{}".format("models", self.epoch))):
                self.model = torch.load("{}/Tommy_{}".format("models", self.epoch), 
                                        map_location=lambda storage, loc: storage)
            else:
                self.epoch -= 100
                #Save Graph
                self.fig.savefig('graphs/Tommy_PerformanceGraph.png')
                #Graph Generation Complete
                self.genComplete = True


    #Return To Main Menu
    def BackToMenu(self):
        self.quit = True


