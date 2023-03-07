import pygame

#AIMinoes (Game)
from aiminoes import AIMinoes

#Arthur AI
from arthur_ai import ArthurAI

SCREEN_HEIGHT = 800
SCREEN_WIDTH = 1200
GAMEAREA_HEIGHT = 700
GAMEAREA_WIDTH = 350
FPS = 120
BLOCKSIZE = 35

#Arthur Plays Class
class ArthurPlays:
    def __init__(self):
        self.display = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.quit = False
        self.titleFont = pygame.font.SysFont('freesansbold.ttf', 82)
        self.text_AIMinoes = self.titleFont.render('AIMinoes',True,
                                                    pygame.Color('red'))
        self.text_AIMinoes_Rect = self.text_AIMinoes.get_rect()
        self.text_AIMinoes_Rect.x = 0

        self.text_Arthur = self.titleFont.render('Arthur',True,
                                                    pygame.Color('red'))
        self.text_Arthur_Rect = self.text_Arthur.get_rect()
        self.text_Arthur_Rect.x = 0
        self.text_Arthur_Rect.y = 100

        self.text_Plays = self.titleFont.render('Plays',True,
                                                pygame.Color('red'))
        self.text_Plays_Rect = self.text_Plays.get_rect()
        self.text_Plays_Rect.x = 0
        self.text_Plays_Rect.y = 180

        self.game = AIMinoes()
        self.arthurAI = ArthurAI(None,None)
        self.quit = False

        self.events = []

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
        self.display.blit(self.text_Arthur,self.text_Arthur_Rect)
        self.display.blit(self.text_Plays,self.text_Plays_Rect)

    #Update
    def update(self):
        self.display.fill('grey')
        self.drawTextObjects()


        if(self.game.newPiece == True):
            action = self.arthurAI.bestAction(self.game.gameArea, self.game.piece)
            self.game.newPiece = False

        if(self.game.actionComplete):
            self.game.dropPiece()
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
        if(self.game.checkGameEnd(self.game.gameArea)):
            self.game.reset()

        pygame.display.update()
        self.clock.tick(FPS)

    #Return To Main Menu
    def BackToMenu(self):
        self.quit = True
