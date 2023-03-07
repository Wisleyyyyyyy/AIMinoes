import pygame

#AIMinoes (Game)
from aiminoes import AIMinoes

SCREEN_HEIGHT = 800
SCREEN_WIDTH = 1200
FPS = 120

#User Plays Class
class UserPlays:
    def __init__(self):
        self.display = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.quit = False
        self.titleFont = pygame.font.SysFont('freesansbold.ttf', 82)
        self.text_AIMinoes = self.titleFont.render('AIMinoes',True,
                                                    pygame.Color('red'))
        self.text_AIMinoes_Rect = self.text_AIMinoes.get_rect()
        self.text_AIMinoes_Rect.x = 0

        self.text_User = self.titleFont.render('User',True,
                                                    pygame.Color('red'))
        self.text_User_Rect = self.text_User.get_rect()
        self.text_User_Rect.x = 0
        self.text_User_Rect.y = 100

        self.text_Plays = self.titleFont.render('Plays',True,
                                                pygame.Color('red'))
        self.text_Plays_Rect = self.text_Plays.get_rect()
        self.text_Plays_Rect.x = 0
        self.text_Plays_Rect.y = 180

        self.game = AIMinoes()

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
        self.display.blit(self.text_User,self.text_User_Rect)
        self.display.blit(self.text_Plays,self.text_Plays_Rect)

    #Update
    def update(self):
        self.display.fill('grey')
        self.drawTextObjects()

        #Controls (User Input)
        for event in list(pygame.event.get()):
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                #Left arrow to move current piece left
                if event.key == pygame.K_LEFT:
                    self.game.moveLeft()
                #Right arrow to move current piece right
                if event.key == pygame.K_RIGHT:
                    self.game.moveRight()
                #Spacebar to drop current piece faster
                if event.key == pygame.K_SPACE:
                    self.game.dropPiece()
                #Up arrow to rotate current piece Clockwise
                if event.key == pygame.K_UP:
                    self.game.rotatePieceClockwise()

            elif event.type == pygame.KEYUP:
                #On spacebar release, reset drop speed
                if event.key == pygame.K_SPACE:
                    self.game.resetDropSpeed()

        #Back to Menu button
        self.button("Back to Menu",900,700,200,50,'black','pink',self.BackToMenu)
        
        self.game.update()
        if(self.game.checkGameEnd(self.game.gameArea)):
            self.game.resetDropSpeed()
            self.game.reset()

        pygame.display.update()
        self.clock.tick(FPS)

    #Return To Main Menu
    def BackToMenu(self):
        self.quit = True

