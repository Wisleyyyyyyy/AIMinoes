import pygame

#Main Menu
from mainmenu import MainMenu

pygame.init()
#Set window name
pygame.display.set_caption('AIMinoes')

#Main Loop
if __name__ == '__main__':
    mainMenu = MainMenu()

    while mainMenu.quit != True:
        mainMenu.update()