import json, os
import pygame, pgzrun

#Open json files
loljson = open("why.json", "r")
saveData = json.loads(loljson.read())
loljson.close()

WIDTH = 1024
HEIGHT = 768

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
    draw (Rect object): Rect object of the button for pgzero to parse and dispaly
    hovering (bool): whether the button is hovered over

    Methods
    -------
    animate(self, mouse_pos): Determines how the button appears, depending on if it is hovered over or clicked
    """

    def __init__(self, coordinates, dimensions, main_colour, bg_colour):
        self.coord = coordinates
        self.dim = dimensions

        self.c_active = (0, 0, 0)
        self.main = main_colour
        self.bg = bg_colour

        self.draw = Rect((self.coord[0], self.coord[1]), (self.dim[0], self.dim[1]))
        self.hovering = False

    def animate(self, mouse_pos):
        """
        Determines how the button appears, depending on if it is hovered over or clicked

        Parameters:
            mouse_pos (tuple of int): the coordinates of the mouse locations

        Returns:
            none
        """
        #Checks if the mouse is hovering over the button
        self.hovering = self.draw.collidepoint(mouse_pos)

        #Chooses what colour the button will take
        if self.hovering:
            self.c_active = self.bg
        else:
            self.c_active = self.main

menu_button = button((450, 180), (250, 50), (21, 35, 56), (218, 224, 232))

def draw():
  screen.fill((194, 212, 242))
  screen.draw.rect(menu_button.draw, menu_button.c_active)

def update():
    main_menu()
    new_game()
    cont_game()
    settings()


def on_mouse_down(button, pos):
    print("Mouse button", button, "clicked at", pos)
    if menu_button.hovering:
        print ("Click on menu button")

def on_key_down(key):
    print(repr(key))
    if key == keys.ESCAPE:
        pygame.display.quit()
        print("yes")

def main_menu():
    mouse_pos = pygame.mouse.get_pos()
    menu_button.animate(mouse_pos)

def new_game():
    pass

def cont_game():
    pass

def settings():
    pass

def bob():
    pass


pgzrun.go()
#raise Exception("Lol this will be so evil")
