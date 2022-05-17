import json, os
import pygame
from new_game import *

#Open json files
flagjson = open("flag.json", "r")
persistent_flags = json.loads(flagjson.read())
flagjson.close()

save_data = []
for file_name in os.listdir("save"):
    print(file_name)
    save = open("save\\" + file_name, "r")
    save_data.append(json.loads(save.read()))
    save.close()

pygame.init()
WIDTH = 1024
HEIGHT = 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

#Colour bank
WHITE = (255, 255, 255)
MAIN_PRIMARY = (21, 35, 56)
MAIN_SECONDARY = (218, 224, 232)

font = pygame.font.SysFont(None, 24) #Uses default pygame font

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
        self.rect = pygame.Rect((self.coord[0], self.coord[1]), (self.dim[0], self.dim[1]))
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

class Therese(pygame.sprite.Sprite):
    def __init__(self, image, width, height):
        pygame.sprite.Sprite.__init__(self)

        self.image

def on_mouse_down(quitting, current_screen, button_list, button_call, button, pos):
    quitting = quitting

    if not(button[0]):
        return quitting, current_screen
    #print(repr(button))

    if current_screen == "quit" and not quitting:
        #Sets a timer for 1 second (1000 ms) to quit the game
        pygame.time.set_timer(pygame.QUIT, 1000, 1)
        quitting = True

    for key in button_call[current_screen]:
        button_list[key].animate(pos)
        if button_list[key].hovering:
            current_screen = button_list[key].press(current_screen)
            break

    return quitting, current_screen

def on_key_down(current_screen, key):
    if key[pygame.K_ESCAPE]:
        pygame.time.set_timer(pygame.QUIT, 10)

    if current_screen == "main_menu":
        pass

def main_menu(mouse_pos, screen, game_state):
    pass

def main_menu_draw():
    return (194, 212, 242) #Bluish shade

def cont_game(mouse_pos, screen, game_state):
    pass

def cont_game_draw():
    return (199, 177, 143) #Wood brown

def settings(mouse_pos, screen, game_state):
    pass

def settings_draw():
    return (143, 102, 79) #Earth brown

def close_game(mouse_pos, screen, game_state):
    pass

def close_game_draw():
    error_message = font.render("Haha lol", True, WHITE)
    x, y = error_message.get_size()
    screen.blit(error_message, ((WIDTH - x)/2, (HEIGHT - y)/2))

    return (10, 10, 10)

def bob():
    pass

#Both dictionaries are for drawing screens
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

def update(current_screen, button_list, button_call):
    mouse_pos = pygame.mouse.get_pos()

    for key in button_call[current_screen]:
        button_list[key].animate(mouse_pos)

def draw(current_screen, current_colour, button_list, button_call):

    screen.fill(current_colour)

    for key in button_call[current_screen]:
        button_list[key].show()

    current_colour = draw_dict[current_screen]()

    return current_colour

def main(flags, saveData):
    """
    Runs the program

    Parameters:
        None

    Returns:
        None
    """

    current_screen = "main_menu"
    current_colour = (194, 212, 242)

    scrollX, scrollY = 0, 0
    quitting = False

    #Stores all the buttons that are present in the game
    button_list = {
        "new_game_button": button((650, 200), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "New Game", "new_game"),
        "cont_game_button": button((650, 300), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Continue Game", "cont_game"),
        "settings_button": button((650, 400), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Settings", "settings"),
        "quit_button": button((650, 500), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Quit", "quit"),
        "back_button": button((422, 700), (180, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Back", "main_menu")
    }

    #Stores the list of buttons to display in each screen
    button_call = {
        "main_menu": ["new_game_button", "cont_game_button", "settings_button", "quit_button"],
        "new_game": [],
        "cont_game": ["back_button"],
        "settings": ["back_button"],
        "quit": []
    }

    #Boilerplate statement for infinite while loop
    running = True

    while running:

        #Caps the framerate at 60 and records how much time has passed since the last frame
        #Cheeky math reference of "delta t," or "change in time"
        dt = clock.tick(60)

        #Handles pygame events
        for event in pygame.event.get():
            #Exits the while loop (and the program as a whole) if the QUIT event is called
            if event.type == pygame.QUIT:
                return

        #Gets input states
        key_states = pygame.key.get_pressed()
        mouse_states = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        #Processes inputs
        on_key_down(current_screen, key_states)
        return_tuple = on_mouse_down(quitting, current_screen, button_list, button_call, mouse_states, mouse_pos)
        quitting, current_screen = return_tuple[0], return_tuple[1]

        #Processes updating and drawing the screen
        update(current_screen, button_list, button_call)
        current_colour = draw(current_screen, current_colour, button_list, button_call)

        pygame.display.update()

#Run! along with json data
main(persistent_flags, save_data)
