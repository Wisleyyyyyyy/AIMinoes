import pygame

import numpy as np

import matplotlib.pyplot
matplotlib.use("Agg")

import matplotlib.backends.backend_agg as agg

from matplotlib.ticker import MaxNLocator

import pylab

#AIMinoes (Game)
from aiminoes import AIMinoes

#Arthur AI
from arthur_ai import ArthurAI

SCREEN_HEIGHT = 800
SCREEN_WIDTH = 1200
FPS = 120

#Arthur Graph Class
class ArthurGraph:
    def __init__(self):
        self.display = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.quit = False
        self.titleFont = pygame.font.SysFont('freesansbold.ttf', 82)
        self.text_AIMinoes = self.titleFont.render('AIMinoes',True,
                                                    pygame.Color('red'))
        self.text_AIMinoes_Rect = self.text_AIMinoes.get_rect()
        self.text_AIMinoes_Rect.x = 0

        self.descFont = pygame.font.SysFont('freesansbold.ttf', 60)
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

        self.text_Graph = self.descFont.render('Graph (Arthur)',True,
                                                pygame.Color('red'))
        self.text_Graph_Rect = self.text_Graph.get_rect()
        self.text_Graph_Rect.x = 0
        self.text_Graph_Rect.y = 260

        self.game = AIMinoes()
        self.arthurAI = ArthurAI(None,None)
        self.quit = False

        self.events = []

        self.numGames = 0

        #Performance Graph
        self.plotNumGames = []
        self.plotEfficiency = []

        self.fig = pylab.figure(figsize=[6, 6],
                   dpi=70,
                   )
        self.ax = self.fig.gca()
        self.ax.set_title('Performance Graph (Arthur)')
        self.ax.set_xlabel('Game')
        self.ax.set_ylabel('Efficiency')
        
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

        if(self.game.newPiece == True):
            action = self.arthurAI.bestAction(self.game.gameArea, self.game.piece)
            self.game.newPiece = False

        if(self.game.actionComplete):
            self.game.dropPieceInstantly()
        else:
            self.game.playAction(action)


        #Manual Quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        #Back to Menu button
        self.button("Back to Menu",900,700,200,50,'black','pink',self.BackToMenu)

        self.game.update()
        if(self.game.checkGameEnd(self.game.gameArea) or self.game.totalLinescleared >= 100 \
           and self.numGames <= 50):
            #Close previous graph
            matplotlib.pyplot.close()
            self.numGames += 1
            
            #Update Values
            self.plotNumGames.append(self.numGames)
            self.plotEfficiency.append(self.game.efficiency)

            #Reset Game
            self.game.reset()

            #Update Performance Graph 
            self.fig = pylab.figure(figsize=[6, 6],
                   dpi=70,
                   )
            self.ax = self.fig.gca()
            self.ax.set_title('Performance Graph (Arthur)')
            self.ax.set_xlabel('Game')
            self.ax.set_ylabel('Efficiency')
            self.ax.xaxis.set_major_locator(MaxNLocator(integer=True))

            self.ax.plot(self.plotNumGames,self.plotEfficiency, label='Efficiency',color='red')
            #Plot Average Efficieny 
            averageEfficiency = [np.mean(self.plotEfficiency)]*len(self.plotNumGames)
            self.ax.plot(self.plotNumGames,averageEfficiency, 
                         label='Average Efficiency = {}'.format(round(np.mean(self.plotEfficiency),2)),
                         linestyle='--', linewidth=3, color="green")
            #Legend
            legend = self.ax.legend(loc='upper right', facecolor='grey', framealpha=1)

            self.canvas = agg.FigureCanvasAgg(self.fig)
            self.canvas.draw()
            self.renderer = self.canvas.get_renderer()
            self.raw_data = self.renderer.tostring_rgb()
            self.graph = pygame.image.fromstring(self.raw_data, self.canvas.get_width_height(), "RGB")

        #Save graph when 50 Games have been completed by Arthur
        if(self.numGames == 50 and self.genComplete == False):
            #Save Graph
            self.fig.savefig('graphs/Arthur_PerformanceGraph.png')
            #Graph Generation Complete
            self.genComplete = True

        
        pygame.display.update()
        self.clock.tick(FPS)

    #Return To Main Menu
    def BackToMenu(self):
        self.quit = True
