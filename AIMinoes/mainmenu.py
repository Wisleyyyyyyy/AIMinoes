import pygame

#User Plays
from user_plays import UserPlays

#Arthur Plays
from arthur_plays import ArthurPlays

#Arthur Graph
from arthur_graph import ArthurGraph

#Tommy Trains
from tommy_trains import TommyTrains

#Tommy Plays
from tommy_plays import TommyPlays

#Tommy Graph
from tommy_graph import TommyGraph

SCREEN_HEIGHT = 800
SCREEN_WIDTH = 1200
FPS = 60

#Mainmenu class
class MainMenu:

    def __init__(self):
        self.display = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.quit = False
        self.largeText = pygame.font.SysFont('freesansbold.ttf', 82)
        self.TextSurf =  self.largeText.render('AIMinoes',True,
                                                pygame.Color('red'))
        self.TextRect = self.TextSurf.get_rect()
        self.TextRect.center = ((SCREEN_WIDTH/2),(50))

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

    #Update
    def update(self):
        self.display.fill('grey')
        
        self.display.blit(self.TextSurf, self.TextRect)
        
        #User manual play
        self.button("Play Game!",400,100,400,50,'black','pink',self.PlayGame)
        #Arthur
        self.button("Arthur Plays!",400,180,400,50,'black','pink',self.ArthurPlays)
        self.button("Generate Performance Graph (Arthur)",400,260,400,50,'black','pink',self.ArthurGraph)
        #Tommy
        self.button("Train Tommy",400,340,400,50,'black','pink',self.TrainTommy)
        self.button("Tommy Plays!",400,420,400,50,'black','pink',self.TommyPlays)
        self.button("Generate Performance Graph (Tommy)",400,500,400,50,'black','pink',self.TommyGraph)
        #Quit
        self.button("Quit",400,600,400,50,'black','pink',self.Quit)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        pygame.display.update()
        self.clock.tick(FPS)

    #Play Game Manually (No AI)
    def PlayGame(self):
        manualPlay = UserPlays()
        while manualPlay.quit != True:
            manualPlay.update()

    #Arthur Plays (Basic Rule Based AI)
    def ArthurPlays(self):
        arthurPlays = ArthurPlays()
        while arthurPlays.quit != True:
            arthurPlays.update()

    #Generate Performance Graph (Arthur)
    def ArthurGraph(self):
        arthurGraph = ArthurGraph()
        while arthurGraph.quit != True:
            arthurGraph.update()

    #Train Tommy
    def TrainTommy(self):
        tommyTrains = TommyTrains()
        while tommyTrains.quit != True:
            tommyTrains.train()

    #Tommy Plays
    def TommyPlays(self):
        tommyPlays = TommyPlays()
        while tommyPlays.quit != True:
            tommyPlays.play()

    #Generate Performance Graph (Tommy)
    def TommyGraph(self):
        tommyGraph = TommyGraph()
        while tommyGraph.quit != True:
            tommyGraph.play()

    #Quit
    def Quit(self):
        self.quit = True
