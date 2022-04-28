import json, os
import pygame, pgzrun
from new_game import *

#Open json files
flagjson = open("flag.json", "r")
globalSD = json.loads(flagjson.read())
flagjson.close()

saveData = []
for file_name in os.listdir("save"):
    print(file_name)
    save = open("save\\" + file_name, "r")
    saveData.append(json.loads(save.read()))
    save.close()

print(saveData)
pygame.init()
WIDTH = 1024
HEIGHT = 768

font = pygame.font.SysFont(None, 24) #Uses default pygame font

#Colour bank
WHITE = (255, 255, 255)
MAIN_PRIMARY = (21, 35, 56)
MAIN_SECONDARY = (218, 224, 232)

current_screen = "main_menu"
current_colour = (194, 212, 242)

class button():
    """
    Represents a clickable button

    Attributes
    ----------
    coord (list of int): coordinate location of the button
    dim (list of int): dimensions of the button
    c_active (tuple of int): active colour of button (changes depending on if the button is being hovered over)
    main (tuple of int): main colour of button
    bg (tuple of int): background colour of button
    text (font object): font object for displaying the button's text
    rect (Rect object): Rect object of the button, used for collision detection
    surf (Surface object): surface object on which the button is drawn
    hovering (bool): whether the button is hovered over
    dest (str): name of the button's destination

    Methods
    -------
    show(self): Draws the button onto the screen via its surface
    animate(self, mouse_pos): Determines how the button appears, depending on if it is hovered over or clicked
    press(self): Carries out what happens when the button is clicked
    """

    def __init__(self, coordinates, dimensions, main_colour, bg_colour, text, destination):
        self.coord = coordinates
        self.dim = dimensions

        self.c_active = (0, 0, 0)
        self.main = main_colour
        self.bg = bg_colour

        self.text = font.render(text, True, WHITE)
        self.rect = Rect((self.coord[0], self.coord[1]), (self.dim[0], self.dim[1]))
        self.surf = pygame.Surface((self.dim[0], self.dim[1]))
        self.hovering = False
        self.dest = destination

    def show(self):
        """
        Draws the button onto the screen via its Surface

        Parameters:
            None

        Returns:
            None
        """

        screen.blit(self.surf, (self.coord[0], self.coord[1]))

    def animate(self, mouse_pos):
        """
        Determines how the button appears, depending on if it is hovered over or clicked

        Parameters:
            mouse_pos (tuple of int): the coordinates of the mouse locations

        Returns:
            None
        """

        #Checks if the mouse is hovering over the button
        self.hovering = self.rect.collidepoint(mouse_pos)

        #Chooses what colour the button will take
        if self.hovering:
            self.c_active = self.bg
        else:
            self.c_active = self.main

        self.surf.fill(self.c_active)

        #Finds the dimensions of the text to then be able to center it
        textx, texty = self.text.get_size()
        self.surf.blit(self.text, ((self.dim[0] - textx)/2, (self.dim[1] - texty)/2))

    def press(self, screen):
        """
        Carries out what happens when the button is clicked

        Parameters:
            screen (str): the current active screen being displayed

        Returns:
            screen (str): the new screen to begin displaying"""
        screen = self.dest
        return screen

class Therese(pygame.sprite.sprite):
    def __init__(self, image, width, height):
        pygame.sprite.Sprite.__init__(self)

        self.image


new_game_button = button((650, 200), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "New Game", "new_game")
cont_game_button = button((650, 300), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Continue Game", "cont_game")
settings_button = button((650, 400), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Settings", "settings")
quit_button = button((650, 500), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Quit", "quit")

back_button = button((422, 700), (180, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Back", "main_menu")

def on_mouse_down(button, pos):
    print(repr(button))
    global current_screen

    if current_screen == "main_menu":
        for i in [new_game_button, cont_game_button, settings_button, quit_button]:
            if i.hovering:
                current_screen = i.press(current_screen)
                break
    elif current_screen == "new_game":
        print("new game called")
    elif current_screen == "cont_game":
        print("cont_game called")
        for i in [back_button]:
            if i.hovering:
                current_screen = i.press(current_screen)
    elif current_screen == "settings":
        print("settings called")
        for i in [back_button]:
            if i.hovering:
                current_screen = i.press(current_screen)
    if current_screen == "quit":
        clock.schedule(quitting, 1.0)

def on_key_down(key):
    print(repr(key))
    if key == keys.ESCAPE:
        pygame.display.quit()

def main_menu(mouse_pos, screen):
    new_game_button.animate(mouse_pos)
    cont_game_button.animate(mouse_pos)
    settings_button.animate(mouse_pos)
    quit_button.animate(mouse_pos)

def main_menu_draw():
    new_game_button.show()
    cont_game_button.show()
    settings_button.show()
    quit_button.show()

    return (194, 212, 242) #Bluish shade

def cont_game(mouse_pos, screen):
    back_button.animate(mouse_pos)

def cont_game_draw():
    back_button.show()

    return (199, 177, 143) #Wood brown

def settings(mouse_pos, screen):
    back_button.animate(mouse_pos)

def settings_draw():
    back_button.show()

    return (143, 102, 79) #Earth brown

def close_game(mouse_pos, screen):
    pass

def close_game_draw():
    error_message = font.render("Haha lol", True, WHITE)
    x, y = error_message.get_size()
    screen.blit(error_message, ((WIDTH - x)/2, (HEIGHT - y)/2))

    return (194, 212, 242)

def quitting():
    pygame.display.quit()

def bob():
    pass

update_dict = {
    "main_menu": main_menu,
    "new_game": new_game,
    "cont_game": cont_game,
    "settings": settings,
    "quit": close_game
}

draw_dict = {
    "main_menu": main_menu_draw,
    "new_game": new_game_draw,
    "cont_game": cont_game_draw,
    "settings": settings_draw,
    "quit": close_game_draw
}

def update():
    mouse_pos = pygame.mouse.get_pos()

    update_dict[current_screen](mouse_pos, current_screen)

def draw():
    global current_screen
    global current_colour

    screen.fill(current_colour)
    current_colour = draw_dict[current_screen]()

pgzrun.go()
