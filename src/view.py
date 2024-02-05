"""
Contains a GUI view for the COVID-19 simulation.

Classes:
    View - the COVID-19 simulation view.
"""

# Hide the Pygame welcome message.
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame
from pygame.locals import K_w, K_a, K_s, K_d, K_r

from model.agent import Compartment


class View:
    """
    Represents a visual, windowed view for the simulation.
    
    Initializing a View object will cause the view window to appear on
    the screen. The view shows the current state of the simulation as it
    runs. The display includes the total number of agents, the number of
    frames that have elapsed, and the number of days that have been
    modeled so far, as well as a rendering of each agent at its current
    position. Pressing (and holding) the W, A, S, or D key will move the
    display camera up, left, down, or right, respectively; pressing and
    releasing the R key will reset the camera to its original position.
    
    The following is a color key for each agent in the model display:
        Susceptible:    white
        Exposed:        yellow
        Infectious:     light red if the agent is not self-isolating and
                            the case is / will be symptomatic
                        dark red if the agent is not self-isolating and
                            the case is / will be asymptomatic
                        dark blue if the agent is self-isolating
        Recovered:      light green
        Deceased:       dark gray
    
    Class constants:
        WINDOW_WIDTH - the width of the view window, in pixels.
        WINDOW_HEIGHT - the height of the view window, in pixels.
        SCROLL_PER_MS - the number of pixels to move the camera in a
            particular direction for every millisecond the corresponding
            scroll key is held down on the keyboard.
    """
    
    # Non-public instance variables:
    #    _model - the model to be displayed by this view.
    #    _display_window - the pygame Surface representing the view
    #        window.
    #    _text_font - the pygame Font object used to render text onto
    #        the view window.
    #    _total_agents_text - a pygame Surface object representing the
    #        text displayed to show the total number of agents modeled.
    #    _clock - the pygame Clock object used to keep track of time
    #        deltas between frames for consistent-speed scrolling.
    #    _x_offset - the value to add (in pixels) to the x position at
    #        which each agent is being rendered to account for
    #        scrolling.
    #    _y_offset - the value to add (in pixels) to the y position at
    #        which each agent is being rendered to account for
    #        scrolling.
    
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    SCROLL_PER_MS = 0.1
    
    def __init__(self, model):
        """
        Create the view.
        
        Arguments:
            model - the model representing the simulation to be
                displayed.
        
        Calling this method causes the view window to appear on the
        screen.
        """
        self._model = model
        
        # Initialize pygame and set up the display window.
        pygame.init()
        self._display_window = pygame.display.set_mode(
            (View.WINDOW_WIDTH, View.WINDOW_HEIGHT))
        pygame.display.set_caption("COVID-19 Compartmental Epidemic Model")
        self._text_font = pygame.font.SysFont("Calibri", 18)
        self._total_agents_text = self._text_font.render(
            "Total agents: " + str(self._model.num_agents), True,
            pygame.Color("white"), pygame.Color("black"))
        
        # Set up variables needed to allow the user to move around the
        # model display with the WASD keys. Offsets are for the display
        # of agents, not for their actual internal positions. (The clock
        # is used to keep track of time deltas between frames.)
        self._clock = pygame.time.Clock()
        self._x_offset = 0
        self._y_offset = 0
    
    def update(self):
        """
        Update the view to represent the current simulation state.
        
        Render each agent as a square at its current position, offset
        based on the current screen scroll, in the color specified by
        the class documentation (based on the agent's compartment and
        state); also render the total agent count and the updated frame
        count and day count. Additionally, if the user releases the R
        key, reset the screen scroll, and if the W, A, S, or D key is
        being pressed, move the display camera up, left, down, or right,
        respectively. Return True if the user has pressed the X button
        on the window to close it, and False otherwise.
        
        This method should be called after every tick of the model. It
        should not be called after the quit method is called.
        """
        self._display_window.fill(pygame.Color("black"))
        
        for ag in self._model.get_agents():
            if ag.compartment is Compartment.SUSCEPTIBLE:
                color = pygame.Color("white")
            elif ag.compartment is Compartment.EXPOSED:
                color = pygame.Color("yellow")
            elif ag.compartment is Compartment.INFECTIOUS:
                if ag.is_isolating:
                    color = pygame.Color("blue")
                else:
                    if ag.is_asymptomatic:
                        color = pygame.Color("darkred")
                    else:
                        color = pygame.Color("red")
            elif ag.compartment is Compartment.RECOVERED:
                color = pygame.Color("green")
            elif ag.compartment is Compartment.DECEASED:
                color = pygame.Color("gray40")
            
            # Draw the agent onto the screen.
            pygame.draw.rect(
                self._display_window, color,
                (round(ag.x - (self._model.infection_distance / 2)
                       + (View.WINDOW_WIDTH / 2) + self._x_offset),
                 round(ag.y - (self._model.infection_distance / 2)
                       + (View.WINDOW_HEIGHT / 2) + self._y_offset),
                 self._model.infection_distance,
                 self._model.infection_distance))
        
        # Display the total number of agents, number of frames elapsed,
        # and number of days modeled on the screen.
        frame_count_text = self._text_font.render(
            "Frames passed: " + str(self._model.tick_count), True,
            pygame.Color("white"), pygame.Color("black"))
        day_count_text = self._text_font.render(
            "Days modeled: " + str(self._model.days_elapsed()), True,
            pygame.Color("white"), pygame.Color("black"))
        self._display_window.blits(
            ((self._total_agents_text, (View.WINDOW_WIDTH - 160, 20)),
             (frame_count_text, (View.WINDOW_WIDTH - 180, 40)),
             (day_count_text, (View.WINDOW_WIDTH - 176, 60))))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            # If the user presses the X button on the window, return
            # True to indicate that the program should be quit.
            if event.type == pygame.QUIT:
                return True
            # If the user releases the R key, reset the screen scroll.
            elif event.type == pygame.KEYUP and event.key == K_r:
                self._x_offset = 0
                self._y_offset = 0
        
        # Scroll the screen if W, A, S, or D is pressed.
        key_seq = pygame.key.get_pressed()
        dt = self._clock.tick()  # the number of ms since the last frame
        if key_seq[K_w]:
            self._y_offset += View.SCROLL_PER_MS * dt
        if key_seq[K_s]:
            self._y_offset -= View.SCROLL_PER_MS * dt
        if key_seq[K_a]:
            self._x_offset += View.SCROLL_PER_MS * dt
        if key_seq[K_d]:
            self._x_offset -= View.SCROLL_PER_MS * dt
        
        return False
    
    def quit(self):
        """
        Call pygame's quit method, closing the view window.
        
        Once this method is called, the update method should not be
        called.
        """
        pygame.quit()
