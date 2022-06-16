import json, os
import math
import pygame
from new_game import *
#from true_reset import *

#Opens json files
flagjson = open("flag.json", "r")
persistent_flags = json.loads(flagjson.read())
flagjson.close()

save_data = []
for file_name in os.listdir("save"):
    print(file_name)
    save = open("save\\" + file_name, "r")
    save_data.append(json.loads(save.read()))
    save.close()

#Initializes base pygame and extra components
pygame.init()
pygame.mixer.init()

#Loads entities
entity = []
for file_name in os.listdir("assets\\entities"):
    entity.append(pygame.image.load("assets\\entities\\" + file_name))

#Resizes assets
entity[0] = pygame.transform.scale(entity[0], (544, 200))
entity[1] = pygame.transform.scale(entity[1], (544, 200))

#Loads sounds
# sound = []
# for file_name in os.listdir("assets\\sounds"):
#    sound.append(pygame.mixer.Sound("assets\\sounds\\" + file_name))

#Initializes main screen
WIDTH = 1024
HEIGHT = 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Scallops!")

#Defines some useful custom events
LOOPMUSIC = pygame.USEREVENT + 1
BUTTON = pygame.USEREVENT + 2
SLIDER = pygame.USEREVENT + 3

#Colour bank
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
MAIN_PRIMARY = (21, 35, 56)
MAIN_SECONDARY = (165, 178, 196)
MAIN_INTERIM = (93, 107, 126)

#Font bank, using default pygame font (ie. default system font)
font = pygame.font.SysFont(None, 24)
big_font = pygame.font.SysFont(None, 48)

class Button:
    """
    Represents a clickable button.
    Anchored to the top-left corner.\n
    Button((x, y), (l, h), main, bg, text, dest)

    Attributes
    ----------
        x (int): x coordinate of button
        y (int): y coordinate of button
        l (int): length of button
        h (int): height of button
        active (tuple of int): active colour of button (changes depending on if the button is being hovered over)
        main (tuple of int): main colour of button
        bg (tuple of int): background colour of button
        text (font object): button text
        textx (int): length of the text
        texty (int): height of the text
        hitbox (Rect object): hitbox of the button; used for collision detection
        surface (Surface object): surface object on which the button is drawn
        hovering (bool): whether the button is hovered over
        dest (Event object): name of the button's destination

    Methods
    -------
        show(self, offset = 0): Draws the button onto the screen via its surface
        animate(self, mouse_pos): Determines how the button appears, depending on if it's hovered over or clicked
    """

    def __init__(self, coordinates, dimensions, main_colour, bg_colour, text, destination):
        self.x, self.y = coordinates
        self.l, self.h = dimensions

        self.active = main_colour
        self.main = main_colour
        self.bg = bg_colour

        self.text = font.render(text, True, WHITE)
        self.textx, self.texty = self.text.get_size() #Finds the dimensions of the text to then be able to center it

        self.hitbox = pygame.Rect((self.x, self.y), (self.l, self.h))
        self.surface = pygame.Surface((self.l + 2, self.h + 2)) #2px butter to accomadate for the "3D" effect
        self.surface.set_colorkey(BLACK) #To turn untouched parts of the surface transparent

        self.hovering = False
        self.dest = pygame.event.Event(BUTTON, dest = destination)

    def show(self, offset = 0):
        """
        Draws the button onto the screen via its Surface

        Parameters:
            offset (int): the y offset of the button, configurable for scrolling

        Returns:
            none
        """

        self.hitbox.topleft = (self.x, self.y - offset) #Hitbox
        screen.blit(self.surface, (self.x, self.y - offset)) #Actual button

    def animate(self, mouse_pos):
        """
        Determines how the button appears, depending on if it is hovered over or clicked

        Parameters:
            mouse_pos (tuple of int): the coordinates of the mouse location

        Returns:
            none
        """

        #Checks if the mouse is hovering over the button
        self.hovering = self.hitbox.collidepoint(mouse_pos)

        #Chooses what colour the button will take
        #bg is used for hovering, main is used otherwise
        self.active = self.bg if self.hovering else self.main

        #Erases whatever was on the surface before (uses colorkey)
        self.surface.fill((0, 0, 0))

        #Draws the "body" of the button, with rounded corners; two layers are used to achieve a 3D effect
        if self.hovering:
            pygame.draw.rect(self.surface, self.active, pygame.Rect(2, 2, self.l, self.h), 0,  8) #Top layer
        else:
            pygame.draw.rect(self.surface, self.bg, pygame.Rect(2, 2, self.l, self.h), 0,  8) #Background layer
            pygame.draw.rect(self.surface, self.active, pygame.Rect(0, 0, self.l, self.h), 0,  8) #Top layer

        #Draws the text at the center of the button; the offset is used to adjust for the "3D" effect
        #Determines if the text needs adjusting for the "3D" effect
        text_offset = 2 if self.hovering else 0
        self.surface.blit(self.text, ((self.l - self.textx)/2 + text_offset, (self.h - self.texty)/2 + text_offset))

class Slider:
    """
    Represents a slider\n
    Slider((x, y), width, l_bound, r_bound, value)

    Attributes
    ----------
        x (int): x coordinate of the slider
        y (int): y coordinate of the slider
        width (int): width of the slider
        l_bound (int): left boundary of the slider value
        r_bound (int): right boundary of the slider value
        value (int): value of the knob on the slider
        channel (int): the sound channel to make changes to (sliders are used exclusively for volume control)
        sliderx (int): x coordinate of the slider knob
        self.hitbox (Rect object): hitbox of the slider knob; used for collision detection
        self.surface (Surface object): surface on which the object is drawn
        hovering (bool): whether the button is hovered over

    Methods
    -------
        show(self, offset = 0): Draws the slider onto the screen via its surface
        animate(self, mouse_pos): Determines how the slider appears, depending on interactions with it
        adjust(self, mouse_pos): Affects slider knob behaviour when it is interacted with
    """

    def __init__(self, coordinates, width, l_value, r_value, initial_value, channel):
        self.x, self.y = coordinates
        self.width = width

        self.l_bound = l_value
        self.r_bound = r_value

        self.value = initial_value
        self.channel = pygame.event.Event(SLIDER, target = channel, value = self.value) #Custom event passing target channel and target value
        self.sliderx = self.value / (self.r_bound - self.l_bound) * self.width - 20

        self.hitbox = pygame.Rect(self.x + self.sliderx - 20, self.y - 10, 40, 60) #Hitbox for the circle
        self.surface = pygame.Surface((self.width + 40, 40))
        self.surface.set_colorkey(BLACK)

        self.hovering = False

    def show(self, offset = 0):
        """
        Draws the slider onto the screen via its surface
        Parameters:
            offset (int): the y offset of the slider, configurable for scrolling

        Returns:
            none
        """

        screen.blit(self.surface, (self.x - 20, self.y - offset))

    def animate(self, mouse_pos):
        """
        Determines how the slider appears, depending on interactions with it

        Parameters:
            mouse_pos (tuple of int): the coordinates of the mouse location

        Returns:
            none
        """

        #Checks if the mouse is hovering over the button
        self.hovering = self.hitbox.collidepoint(mouse_pos)

        #Draws the shapes
        self.surface.fill(BLACK)
        pygame.draw.rect(screen, BLACK, self.hitbox)
        pygame.draw.rect(self.surface, MAIN_PRIMARY, pygame.Rect(20, 14, self.width, 12), 0, 8)
        if self.hovering:
            pygame.draw.circle(self.surface, MAIN_INTERIM, (self.sliderx + 20, 20), 10)
        else:
            pygame.draw.circle(self.surface, MAIN_SECONDARY, (self.sliderx + 20, 20), 10)

    def adjust(self, mouse_pos):
        """
        Affects slider knob behaviour when it is interacted with

        Parameters:
            mouse_pos (tuple of int): the coordinates of the mouse location

        Returns:
            none
        """

        #Sets the knob's x coordinate
        self.sliderx = mouse_pos[0] - self.x

        #Check if the knob is out of bounds
        if self.sliderx < 20 or self.sliderx > self.width - 20:
            self.sliderx = 20 if self.sliderx < 20 else self.width - 20

        #Adjusts the hitbox according to the knob
        self.hitbox.topleft = (self.x + self.sliderx - 20, self.y - 10)

        #The value is determined by the proportion of the slider, multiplied by the difference between bounds, plus the bottom bound (in case it's non-zero)
        self.value = ((self.sliderx - 20) / self.width) * (self.r_bound - self.l_bound) + self.l_bound

class Text:
    """
    Represents text to print on screen.
    Always aligned center, but vertical alignment depends on align attribute.\n
    Text(text, (x, y))

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
            none
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
    error_message = font.render("Saving...", True, WHITE)
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

def on_mouse_down(quitting, current_screen, button_list, button_call, slider_list, button, pos):
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
        return quitting

    print(pos)

    #Checks if the game is in the settings menu
    if current_screen == "settings":
        for key in slider_list:
            if slider_list[key].hovering:
                slider_list[key].adjust(pos)
                pygame.event.post(slider_list[key].channel)

    #Checks if the game is quitting
    if current_screen == "quit" and not quitting:
        #Sets a timer for 1 second (1000 ms) to quit the game
        pygame.time.set_timer(pygame.QUIT, 1000, True)
        #Sets a flag so that the player can't refresh the timer by clicking again
        quitting = True

    #Default behaviour, checking for clicks on a button
    for key in button_call[current_screen]:
        if button_list[key].hovering:
            pygame.event.post(button_list[key].dest)
            break

    return quitting

def update(current_screen, button_list, button_call, slider_list, deg):
    """
    Updates the parts moving in the fore- and background

    Parameters:
        current_screen (int): the current screen being displayed
        button_list (dict of Button): list of Button objects
        button_call (dict of list of str): list of names of buttons to call in their respective screens

    Returns:
        None
    """

    #Gets the mouse position, for passing down to other functions
    mouse_pos = pygame.mouse.get_pos()

    #Calls the objects that should be shown in the current screen
    for key in button_call[current_screen]:
        button_list[key].animate(mouse_pos)

    #Bobbing text!
    deg += 1
    if deg == 360:
        deg = 0

    if current_screen == "settings":
        for key in slider_list:
            slider_list[key].animate(mouse_pos)

    return deg

def draw(entity, current_screen, current_colour, button_list, button_call, slider_list, text_list, text_call, deg, scroll):
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

    #Calls the behaviour for the currently displayed screen
    screen.fill(current_colour)
    current_colour = draw_dict[current_screen]()

    rad = math.radians(deg)
    #Checks if the current screen is "main menu" because the title is animated
    if current_screen == "main_menu":
        screen.blit((pygame.transform.rotate(entity[1], 2*math.sin(rad))), (54, 54)) #Bottom layer
        screen.blit((pygame.transform.rotate(entity[0], 2*math.sin(rad))), (50, 50)) #Top layer

    #Checks if the current screen is "settings" because special scroll functionality is required
    if current_screen == "settings":
        screen.blit(entity[2], (0, 0 - scroll))
        #Calls all the buttons except for the first one, which is the back button that gets called later
        for key in button_call["settings"][1:]:
            button_list[key].show(scroll)

        for key in text_call["settings"]:
            text_list[key].show(scroll)

        for key in slider_list:
            slider_list[key].show(scroll)

        #Aaaand there's the previously-mentioned back button
        button_list["back_button"].show(3*math.sin(2*rad))

        #Cuts the function short by returning
        return current_colour

    #Creates a slight offset on the bobs of the buttons
    offset = 0
    #Adds the bob to all the buttons
    for key in button_call[current_screen]:
        button_list[key].show(3*math.sin(2*(rad - offset)))
        offset += 0.3

    return current_colour

def music(sound, intro):
    """
    Controls the music

    Parameters:
        sound (list of Sound object): full list of sounds in the game
        intro (bool): whether the intro has played

    Returns:
        intro (bool): update of the intro status
    """

    if intro:
        pygame.mixer.Channel(0).play(sound[0])
        pygame.time.set_timer(LOOPMUSIC, 10739, True) #10379 is a magic number representing the length (in ms) of the first music file
        intro = False

    return intro

def main(p_flags, save_data, entity):
    """
    Runs the main program program

    Parameters:
        flags
        save_data
        entity
        sound

    Returns:
        None
    """

    current_screen = "main_menu"
    current_colour = (194, 212, 242)

    deg = 0
    scroll = 0
    intro = True
    quitting = False

    #Stores buttons corresponding to each save slot
    save_slot = []
    index = 1
    for i in save_data: #what is i doing
        if index == 1:
            positioning = (200, 300)
        elif index == 1:
            positioning = (200, 500)
        elif index == 3:
            positiong = (624, 300)
        elif index == 4:
            positiong = (624, 500)

        save_slot.append(Button(positioning, (300, 100), BLACK, (176, 152, 123), f"Save {i+1}", f"save {i}"))

        index = index + 1 if index < 5 else 1

    #Stores all the buttons that are present in the game
    button_list = {
        "new_game_button": Button((680, 300), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "New Game", "new_game"),
        "cont_game_button": Button((680, 400), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Continue Game", "cont_game"),
        "settings_button": Button((680, 500), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Settings", "settings"),
        "quit_button": Button((680, 600), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Quit", "quit"),
        "back_button": Button((422, 680), (180, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Back", "main_menu"),
        "reset_button": Button((594, 600), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Reset data", "reset"),
        "crash_button": Button((387, 1750), (250, 50), BLACK, (128, 89, 68), "Crash", "crash")
    }

    #Stores the list of buttons to display in each screen
    button_call = {
        "main_menu": ["new_game_button", "cont_game_button", "settings_button", "quit_button"],
        "new_game": [],
        "cont_game": ["back_button"],
        "settings": ["back_button", "reset_button", "crash_button"],
        "quit": []
    }

    #Stores the list of sliders present in the game
    slider_list = {
        "music_vol_slider": Slider((494, 100), 300, 0, 100, 100, 0),
        "sfx_vol_slider": Slider((494, 200), 300, 0, 100, 100, 1)
    }
    #No slider_call dictionary because they only appear in the settings menu anyways

    #Stores all the text that's present in the game
    text_list = {
        "music_vol_text": Text("Music Volume", (180, 120)),
        "sfx_vol_text": Text("Effect Volume", (180, 220))
    }

    #Stores the list of text to display in each screen
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

        #Input handling is done first so that any changes caused by them aren't delayed to the next frame (from event handling)
        #Gets input states
        key_states = pygame.key.get_pressed()
        mouse_states = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        #Processes keyboard inputs
        current_screen = on_key_down(current_screen, key_states)

        #Processes mouse inputs
        quitting = on_mouse_down(quitting, current_screen, button_list, button_call, slider_list, mouse_states, mouse_pos)

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

            #Loops the music in game after the intro plays
            elif event.type == LOOPMUSIC:
                pygame.mixer.Channel(0).play(sound[1], -1)

            elif event.type == BUTTON:
                #Checks for a data reset of the game
                if event.dest == "reset":
                    #data_reset()
                    return

                #Checks if the player willingly chose to crash the game
                if event.dest == "crash":
                    raise Exception("no, that simply won't do...")

                #Otherwise, change the screen
                current_screen = event.dest

            elif event.type == SLIDER:
                #Updates the volume of the proper sound channel
                pygame.mixer.Channel(event.target).set_volume(event.value / 100.0)

        #Processes music
        #intro = music(sound, intro)

        #Processes screen updating
        deg = update(current_screen, button_list, button_call, slider_list, deg)

        #Processes screen drawing
        current_colour = draw(entity, current_screen, current_colour, button_list, button_call, slider_list, text_list, text_call, deg, scroll)

        pygame.display.update()

#Run! along with all the requisite data
main(persistent_flags, save_data, entity)
