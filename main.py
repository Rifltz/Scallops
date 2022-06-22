import json, math, random, os
import pygame
from new_game import *
#from true_reset import *

#Opens json files
flagjson = open("flag.json", "r")
persistent_flags = json.loads(flagjson.read())
flagjson.close()

save_data = []
for file_name in os.listdir("save"):
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
entity[0] = pygame.transform.scale(entity[0], (362, 133))
entity[1] = pygame.transform.scale(entity[1], (362, 133))

#Loads sounds
sound = []
for file_name in os.listdir("assets\\sounds"):
    sound.append(pygame.mixer.Sound("assets\\sounds\\" + file_name))

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

FISHING = pygame.USEREVENT + 4
START = pygame.event.Event(FISHING, status = "start")
CATCH = pygame.event.Event(FISHING, status = "catch")
END = pygame.event.Event(FISHING, status = "end")

QUITTING = pygame.USEREVENT + 5
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
        self.channel = channel
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

        pygame.event.post(pygame.event.Event(SLIDER, target = self.channel, value = self.value))

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

class Scallop:
    """
    Represents the scallops in the game

    Attributes
    ----------
        img (Surface object): sprite of the scallop
        hitbox (surface object): hitbox of the scallop image; used for collision detection
        name (str): name of the scallop
        description (str): description of the scallop
        rate (int): catch rate of the scallop

    Methods
    -------
        display(inventory): Displays the scallop in the proper inventory position
    """

    def __init__(self, image, name, description, catch_rate):
        self.image = image
        self.name = name
        self.description = description
        self.rate = catch_rate

        self.hitbox = pygame.Rect((0, 0), self.image.get_size())

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

        screen.blit(self.image, (x, y))
        self.hitbox.topleft = (x, y)

        hovering = self.hitbox.collidepoint(mouse_pos)

        if hovering:
            return self.name, self.description
        else:
            return "", ""

def on_mouse_down(current_screen, slider_list, button, pos):
    """
    Defines behaviour on held mouse inputs

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
        return

    #Checks if the game is in the settings menu
    if current_screen == "settings":
        for key in slider_list:
            if slider_list[key].hovering:
                slider_list[key].adjust(pos)

def fishing(status, active_save, fish_list):
    if status == "luring":
        rng = random.randint(1, 100)
        if catch >= rng:
            pygame.event.post(CATCH)
        return catch, active_save

    if status == "reeling":
        pass

def update(current_screen, save_slot, button_list, button_call, slider_list, quitting):
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

    if current_screen == "new_game":
        new_game()

    elif current_screen == "cont_game":
        for key in save_slot:
            save_slot[key].animate(mouse_pos)

    elif current_screen == "settings":
        for key in slider_list:
            slider_list[key].animate(mouse_pos)

def draw(entity, current_screen, save_slot, button_list, button_call, slider_list, text_list, text_call, rad, scroll):
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

    #Checks if the current screen is "main menu" because the title is animated
    if current_screen == "main_menu":
        #Blits the background image
        pygame.draw.rect(screen, (109,173,225), (470, 0, 554, 460)) #Sky
        pygame.draw.rect(screen, (112,146,190), (660, 460, 384, 308)) #Water
        
        #Makes the computer have an easier time by pre-calcaluting a reused value
        bob_cycle = math.sin(rad)

        #Blits the logo
        screen.blit((pygame.transform.rotate(entity[1], 2*bob_cycle)), (626, 104)) #Bottom layer
        screen.blit((pygame.transform.rotate(entity[0], 2*bob_cycle)), (624, 100)) #Top layer

    elif current_screen == "new_game":
        pygame.draw.rect(screen, (109,173,225), (470, 0, 554, 460)) #Sky
        pygame.draw.rect(screen, (112,146,190), (660, 460, 384, 308)) #Water

    #Checks if the current screen is "continue game" because the save slots need to be shown
    elif current_screen == "cont_game":
        pygame.draw.rect(screen, (193, 178, 162), (120, 70, 790, 470)) #Paper
        pygame.draw.rect(screen, (199, 177, 143), (422, 670, 180, 70)) #Back button buffer
        
        #Creatse a slight offset on the bobs of the buttons
        offset = 0
        for key in save_slot:
            save_slot[key].show(3*math.sin(2*(rad - offset)))
            offset += 0.3

    #Checks if the current screen is "settings" because special scroll functionality is required
    elif current_screen == "settings":
        screen.blit(entity[5], (0, 0 - scroll))
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
        return
    
    elif current_screen == "quit":
        screen.fill((0, 0, 0))

    #Creates a slight offset on the bobs of the buttons
    offset = 0

    #Adds the bob to all the buttons
    for key in button_call[current_screen]:
        button_list[key].show(3*math.sin(2*rad - offset))
        offset += 0.3

    #Prints any miscellaneous text
    for key in text_call[current_screen]:
        text_list[key].show()

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
    pygame.draw.rect(screen, (109,173,225), (0, 0, 1024, 460)) #Sky
    pygame.draw.rect(screen, (112,146,190), (0, 460, 1024, 308)) #Water
    screen.blit(entity[2], (0, 0))

    deg = 0
    scroll = 0
    intro = True
    quitting = False

    #Fishing minigame flags
    fishing = False
    status = "luring"

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
            positioning = (554, 80) #x component is WIDTH - 100 - 360
        elif index == 4:
            positioning = (554, 320)

        save_slot[f"save {i}"] = (Button(positioning, (320, 200), (193, 178, 162), (176, 152, 123), f"""File {i+1}: {save_data[i]["caught"]} catches""", f"save {i}"))

        index = index + 1 if index < 5 else 1

    #Stores all the buttons that are present in the game
    button_list = {
        "new_game_button": Button((680, 270), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "New Game", "new_game"),
        "cont_game_button": Button((680, 370), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Continue Game", "cont_game"),
        "settings_button": Button((680, 470), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Settings", "settings"),
        "quit_button": Button((680, 570), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Quit", "quit"),
        "back_button": Button((422, 680), (180, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Back", "main_menu"),
        "reset_button": Button((594, 600), (250, 50), MAIN_PRIMARY, MAIN_SECONDARY, "Reset data", "reset"),
        "crash_button": Button((387, 1750), (250, 50), BLACK, (128, 89, 68), "Crash", "crash"),
        "catch_button": Button((600, 600), (300, 100), CATCH_PRIMARY, CATCH_SECONDARY, "Catch!", "catch")
    }

    #Stores the list of buttons to display in each screen
    button_call = {
        "main_menu": ["new_game_button", "cont_game_button", "settings_button", "quit_button"],
        "new_game": ["catch_button"],
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
        "music_vol_text": Text("Music Volume", (180, 120), "left"),
        "sfx_vol_text": Text("Effect Volume", (180, 220), "left"),
        "saving_text": Text("Saving...", (512, 384), "center")
    }

    #Stores the list of text to display in each screen
    text_call = {
        "main_menu": [],
        "new_game": [],
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
        mouse_states = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        #Processes held mouse inputs
        on_mouse_down(current_screen, slider_list, mouse_states, mouse_pos)

        #Handles pygame events
        for event in pygame.event.get():
            #Exits the while loop (and the program as a whole) if the QUIT event is called
            if event.type == pygame.QUIT:
                return "Succesfully saved persistent data."

            #Processes keyboard input
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_screen == "main_menu":
                        pygame.time.set_timer(pygame.QUIT, 10)
                        return current_screen

                    if current_screen != "new_game":
                        current_screen = "main_menu"

            #Processes mouse input
            elif event.type == pygame.MOUSEBUTTONDOWN:
                #Checks if LMB is pressed; all other mouse buttons should do nothing
                if event.button != 1:
                    continue

                print(event.pos)

                #Checks if the current screen is "continue game" to check save slot buttons
                if current_screen == "cont_game":
                    for key in save_slot:
                        if save_slot[key].hovering:
                            pygame.event.post(save_slot[key].dest)

                #Default behaviour, checking for clicks on a button
                for key in button_call[current_screen]:
                    if button_list[key].hovering:
                        pygame.event.post(button_list[key].dest)
                        break

            #Processes scroll wheel input
            elif event.type == pygame.MOUSEWHEEL:
                scroll -= 50*event.y
                if scroll < 0:
                    scroll = 0
                elif scroll > 1400:
                    scroll = 1400

            #Loops the music in game after the intro plays
            elif event.type == LOOPMUSIC:
                pygame.mixer.Channel(0).play(sound[1], -1)

            #Processes button behaviour upon clicking one
            elif event.type == BUTTON:
                #Checks if a save file is being loaded
                if event.dest[:4] == "save":
                    current_screen = "new_game"
                    active_save = save_data[int(event.dest[5])]
                    continue

                #Checks for a data reset of the game
                if event.dest == "reset":
                    #Wipes all save files
                    for file_name in os.listdir("save"):
                        os.remove("save\\" + file_name)

                    #Returns persistent data to default state
                    p_flags = {"state": 0, "quits": 0, "drained": False, "crashed": False}

                    #Returns confirmation and closes the game
                    print("Succesfully reset data.")
                    pygame.event.post(DATA_RESET)
                    continue

                #Checks if the player willingly chose to crash the game
                if event.dest == "crash":
                    return "ERROR: could not save persistent data. \nWhatever you did, please do not do it again."

                #Checks if the fishing minigame is about to begin
                if event.dest == "catch":
                    fishing = True
                    continue

                #Checks if the game is quitting
                if event.dest == "quit":
                    #Sets a timer for 1 second (1000 ms) to quit the game
                    pygame.time.set_timer(QUITTING, 1000, True)

                #Otherwise, changes the screen
                current_screen = event.dest

                #Additionally draws things that are drawn onto the screen only once upon transition
                if current_screen == "main_menu":
                    pygame.draw.rect(screen, (109,173,225), (0, 0, 1024, 460)) #Sky
                    pygame.draw.rect(screen, (112,146,190), (0, 460, 1024, 308)) #Water
                    screen.blit(entity[2], (0, 0))

                elif current_screen == "cont_game":
                    screen.fill((199, 177, 143)) #Background
                    screen.blit(entity[4], (0, 0)) #Book

            #Processes slider behaviour upon clicking the knob
            elif event.type == SLIDER:
                #Updates the volume of the proper sound channel
                pygame.mixer.Channel(event.target).set_volume(event.value / 100.0) #Float value so python doesn't truncate to int like it did for that one CCC question I did that one time (Please don't mark this comment, I just wanted to share my grievance)

            elif event.type == FISHING:
                if event.status == "start":
                    fishing = True
                    status = "luring"
                elif event.status == "snag":
                    status = "reeling"

                elif event.status == "end":
                    #Checks if the player succeeded to catch a fish
                    if event.success == False:
                        for key in fish_list:
                            rng = random.randint(1, 100)
                            if fish_list[key].rate >= rng:
                                active_save["fish"].append(fish_list[key])
                                break

                        #Increments the number of fish caught
                        active_save["caught"] += 1

                    #Ends the minigmae regardless of outcome
                    fishing = False

            elif event.type == QUITTING:
                json.dump(p_flags, open("flag.json", "w"))
                pygame.time.set_timer(pygame.QUIT, 10)

        #Processes bobbing cycle for various objects
        deg += 1
        if deg == 360:
            deg = 0

        #Converts deg to radian
        rad = math.radians(deg)

        #Processes music
        intro = music(sound, intro)

        #Processes screen updating
        update(current_screen, save_slot, button_list, button_call, slider_list, quitting)

        #Specifically handles fishing
        if fishing:
            catch, active_save = fishing(status, active_save, fish_list)

        #Processes screen drawing
        draw(entity, current_screen, save_slot, button_list, button_call, slider_list, text_list, text_call, rad, scroll)

        pygame.display.update()

#Run! along with all the requisite data
save_status = main(persistent_flags, save_data, entity)
print(save_status)