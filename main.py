import json, os
import math
import pygame
from new_game import *
#from true_reset import *

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

entity = []
for file_name in os.listdir("entities"):
    entity.append(pygame.image.load("entities\\" + file_name))

entity[1] = pygame.transform.scale(entity[1], (544, 200))

#Initialize pygame and the relevant components
pygame.init()
WIDTH = 1024
HEIGHT = 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

#Colour bank
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
MAIN_PRIMARY = (21, 35, 56)
MAIN_SECONDARY = (218, 224, 232)

#Font bank, using default pygame font (ie. default system font)
font = pygame.font.SysFont(None, 24)
big_font = pygame.font.SysFont(None, 48)

class Button:
    """
    Represents a clickable button

    Attributes
    ----------
        coord (list of int): coordinate location of the button
        dim (list of int): dimensions of the button
        c_active (tuple of int): active colour of button (changes depending on if the button is being hovered over)
        main (tuple of int): main colour of button
        bg (tuple of int): background colour of button
        text (font object): button text
        rect (Rect object): button hitbox, used for collision detection
        surf (Surface object): surface object on which the button is drawn
        hovering (bool): whether the button is hovered over
        dest (str): name of the button's destination

    Methods
    -------
        show(self, offset = 0): Draws the button onto the screen via its surface
        animate(self, mouse_pos): Determines how the button appears, depending on if it's hovered over or clicked
        press(self, screen): Carries out what happens when the button is clicked
    """

    def __init__(self, coordinates, dimensions, main_colour, bg_colour, text, destination):
        self.coord = coordinates
        self.dim = dimensions

        self.c_active = BLACK
        self.main = main_colour
        self.bg = bg_colour

        self.text = font.render(text, True, WHITE)
        self.rect = pygame.Rect((self.coord[0], self.coord[1]), (self.dim[0], self.dim[1]))
        self.surf = pygame.Surface((self.dim[0], self.dim[1]))
        self.hovering = False
        self.dest = destination

    def show(self, offset = 0):
        """
        Draws the button onto the screen via its Surface

        Parameters:
            offset (int): the y offset of the button, configurable for scrolling

        Returns:
            None
        """

        self.rect.topleft = (self.coord[0], self.coord[1] - offset) #Hitbox
        screen.blit(self.surf, (self.coord[0], self.coord[1] - offset)) #Actual button

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
            screen (str): the new screen to begin displaying
        """

        #Checks for a data reset of the game
        if self.dest == "reset":
            #data_reset()
            return screen

        #Checks if the player willingly chose to crash the game
        if self.dest == "crash":
            raise Exception("no, that simply won't do...")

        #Otherwise, change the screen
        screen = self.dest
        return screen

class Text:
    """
    Represents text to print on screen

    Attributes
    ----------
        text (font object): font object for the text to be displayed
        x (int): x coordinate of the text
        y (int): y coordintae of the text

    Methods
    -------
        show(self, offset, align = "left"): Displays the text on screen according to the desired alignment
    """

    def __init__(self, text, coordinates):
        self.text = big_font.render(text, True, WHITE)
        self.x, self.y = coordinates

    def show(self, offset, align = "left"):
        """
        Displays the text on screen according to the desired alignment

        Parameters:
            offset (int): the y offset of the text, configurable for scrolling
            align (str): which part to align the text from

        Returns:
            None
        """

        #Finds the dimensions of the text
        textx, texty = self.text.get_size()

        #Displays the text depending on the chosen alignment, centered along the y axis by default
        if align == "left":
            screen.blit(self.text, (self.x, self.y - texty/2 - offset))
        elif align == "center":
            screen.blit(self.text, (self.x - textx/2, self.y - texty/2 - offset))
        elif align == "right":
            screen.blit(self.text, (self.x - textx, self.y - texty/2 - offset))

class Slider:
    """
    Represents a slider

    Attributes
    ----------
        x (int): x coordinate of the slider
        y (int): y coordinate of the slider
        width (int): width of the slider
        value (int): value of the knob on the slider

    Methods
    -------
        animate(self, mouse_pos): Determines how the slider appears, depending on if it's hovered over or clicked
    """

    def __init__(self, coordinates, width, initial_value):
        self.x, self.y = coordinates
        self.width = width
        self.value = initial_value

    def animate(self, mouse_pos):
        pass

class Therese(pygame.sprite.Sprite):
    """
    Represents Therese, the movable sprite and playable character of the game

    Attributes
    ----------
        Alongside those of the default pygame sprite class,
        image (image object): image/sprite of the character
        spawn (tuple of int): the initial coordinates of the character, ie. its spawn location
        hitbox (Rect object): character hitbox

    Methods
    -------
        Those of the default pygame sprite class
    """

    def __init__(self, image, coordinates, width, height):
        pygame.sprite.Sprite.__init__(self)

        self.image = image
        self.spawn = (coordinates)
        self.hitbox = pygame.Rect((coordinates[0], coordinates[1]), (width, height))

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

def on_mouse_down(quitting, current_screen, button_list, button_call, button, pos):
    """
    Defines behaviour on mouse presses or movement

    Parameters:
        quitting (bool): whether the game is in the process of quitting
        current_screen (str): the current screen being displayed
        button_list (dict of Button): list of Button objects
        button_call (dict of list of str): list of names of buttons to call in their respective screens
        button (tuple of bool): the list of mouse buttons being pressed, represented with a True statement
        pos (tuple of int): tuple of mouse coordinates

    Returns:
        quitting (bool): whether the game is in the process of quitting
        current_screen (str): the screen to change to
    """

    #Checks if LMB is pressed; all other mouse buttons should do nothing
    if not(button[0]):
        return quitting, current_screen

    #Checks if the game is quitting
    if current_screen == "quit" and not quitting:
        #Sets a timer for 1 second (1000 ms) to quit the game
        pygame.time.set_timer(pygame.QUIT, 1000, 1)
        #Sets a flag so that the player can't refresh the timer by clicking again
        quitting = True

    #Default behaviour, checking for clicks on a button
    for key in button_call[current_screen]:
        if button_list[key].hovering:
            current_screen = button_list[key].press(current_screen)
            break

    return quitting, current_screen

def on_key_down(current_screen, key):
    """
    Defines behaviour on key presses

    Parameters:
        current_screen (str): the current screen being displayed
        key (list of bool): the list of keys being pressed, represented with a True statement

    Returns:
        current_screen (str): the screen to change to
    """

    if key[pygame.K_ESCAPE]:
        if current_screen == "main_menu":
            pygame.time.set_timer(pygame.QUIT, 10)
            return current_screen
        if current_screen != "new_game":
            current_screen = "main_menu"

    return current_screen

def update(current_screen, button_list, button_call, deg):
    """
    Updates the parts moving in the fore- and background

    Parameters:
        current_screen (int): the current screen being displayed
        button_list (dict of Button): list of Button objects
        button_call (dict of list of str): list of names of buttons to call in their respective screens

    Returns:
        None
    """

    mouse_pos = pygame.mouse.get_pos()

    for key in button_call[current_screen]:
        button_list[key].animate(mouse_pos)
    
    if current_screen == "main_menu":
        if deg == 360:
            deg = 0
        deg += 1

    return deg


def draw(entity, current_screen, current_colour, button_list, button_call, text_list, text_call, deg, scroll):
    """
    Draws things to the screen

    Parameters:
        current_screen (int): the current screen being displayed
        current_colour (tuple of int): the current colour of the background
        button_list (dict of Button): list of Button objects
        button_call (dict of list of str): list of names of buttons to call in their respective screens
        text_list (dict of Text): list of Text objects
        text_call (dict of list of Text) list of names of Text to call in their respective screens

    Returns:
        current_colour (int): the colour to change the background to
    """

    current_colour = draw_dict[current_screen]()
    screen.fill(current_colour)

    if current_screen == "main_menu":
        rad = math.radians(deg)
        screen.blit((pygame.transform.rotate(entity[1], 2*math.sin(rad))), (50, 50))

    if current_screen == "settings":
        for key in button_call["settings"][1:]:
            button_list[key].show(scroll)

        for key in text_call["settings"]:
            text_list[key].show(scroll)

        bottom = pygame.Surface((1024, 100))
        bottom.fill((143, 102, 79))
        screen.blit(bottom, (0, 668))

        button_list["back_button"].show()

        return current_colour

    for key in button_call[current_screen]:
        button_list[key].show()

    return current_colour

def main(flags, saveData, entity):
    """
    Runs the program

    Parameters:
        None

    Returns:
        None
    """

    current_screen = "main_menu"
    current_colour = (194, 212, 242)

    deg = 0
    scroll = 0
    quitting = False

    #Stores all the buttons that are present in the game
    button_list = {
        "new_game_button": Button((650, 200), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "New Game", "new_game"),
        "cont_game_button": Button((650, 300), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Continue Game", "cont_game"),
        "settings_button": Button((650, 400), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Settings", "settings"),
        "quit_button": Button((650, 500), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Quit", "quit"),
        "back_button": Button((422, 700), (180, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Back", "main_menu"),
        "reset_button": Button((594, 600), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Reset data", "reset"),
        "crash_button": Button((387, 1750), (250, 50), BLACK, (20, 20, 20), "Crash", "crash")
    }

    #Stores the list of buttons to display in each screen
    button_call = {
        "main_menu": ["new_game_button", "cont_game_button", "settings_button", "quit_button"],
        "new_game": [],
        "cont_game": ["back_button"],
        "settings": ["back_button", "reset_button", "crash_button"],
        "quit": []
    }

    text_list = {
        "music_vol_text": Text("Music Volume", (180, 120)),
        "sfx_vol_text": Text("Effect Volume", (180, 220))
    }

    text_call = {
        "main_menu": [],
        "new_game": [],
        "cont_game": [],
        "settings": ["music_vol_text", "sfx_vol_text"],
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
            elif event.type == pygame.MOUSEWHEEL:
                scroll -= 50*event.y
                if scroll < 0:
                    scroll = 0
                elif scroll > 1400:
                    scroll = 1400

        #Gets input states
        key_states = pygame.key.get_pressed()
        mouse_states = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        #Processes keyboard inputs
        current_screen = on_key_down(current_screen, key_states)

        #Processes mouse inputs
        return_tuple = on_mouse_down(quitting, current_screen, button_list, button_call, mouse_states, mouse_pos)
        quitting, current_screen = return_tuple[0], return_tuple[1]

        #Processes screen updating
        deg = update(current_screen, button_list, button_call, deg)

        #Processes screen drawing
        current_colour = draw(entity, current_screen, current_colour, button_list, button_call, text_list, text_call, deg, scroll)

        pygame.display.update()

#Run! along with json data
main(persistent_flags, save_data, entity)
