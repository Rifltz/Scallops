import json, math, os, random
import pygame

#Opens json files
flagjson = open("flag.json", "r")
persistent_flags = json.loads(flagjson.read())
flagjson.close()

#List to check which save files exist
save_status = [0, 0, 0, 0]

#Continues to laod json files
save_data = []
for file_name in os.listdir("save"):
    save = open("save\\" + file_name, "r")
    save_data.append(json.loads(save.read()))
    save.close()

    #Updates the status of the save to indicate existence
    save_status[int(file_name[5]) - 1] = 1

#Creates an empty save file
empty_save = {
    "fish": [""],
    "caught": 0,
    "crashed": False
}

#Creates any missing save files
for i in range(len(save_status)):
    if not save_status[i]:
        json.dump(empty_save, open(f"save\\save {str(i+1)}.json", "x"))

#Initializes base pygame and extra components
pygame.init()
pygame.mixer.init()

#Loads entities
entity = []
for file_name in os.listdir("assets\\entities"):
    entity.append(pygame.image.load("assets\\entities\\" + file_name))

#Resizes entities
entity[0] = pygame.transform.scale(entity[0], (362, 133))
entity[1] = pygame.transform.scale(entity[1], (362, 133))

#Loads sounds
sound = []
for file_name in os.listdir("assets\\sounds"):
    sound.append(pygame.mixer.Sound("assets\\sounds\\" + file_name))

#Initializes the game window
WIDTH = 1024
HEIGHT = 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Scallops!")

#Updates the sound volumes
pygame.mixer.Channel(0).set_volume(persistent_flags["music_vol"] / 100.0)
pygame.mixer.Channel(1).set_volume(persistent_flags["sfx_vol"] / 100.0)

#Defines some useful custom events
MUSIC = pygame.USEREVENT + 1
LOOPMUSIC = pygame.event.Event(MUSIC, sound = "loop")
PRESS = pygame.event.Event(MUSIC, sound = "press")
LOAD = pygame.event.Event(MUSIC, sound = "load")
SPLASH = pygame.event.Event(MUSIC, sound = "splash")
EXCLAMATION = pygame.event.Event(MUSIC, sound = "exclamation")

BUTTON = pygame.USEREVENT + 2
SLIDER = pygame.USEREVENT + 3

FISHING = pygame.USEREVENT + 4
START = pygame.event.Event(FISHING, status = "start")
SNAG = pygame.event.Event(FISHING, status = "snag")
REEL = pygame.event.Event(FISHING, stauts = "reeling")
SUCCESS = pygame.event.Event(FISHING, status = "end", success = True)
FAIL = pygame.event.Event(FISHING, status = "end", success = False)

SWITCH = pygame.USEREVENT + 5
SCREEN_SWITCH = pygame.event.Event(SWITCH)

QUITTING = pygame.USEREVENT + 6
DATA_RESET = pygame.event.Event(QUITTING)

#Colour bank
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
MAIN_PRIMARY = (21, 35, 56)
MAIN_SECONDARY = (165, 178, 196)
MAIN_INTERIM = (93, 107, 126)
CATCH_PRIMARY = (222, 142, 176)
CATCH_SECONDARY = (214, 116, 144)

#Font bank, using default pygame font (ie. default system font)
font = pygame.font.SysFont(None, 24)
big_font = pygame.font.SysFont(None, 48)

class Button:
    """
    Represents a clickable button.
    Anchored to the top-left corner.

    Attributes
    ----------
        x (int): x coordinate of button
        y (int): y coordinate of button
        l (int): length of button
        h (int): height of button
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

        self.main = main_colour
        self.bg = bg_colour

        self.text = font.render(text, True, WHITE)
        #Finds the dimensions of the text to then be able to center it
        self.textx, self.texty = self.text.get_size()

        self.hitbox = pygame.Rect((self.x, self.y), (self.l, self.h))
        self.surface = pygame.Surface((self.l + 2, self.h + 2)) #2px butter to accomadate for the 3D effect
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

        #Erases whatever was on the surface before (using colorkey)
        self.surface.fill((0, 0, 0))

        #Draws the "body" of the button, with rounded corners; two layers are used to achieve a 3D effect
        #Checks if
        if self.hovering:
            pygame.draw.rect(self.surface, self.bg, pygame.Rect(2, 2, self.l, self.h), 0,  8) #Top layer
        else:
            pygame.draw.rect(self.surface, self.bg, pygame.Rect(2, 2, self.l, self.h), 0,  8) #Background layer
            pygame.draw.rect(self.surface, self.main, pygame.Rect(0, 0, self.l, self.h), 0,  8) #Top layer

        #Determines if the text needs adjusting for the 3D effect
        text_offset = 2 if self.hovering else 0
        
        #Draws the text at the center of the button; the offset is used to adjust for the 3D effect
        self.surface.blit(self.text, ((self.l - self.textx)/2 + text_offset, (self.h - self.texty)/2 + text_offset))


class Slider:
    """
    Represents a slider

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
        hovering (bool): whether the slider knob is hovered over
        adjusted (bool): whether the slider knob is being adjusted

    Methods
    -------
        show(self, offset = 0): Draws the slider onto the screen via its surface
        animate(self, mouse_pos): Determines how the slider appears, depending on interactions with it
        adjust(self, mouse_pos): Controls the slider knob behaviour when it is interacted with
    """

    def __init__(self, coordinates, width, l_value, r_value, initial_value, channel):
        self.x, self.y = coordinates
        self.width = width

        self.l_bound = l_value
        self.r_bound = r_value

        self.value = initial_value
        self.channel = channel
        #The proportion between the bounds that the value takes, times the width of the slider
        self.sliderx = (self.value - self.l_bound) / (self.r_bound - self.l_bound) * self.width - 20

        #Mirrors the position of the slider, with some extra constants to accomodate the larger surface and the Rect coordinate system
        self.hitbox = pygame.Rect(self.x + self.sliderx - 20, self.y - 10, 40, 60)

        #The surface is slighter longer (20px on either side) than the slider itself to accomodate for the size of the knob
        self.surface = pygame.Surface((self.width + 40, 40))
        self.surface.set_colorkey(BLACK)

        self.hovering = False
        self.adjusted = False

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

        #Checks if the mouse is hovering over the slider knob
        self.hovering = self.hitbox.collidepoint(mouse_pos)

        #Erases the surface
        self.surface.fill(BLACK)

        #Draws the shapes that make up the slider
        pygame.draw.rect(screen, BLACK, self.hitbox) #Hitbox
        pygame.draw.rect(self.surface, MAIN_PRIMARY, pygame.Rect(20, 14, self.width, 12), 0, 8) #Long bar

        #Determines what colour the knob takes based on mouse hovering, and draws the knob
        if self.hovering:
            pygame.draw.circle(self.surface, MAIN_INTERIM, (self.sliderx + 20, 20), 10)
        else:
            pygame.draw.circle(self.surface, MAIN_SECONDARY, (self.sliderx + 20, 20), 10)

    def adjust(self, mouse_pos):
        """
        Controls the slider knob behaviour when it is interacted with

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

        #Calls the program to update whatever value the slider changes
        pygame.event.post(pygame.event.Event(SLIDER, target = self.channel, value = self.value))


class Text:
    """
    Represents text to print on screen.
    Always aligned center, but vertical alignment depends on align attribute.

    Attributes
    ----------
        text (font object): font object for the text to be displayed
        x (int): x coordinate of the text
        y (int): y coordintae of the text
        align (str): vertical alignment of the text

    Methods
    -------
        show(self, offset, align = "left"): Displays the text on screen according to the desired alignment
    """

    def __init__(self, text, coordinates, alignment):
        self.text = big_font.render(text, True, WHITE)
        self.x, self.y = coordinates
        self.align = alignment

    def show(self, offset = 0):
        """
        Displays the text on screen according to the desired alignment

        Parameters:
            offset (int): the y offset of the text, configurable for scrolling

        Returns:
            none
        """

        #Finds the dimensions of the text
        textx, texty = self.text.get_size()

        #Displays the text depending on the chosen alignment, centered along the y axis by default
        if self.align == "left":
            screen.blit(self.text, (self.x, self.y - texty/2 - offset))
        elif self.align == "center":
            screen.blit(self.text, (self.x - textx/2, self.y - texty/2 - offset))
        elif self.align == "right":
            screen.blit(self.text, (self.x - textx, self.y - texty/2 - offset))


#
#class Therese(pygame.sprite.Sprite):
#    """
#    Represents Therese, the movable sprite and playable character of the game
#
#    Attributes
#    ----------
#        Alongside those of the default pygame sprite class,
#        image (image object): image/sprite of the character
#        spawn (tuple of int): the initial coordinates of the character, ie. its spawn location
#        hitbox (Rect object): character hitbox
#
#    Methods
#    -------
#        Those of the default pygame sprite class
#    """
#
#    def __init__(self, image, coordinates, width, height):
#        pygame.sprite.Sprite.__init__(self)
#
#        self.image = image
#        self.spawn = (coordinates)
#        self.hitbox = pygame.Rect((coordinates[0], coordinates[1]), (width, height))


class Scallop:
    """
    Represents a scallop type in the game\n
    Scallop(image, name, description, rate)

    Attributes
    ----------
        image (Surface object): sprite of the scallop
        hitbox (surface object): hitbox of the scallop image; used for collision detection
        name (str): name of the scallop
        description (str): description of the scallop
        rate (int): catch rate of the scallop

    Methods
    -------
        display(self, mouse_pos, x, y): Displays the scallop in the proper inventory position
    """

    def __init__(self, image, name, description, catch_rate):
        self.image = image
        self.hitbox = pygame.Rect((0, 0), self.image.get_size())

        self.name = name
        self.description = description
        self.rate = catch_rate

    def display(self, mouse_pos, x, y):
        """
        Displays the scallop in the proper inventory position

        Parameters:
            mouse_pos (tuple of int): coordinates of the mouse
            x (int): x coordinate to position the display
            y (int): y coordinate to position the display

        Returns:
            name (str): name of scallop to display in the textbox
            description (str): description of scallop to display in the textbox
        """

        #Draws the scallop icon (and its hitbox) to the screen
        screen.blit(self.image, (x, y))
        self.hitbox.topleft = (x, y)

        #Checks if the icon is being hovered over
        hovering = self.hitbox.collidepoint(mouse_pos)

        if hovering:
            return self.name, self.description
        else:
            return "", ""

def on_mouse_held(current_screen, slider_list, button, pos):
    """
    Defines behaviour on held mouse inputs (just for sliders at the moment)

    Parameters:
        current_screen (str): the current screen being displayed
        slider_list (dict of Slider object): list of sliders in the game
        button (tuple of bool): the list of mouse buttons being pressed, represented with a True statement
        pos (tuple of int): tuple of mouse coordinates

    Returns:
        None
    """

    #Checks if LMB is pressed; all other mouse buttons should do nothing
    if not(button[0]):
        #Removes the adjusted state from all sliders if the mouse is no longer held
        for key in slider_list:
            slider_list[key].adjusted = False
        return

    #Checks if the game is in the settings menu to limit slider interactivity
    if current_screen == "settings":
        for key in slider_list:
            #Looks for which slider is in the adjusted state
            if slider_list[key].adjusted:
                #Adjusts the knob accordingly
                slider_list[key].adjust(pos)

def update(current_screen, save_slot, button_list, button_call, slider_list):
    """
    Updates the moving parts in the fore- and backgrounds

    Parameters:
        current_screen (int): the current screen being displayed
        save_slot (list of dict): list of available save slots
        button_list (dict of Button): list of Button objects
        button_call (dict of list of str): list of names of buttons to call in their respective screens
        slider_list (dict of Slider): list of Slider objects

    Returns:
        None
    """

    #Gets the mouse position, for passing down to other functions
    mouse_pos = pygame.mouse.get_pos()

    #Animates the buttons that should be shown on the current screen
    for key in button_call[current_screen]:
        button_list[key].animate(mouse_pos)

    #Animates the save slots if the current screen is "continue game"
    if current_screen == "cont_game":
        for key in save_slot:
            save_slot[key].animate(mouse_pos)

    #Animates the sliders if the current screen is "settings"
    elif current_screen == "settings":
        for key in slider_list:
            slider_list[key].animate(mouse_pos)

def fishing_update(status, rect_list, speed_list, text_list, stability):
    """
    Updates specifically the moving parts of the fishing minigame
    
    Parameters:
        status (str): stage of the fishing minigame
        rect_list (dict of Rect object): list of Rect objects that need to be transferred across functions
        speed_list (dict of int): list of speeds to track for the fishing minigame
        text_list (dict of Text): list of Text objects
        fish_speed (int): speed of the fish box
        stability (int): stability of the catch; 100 is success, 0 is fail
        
    Returns:
        None
    """

    #Number to control the constant deceleration of every speed variable
    gravity = 0.1

    #Nothing happenens during the "luring" phase

    #Shows the signal of a snag occuring during the "snag" phase
    if status == "snag":
        text_list["exclamation_text"].show()

    #Runs the main minigame during the "reeling" phase
    elif status == "reeling":

        speed_list["fish"] += random.uniform(-1, 3)
        speed_list["fish"] -= gravity

        #Caps the fish box speed
        if speed_list["fish"] > 10:
            speed_list["fish"] = 10
        elif speed_list["fish"] < -10:
            speed_list["fish"] = -10

        rect_list["fish_box"].y += fish_speed

        #Caps the fish box placement
        if rect_list["fish_box"].y > 500:
            rect_list["fish_box"].y = 500
            speed_list["fish"] = 0
        elif rect_list["fish_box"].y < 100:
            rect_list["fish_box"].y = 100
            fish_speed = 0

        speed_list["rod"] -= gravity

        if speed_list["rod"] > 8:
            speed_list["rod"] = 8
        elif speed_list["rod"] < -8:
            speed_list["rod"] = -8
        
        rect_list["rod_box"].y += speed_list["rod"]

        #Caps the rod box placement
        if rect_list["rod_box"].y > 500:
            rect_list["rod_box"].y = 500
            speed_list["rod"] = 0
        elif rect_list["fish_box"].y < 100:
            rect_list["rod_box"].y = 100
            speed_list["rod"] = 0

        if rect_list["rod_box"].colliderect(rect_list["rod_box"]):
            stability += 0.5

        stability += speed_list["stability"]
        speed_list["stability"] -= gravity

        if stability > 100:
            pygame.event.post(SUCCESS)
        elif stability < 0:
            pygame.event.post(FAIL)

    return speed_list, stability
    
    
def draw(entity, current_screen, save_slot, button_list, button_call, rect_list, slider_list, text_list, text_call, rad, scroll, stability):
    """
    Draws things to the screen

    Parameters:
        entity (list of Surface object): list of all the entity images
        current_screen (int): the current screen being displayed
        save_slot (list of dict): list of available save slots
        button_list (dict of Button): list of Button objects
        button_call (dict of list of str): list of names of buttons to call in their respective screens
        rect_list (dict of Rect object): list of Rect objects that need to be transferred across functions
        slider_list (dict of Slider): list of Slider objects
        text_list (dict of Text): list of Text objects
        text_call (dict of list of str) list of names of Text to call in their respective screens
        rad (float): a radian value between 0 and 2pi
        scroll (int): the scroll offset of the screen
        stability

    Returns:
        None
    """

    #Draws the title logo
    if current_screen == "main_menu":
        #Redraws the background only on some parts of the screen
        pygame.draw.rect(screen, (109,173,225), (470, 0, 554, 460)) #Sky
        pygame.draw.rect(screen, (112,146,190), (660, 460, 384, 308)) #Water
        pygame.draw.circle(screen, (222, 210, 75), (1004, -50), 200) #Sun

        #Gives the computer an easier time by pre-calcaluting a reused value
        #Uses sin to create a cyclical bob
        bob_cycle = math.sin(rad)

        #Blits the logo
        screen.blit((pygame.transform.rotate(entity[1], 2*bob_cycle)), (626, 104)) #Bottom layer
        screen.blit((pygame.transform.rotate(entity[0], 2*bob_cycle)), (624, 100)) #Top layer

    #Draws identically to "main menu" but without the title logo
    elif current_screen == "new_game":
        pygame.draw.rect(screen, (109,173,225), (470, 0, 554, 460)) #Sky
        pygame.draw.rect(screen, (112,146,190), (660, 460, 384, 308)) #Water
        pygame.draw.rect(screen, (112,146,190), (0, 680, 660, 88)) #More water
        pygame.draw.circle(screen, (222, 210, 75), (1004, -50), 200) #Sun

    #Ditto, but also draws some of the fishing minigame assets
    elif current_screen == "fishing_game":
        screen.blit(big_font.render(str(stability), True, WHITE), (500, 100))

        pygame.draw.rect(screen, (109,173,225), (470, 0, 554, 460)) #Sky
        pygame.draw.rect(screen, (112,146,190), (660, 460, 384, 308)) #Water
        pygame.draw.rect(screen, (112,146,190), (0, 680, 660, 88)) #More water
        pygame.draw.circle(screen, (222, 210, 75), (1004, -50), 200) #Sun

        pygame.draw.rect(screen, (0, 255, 0), rect_list["fish_box"])

    #Draws the save slots if the current screen is "continue game"
    elif current_screen == "cont_game":
        #Redraws certain parts of the screen
        pygame.draw.rect(screen, (193, 178, 162), (120, 70, 790, 470)) #Paper
        pygame.draw.rect(screen, (199, 177, 143), (422, 670, 180, 70)) #Back button buffer

        #Creates a slight offset on the bobs of each save slot
        offset = 0
        #Draws and applies the offset to each save slot
        for key in save_slot:
            save_slot[key].show(3*math.sin(2*(rad - offset)))
            offset += 0.3

    #Draws with a special scroll functionality included if the current screen is "settings"
    elif current_screen == "settings":
        #Draws the background image with the scroll offset
        screen.blit(entity[5], (0, 0 - scroll))

        #Draws all the buttons except for the first one, which is the back button that gets drawn over everything else
        for key in button_call["settings"][1:]:
            button_list[key].show(scroll)

        #Draws all the text
        #This is done independently of the default text-drawing behaviour because the whole draw gets cut short for "settings"
        for key in text_call["settings"]:
            text_list[key].show(scroll)

        #Draws all the sliders
        for key in slider_list:
            slider_list[key].show(scroll)

        #Aaaand there's the previously-mentioned back button
        button_list["back_button"].show(3*math.sin(2*rad))

        #Cuts the function short by returning
        return

    #Draws a blank black screen if the current screen is "quit"
    elif current_screen == "quit":
        screen.fill((10, 10, 10))

    #Creates a slight offset on the bobs of each button
    offset = 0

    #Draws and applies the bob to each button
    for key in button_call[current_screen]:
        button_list[key].show(3*math.sin(2*rad - offset))
        offset += 0.3

    #Draws any miscellaneous text
    for key in text_call[current_screen]:
        text_list[key].show()

def music(sound, intro):
    """
    Controls the music and sound effects

    Parameters:
        sound (list of Sound object): full list of sounds in the game
        intro (bool): whether the intro has played

    Returns:
        intro (bool): updated status of the intro
    """

    if intro:
        pygame.mixer.Channel(0).play(sound[0])
        pygame.time.set_timer(LOOPMUSIC, 10739, True) #10379 is a magic number representing the length (in ms) of the first music file
        intro = False

    return intro

def main(p_flags, save_data, entity):
    """
    Runs the main program loop

    Parameters:
        p_flags (dict): various data that persists between instances of the game
        save_data (list of dict) list of loaded save data
        entity (list of Surface object): list of all the entity images
        sound (list of Sound object): list of all the sounds

    Returns:
        save_status (str): Message to print in the console upon quitting the game
    """

    #Sets the default screen
    current_screen = "main_menu"
    pygame.event.post(SCREEN_SWITCH)

    #Declares some useful variables
    deg = 0 #Degree value, for sin
    scroll = 0 #Scrol value, to track scrolling
    intro = True #If the sound intro has played
    quitting = False #If the game is quitting

    #Declares some fishing minigame flags
    status = "luring"

    speed_list = {
        "stability": 0,
        "fish": 0,
        "rod": 0
    }

    stability = 10.0

    #Creates empty save slot in case the player doesn't load a save file
    active_slot = 0
    active_save = {
        "fish": [""],
        "caught": 0,
        "crashed": False
    }

    #Stores buttons corresponding to each save slot
    save_slot = {}
    index = 1
    for i in range(len(save_data)):
        if index == 1:
            positioning = (150, 80)
        elif index == 2:
            positioning = (150, 320)
        elif index == 3:
            positioning = (554, 80) #x component is WIDTH - 100 - 320
        elif index == 4:
            positioning = (554, 320)

        save_slot[f"save {i}"] = (Button(positioning, (320, 200), (193, 178, 162), (176, 152, 123), f"""File {i+1}: {save_data[i]["caught"]} catches""", f"save {i}"))

        #This line was supposed to also support multiple pages of save files; I ultimately scrapped the idea
        index = index + 1 #if index < 5 else 1

    #Stores all the buttons that are present in the game
    button_list = {
        "new_game_button": Button((680, 270), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "New Game", "new_game"),
        "cont_game_button": Button((680, 370), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Continue Game", "cont_game"),
        "settings_button": Button((680, 470), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Settings", "settings"),
        "quit_button": Button((680, 570), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Quit", "quit"),
        "back_button": Button((422, 680), (180, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Back", "main_menu"),
        "reset_button": Button((594, 600), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Reset data", "reset"),
        "crash_button": Button((387, 1750), (250, 50), BLACK, (128, 89, 68), "Crash", "crash"),
        "catch_button": Button((674, 668), (300, 80), CATCH_PRIMARY, CATCH_SECONDARY, "Catch!", "catch"),
        "save_button": Button((50, 698), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Save", "saving")
    }

    #Stores the list of buttons to display in each screen
    button_call = {
        "main_menu": ["new_game_button", "cont_game_button", "settings_button", "quit_button"],
        "new_game": ["catch_button", "save_button"],
        "fishing_game": [],
        "cont_game": ["back_button"],
        "settings": ["back_button", "reset_button", "crash_button"],
        "quit": []
    }

    #Stores the list of pygame.Rect() objects that need to be transferred between functions
    rect_list = {
        "stability_box": pygame.Rect(500, 200, 50, 2*stability),
        "fish_box": pygame.Rect(750, 0, 30, 80),
        "rod_box": pygame.Rect(750, 0, 30, 30)
    }

    #Stores the list of sliders present in the game
    slider_list = {
        "music_vol_slider": Slider((494, 100), 300, 0, 100, p_flags["music_vol"], 0),
        "sfx_vol_slider": Slider((494, 200), 300, 0, 100, p_flags["sfx_vol"], 1)
    }

    #No slider_call dictionary because they only appear in the settings menu anyways

    #Stores all the text that's present in the game
    text_list = {
        "exclamation_text": Text("!", (300, 450), "center"),
        "music_vol_text": Text("Music Volume", (180, 120), "left"),
        "sfx_vol_text": Text("Effect Volume", (180, 220), "left"),
        "saving_text": Text("Saving...", (512, 384), "center")
    }

    #Stores the list of text to display in each screen
    text_call = {
        "main_menu": [],
        "new_game": [],
        "fishing_game": [],
        "cont_game": [],
        "settings": ["music_vol_text", "sfx_vol_text"],
        "quit": ["saving_text"]
    }

    #Stores the types of fish in the game
    fish_list = {
        "glitch_scallop": Scallop(entity[3], """Scal&A%"   l---   op  --0-+   """, "Uh oh", 2),
        "pearl_scallop": Scallop(entity[3], "Pearl Scallop", "Not an actual species, but hey! It's got a pearl!", 8),
        "queen_scallop": Scallop(entity[3], "Queen Scallop", "Regal in both appearance and in taste.", 22),
        "bay_scallop": Scallop(entity[3], "Bay Scallop", "A common scallop. Makes for a nice meal.", 100)
    }

    #Boilerplate statement for infinite while loop
    running = True
    while running:

        #Caps the framerate at 60 and records how much time has passed since the last frame
        #Cheeky math reference of "delta t," or "change in time"
        dt = clock.tick(60)

        #Input handling is done first so that any changes caused by them aren't delayed to the next frame (from event handling)
        #Gets input states
        keys = pygame.key.get_pressed()
        mouse_states = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        #Processes held mouse inputs
        on_mouse_held(current_screen, slider_list, mouse_states, mouse_pos)

        #Handles pygame events
        for event in pygame.event.get():
            #Exits the while loop (and the program as a whole) if the QUIT event is called
            if event.type == pygame.QUIT:
                return "Succesfully saved persistent data."

            #Processes keyboard input
            elif event.type == pygame.KEYDOWN:
                print("key")
                #Checks if esc was pressed, used similarly to the back button
                if event.key == pygame.K_ESCAPE:
                    #Acts as the quit button if the current screen is "main menu"
                    if current_screen == "main_menu":
                        (pygame.QUIT, 10)
                        return current_screen

                    #Acts as the save button if the current screen is "new game"
                    elif current_screen == "new_game":
                        button_list["save_button"].dest

                    #Ends the fishing minigame by just pretending the player lost if the current screen is "fishing game"
                    elif current_screen == "fishing_game":
                        pygame.event.post(FAIL)

                    else:
                        current_screen = "main_menu"
                        pygame.event.post(SCREEN_SWITCH)
                
                #Checks if the spacebar was pressed
                elif event.key == pygame.K_SPACE:
                    #Checks if the current screen is "fishing game" to react to the "snag" phase
                    #Both this and the mouse click can be used
                    if current_screen == "fishing_game":
                        if status == "snag":
                            #Disables the failure check
                            pygame.time.set_timer(FAIL, 0)
                            #Moves the fishing minigame onto the next phase
                            pygame.event.post(REEL)
                        #Otherwise, counts it as the player prematurely reeling the line back in
                        else:
                            pygame.event.post(FAIL)

            #Processes mouse input
            elif event.type == pygame.MOUSEBUTTONDOWN:
                #Checks if LMB is pressed; all other mouse buttons should do nothing
                if event.button != 1:
                    continue

                print(event.pos)

                #Checks if the current screen is "fishing game" to react to the "snag" phase
                #Both this and the keyboard press can be used
                if current_screen == "fishing_game":
                    if status == "snag":
                        #Disables the failure check
                        pygame.time.set_timer(FAIL, 0)
                        #Moves the fishing minigame onto the next phase
                        pygame.event.post(REEL)
                    #Otherwise, counts it as the player prematurely reeling the line back in
                    else:
                        pygame.event.post(FAIL)

                #Checks if the current screen is "continue game" to check save slot buttons
                if current_screen == "cont_game":
                    for key in save_slot:
                        if save_slot[key].hovering:
                            pygame.event.post(save_slot[key].dest)

                #Checks if the current screen is "settings" to apply the "press" behaviour of sliders
                if current_screen == "settings":
                    for key in slider_list:
                        #Checks if the slider knob is being hovered over
                        if slider_list[key].hovering:
                            slider_list[key].adjusted = True
                            #Plays the sound effect
                            pygame.event.post(PRESS)

                #Default behaviour, checking for clicks on a button
                for key in button_call[current_screen]:
                    if button_list[key].hovering:
                        pygame.event.post(button_list[key].dest)
                        break

            #Processes scroll wheel input
            elif event.type == pygame.MOUSEWHEEL:
                scroll -= 50*event.y

                #Confines the scroll value between 0 and 1400
                if scroll < 0:
                    scroll = 0
                elif scroll > 1400:
                    scroll = 1400

            #Loops the music in game after the intro plays
            elif event.type == MUSIC:
                #Loops the main background music
                if event.sound == "loop":
                    pygame.mixer.Channel(0).play(sound[1], -1)

                #Plays the sound of a button pressing
                elif event.sound == "press":
                    pygame.mixer.Channel(1).play(sound[2])

                #Plays the sound of a save file being laoded
                elif event.sound == "load":
                    pygame.mixer.Channel(1).play(sound[3])
                
                #Plays the sound of the fishing minigame beginning
                elif event.sound == "splash":
                    pygame.mixer.Channel(1).play(sound[4])

                #Plays the sound of the fishing minigame beginning
                elif event.sound == "exclamation":
                    pygame.mixer.Channel(1).play(sound[5])

            #Processes button behaviour upon clicking one
            elif event.type == BUTTON:

                #Checks if a save file is being loaded
                if event.dest[:4] == "save":
                    #Plays the special loading sound effect
                    pygame.event.post(LOAD)

                    #Immediately transitions to the new game screen
                    current_screen = "new_game"
                    pygame.event.post(SCREEN_SWITCH)

                    #Sets the selected file as the active file
                    #The 6th letter (and onwards) is the number of the save file
                    active_slot = int(event.dest[5:]) - 1
                    active_save = save_data[int(event.dest[5:])]
                    continue

                #Play the default sound effect (given a save isn't being loaded)
                pygame.event.post(PRESS)

                #Checks if progress is being saved
                if event.dest == "saving":
                    #Transitions to the main menu
                    current_screen = "main_menu"
                    pygame.event.post(SCREEN_SWITCH)

                    #Saves the active save file to the proper spot in the rest of the save data
                    save_data[active_slot] = active_save
                    continue

                #Checks for a data reset of the game
                if event.dest == "reset":
                    #Creates empty version of save slot
                    empty_save = {
                        "fish": [""],
                        "caught": 0,
                        "crashed": False
                    }

                    #Wipes all save files
                    for file_name in os.listdir("save"):
                        json.dump(empty_save, open("save\\" + file_name, "w"))

                    #Returns persistent data to default state
                    p_flags = {"music_vol": 100.0, "sfx_vol": 100.0, "state": 0, "quits": 0, "drained": False, "crashed": False}

                    #Returns confirmation and closes the game with default behaviour
                    print("Succesfully reset data.")
                    pygame.event.post(DATA_RESET)
                    continue

                #Checks if the player willingly chose to crash the game
                if event.dest == "crash":
                    #Terminates the game loop and sends a message in console
                    return "ERROR: could not save persistent data. \nWhatever you did, please do not do it again."

                #Checks if the fishing minigame is about to begin
                if event.dest == "catch":
                    pygame.event.post(START)
                    continue

                #Checks if the game is quitting
                if event.dest == "quit":
                    #Sets a timer for 1 second (1000 ms) to quit the game
                    pygame.time.set_timer(QUITTING, 1000, True)

                #Otherwise, changes the screen
                current_screen = event.dest
                #Calls the controller for blitting objects once upon transition
                pygame.event.post(SCREEN_SWITCH)

            #Processes slider behaviour upon clicking the knob
            elif event.type == SLIDER:
                #Updates the volume of the proper sound channel
                pygame.mixer.Channel(event.target).set_volume(event.value / 100.0)
                
                #Saves the new value to persistent data
                if event.target == 0:
                    p_flags["music_vol"] = event.value
                elif event.target == 1:
                    p_flags["sfx_vol"] = event.value

            #Checks if the fishing minigame status is being updated
            elif event.type == FISHING:
                #Always calls a redraw
                pygame.event.post(SCREEN_SWITCH)

                #Makes sure that the fishing minigame is still running, as it's possible to prematurely quit out
                if current_screen != "fishing":
                    return

                #Checks which phase the minigame is currently in
                if event.status == "start":
                    #Sets the current screen to "fishing game" and starts the first phase
                    current_screen = "fishing_game"
                    status = "luring"

                    #Sets a timer for moving onto the next phase
                    luring_time = int(random.uniform(2, 8) * 1000) #Multiplied by 1000 to convert to ms
                    pygame.time.set_timer(SNAG, luring_time, True)

                    #Plays the sound effect
                    pygame.event.post(SPLASH)

                elif event.status == "snag":
                    #Sets a timer for the player to react and updates the phase
                    pygame.time.set_timer(FAIL, 1000, True)
                    status = "snag"

                    #Plays the sound effect
                    pygame.event.post(EXCLAMATION)

                elif event.status == "reeling":
                    #Updates the phase
                    status = "reeling"

                elif event.status == "end":
                    #Checks if the player succeeded to catch a fish
                    if event.success:
                        for key in fish_list:
                            rng = random.randint(1, 100)
                            if fish_list[key].rate >= rng:
                                active_save["fish"].append(fish_list[key])

                                if key == "glitch_scallop":
                                    active_save["crashed"] = True
                                    p_flags["state"] = 1
                                break

                        #Increments the number of fish caught
                        active_save["caught"] += 1

                    #Ends the minigmae regardless of outcome
                    current_screen = "new_game"

            #Checks if the game is calling for a one-time redraw, usually upon switching screens
            elif event.type == SWITCH:
                #Additionally draws things that are drawn onto the screen only once upon transition
                if current_screen == "main_menu" or current_screen == "new_game" or current_screen == "fishing_game":
                    pygame.draw.rect(screen, (109,173,225), (0, 0, 1024, 460)) #Sky
                    pygame.draw.rect(screen, (112,146,190), (0, 460, 1024, 308)) #Water
                    screen.blit(entity[2], (0, 0))

                elif current_screen == "cont_game":
                    screen.fill((199, 177, 143)) #Background
                    screen.blit(entity[4], (0, 0)) #Book

            elif event.type == QUITTING:
                json.dump(p_flags, open("flag.json", "w"))
                pygame.time.set_timer(pygame.QUIT, 10, True)

        #Processes bobbing cycle for various objects
        deg = deg + 1 if deg < 360 else 0
        #Converts deg to radian
        rad = math.radians(deg)

        #Processes music
        intro = music(sound, intro)

        #Processes screen updating
        update(current_screen, save_slot, button_list, button_call, slider_list)

        #Proceses updating specifically for the fishing minigame
        if current_screen == "fishing_game":
            #Enables held key behaviour here because it's the only time it's used
            if keys[pygame.K_SPACE]:
                speed_list["rod"] += 1
            
            speed_list, stability = fishing_update(status, rect_list, speed_list, text_list, stability)

        #Processes screen drawing
        draw(entity, current_screen, save_slot, button_list, button_call, rect_list, slider_list, text_list, text_call, rad, scroll, stability)

        pygame.display.update()

#Run! along with all the requisite data
save_status = main(persistent_flags, save_data, entity)
#Prints a message to console depending on how the game was exited
print(save_status)
