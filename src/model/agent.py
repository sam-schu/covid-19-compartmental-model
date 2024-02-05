"""
Contains a constant and classes relating to model's individual agents.

Note that a "tick" is the unit of time representing how often agents
are updated by calling their tick method. If a graphical display is
used, one frame should correspond to one tick.

Module constants:
    TICKS_PER_DAY - the number of ticks used to model one day.

Classes:
    Compartment - an Enum representing an agent's model compartment.
    Agent - a single agent (simulated person) in the model.
"""

import math
import random
from enum import Enum

TICKS_PER_DAY = 4 * 24  # 1 tick models 15 minutes

Compartment = Enum("Compartment", (("SUSCEPTIBLE", 0), ("EXPOSED", 1),
                                   ("INFECTIOUS", 2), ("RECOVERED", 3),
                                   ("DECEASED", 4)))
"""
Represents an agent's compartment in the model. Subclass of Enum.

Compartments are subgroups used to categorize the current stage of
infection of agents in the model.

Additional methods: none

Additional enum class constants: SUSCEPTIBLE (value 0), EXPOSED (value
    1), INFECTIOUS (value 2), RECOVERED (value 3), DECEASED (value 4)
"""


class Agent:
    """
    Represents an agent (modeled person) in the compartmental model.
    
    Class constants:
        INFECTION_PROBABILITY - the base probability (as a decimal, not
            taking masks into account) of being infected if the contact
            method is called.
        INCUBATION_MIN_TICKS - the minimum possible number of ticks
            needed for an agent to become symptomatic after becoming
            exposed.
        INCUBATION_MAX_TICKS - the maximum possible number of ticks
            needed for an agent to become symptomatic after becoming
            exposed.
        ASYMPTOMATIC_PROBABILITY - the probability (as a decimal) of a
            particular case being asymptomatic (meaning the agent will
            not show symptoms for the entire duration of the case).
        MASK_INFECTION_FACTOR - the factor by which to multiply the
            base probability of being infected if the agent potentially
            becoming infected is wearing a mask.
        TICKS_INFECTIOUS_AFTER_SYMPTOMATIC - the number of ticks that
            an agent will be infectious for after showing symptoms (for
            a symptomatic case) or after they would show symptoms if
            their case were not asymptomatic (for an asymptomatic
            case).
        TICKS_IMMUNE - the number of ticks for which an agent will be
            immune from future cases after being infected (measured
            from the time they become infected).
        TICKS_INFECTIOUS_BEFORE_SYMPTOMATIC - the number of ticks for
            which an agent will be infectious before they are
            calculated to become symptomatic (unless using this full
            value would suggest that the agent should be infectious
            before they even contracted the virus).
        CHANCE_OF_DEATH - the probability (as a decimal) that an agent
            will die from their case of the virus.
    
    Instance variables:
        x - the current x position of the agent.
        y - the current y position of the agent.
        is_isolating - whether or not the agent is currently self-
            isolating, meaning that they do not move when the tick
            method is called and that they should not be allowed to
            infect other agents. (read-only property)
        compartment - the agent's current Compartment in the
            compartmental epidemic model. (read-only property)
        num_infections - a counter for the total number of times the
            agent has been infected. Initially set to 0; is incremented
            every time the agent is infected (including if they are
            created to be initially infected).
        is_asymptomatic - whether or not the agent's current or last
            infection is/was an asymptomatic case. Does not indicate
            whether or not the agent is actually showing symptoms. If
            this value is True, the agent will not be able to self-
            isolate when they should become symptomatic, even if
            should_isolate is True. Initially set to True if the agent
            is created to be initially infected, or False otherwise.
        has_mask - whether or not the agent is wearing a mask. If so,
            their chance of contracting the virus in the contact method
            will be multiplied by MASK_INFECTION_FACTOR.
        should_isolate - whether or not the agent should self-isolate if
            they become symptomatic (meaning that the agent has a non-
            asymptomatic case and enough time has passed for them to
            become symptomatic).
    
    Notes:
        1. If the agent has an asymptomatic case, they will not become
            symptomatic even after INCUBATION_MAX_TICKS ticks have
            elapsed. However, the time when they would have become
            symptomatic if their case were not asymptomatic is still
            used as a basis for certain calculations, such as the
            timing of their infectious period.
        2. TICKS_INFECTIOUS_AFTER_SYMPTOMATIC also represents the
            length of self-isolation (in ticks), as self-isolation (if
            applicable) starts when an agent becomes symptomatic and
            ends when they stop being infectious.
        3. The scale of x and y coordinates is arbitrary.
    """
    
    # Non-public instance variables:
    #    _future_compartment - the compartment that the agent will move
    #        to at the end of the current or next call to the tick
    #        method.
    #    _immunity_ticks_left - the number of ticks of immunity that
    #        the agent has left (this value will still tick down even
    #        if the agent is currently infected). This value's being
    #        greater than 0 does not necessarily mean that the agent is
    #        currently immune and not infected, but if the agent is
    #        currently recovered and they run out of immunity ticks,
    #        they will become susceptible again.
    #    _ticks_before_symptomatic - the number of ticks that the agent
    #        has left before they start showing symptoms if their case
    #        is not asymptomatic. May be negative after this time has
    #        passed. A zero or negative value is possible when the
    #        agent is or is not currently infected.
    #    _ticks_before_infectious - the number of ticks that the agent
    #        has left before they become infectious. May be negative
    #        after this time has passed. A zero or negative value is
    #        possible when the agent is or is not currently infected.
    #    _ticks_infectious_left - the number of ticks that the agent
    #        has left until they are no longer infectious. Only
    #        applicable when the agent is symptomatic or would be
    #        symptomatic if their case were not asymptomatic.
    
    # The values used for these constants are the result of research
    # conducted in November and December 2020.
    INFECTION_PROBABILITY = 0.037
    INCUBATION_MIN_TICKS = 2 * TICKS_PER_DAY
    INCUBATION_MAX_TICKS = 14 * TICKS_PER_DAY
    ASYMPTOMATIC_PROBABILITY = 0.20
    MASK_INFECTION_FACTOR = 0.56
    TICKS_INFECTIOUS_AFTER_SYMPTOMATIC = (
        10 * TICKS_PER_DAY)
    TICKS_IMMUNE = 90 * TICKS_PER_DAY
    TICKS_INFECTIOUS_BEFORE_SYMPTOMATIC = (
        3 * TICKS_PER_DAY)
    CHANCE_OF_DEATH = 321734 / 18170062
    
    def __init__(self, x, y, has_mask, should_isolate, infectious):
        """
        Create the agent.
        
        Arguments:
            x - the initial x position of the agent.
            y - the initial y position of the agent.
            has_mask - whether or not the agent is wearing a mask
                (which multiplies their chance of infection by
                MASK_INFECTION_FACTOR).
            should_isolate - whether or not the agent should self-
                isolate upon becoming symptomatic.
            infectious - whether or not the agent should be created to
                be initially infectious.
        
        The agent will initially not be isolating. If they are created
        to be initially infectious, they are initially in the
        INFECTIOUS compartment, with 1 total infection and an
        asymptomatic case. Otherwise, they are initially in the
        SUSCEPTIBLE compartment, with 0 total infections and without an
        asymptomatic case.
        """
        self.x = x
        self.y = y
        self._is_isolating = False
        
        if infectious:
            self._compartment = Compartment.INFECTIOUS
            self._future_compartment = Compartment.INFECTIOUS
            self.num_infections = 1
            self._immunity_ticks_left = Agent.TICKS_IMMUNE
            self._ticks_before_symptomatic = 3 * TICKS_PER_DAY
            self.is_asymptomatic = True
        else:
            self._compartment = Compartment.SUSCEPTIBLE
            self._future_compartment = Compartment.SUSCEPTIBLE
            self.num_infections = 0
            self._immunity_ticks_left = 0
            self._ticks_before_symptomatic = 0
            self.is_asymptomatic = False
        
        self._ticks_before_infectious = 0
        self._ticks_infectious_left = 0
        
        self.has_mask = has_mask
        self.should_isolate = should_isolate
    
    @property
    def is_isolating(self):
        """
        Get whether the agent is isolating. (read-only property)
        
        Get whether or not the agent is currently self-isolating.
        """
        return self._is_isolating
    
    @property
    def compartment(self):
        """Get the agent's current Compartment. (read-only property)"""
        return self._compartment
    
    def tick(self):
        """
        Update the state of the agent (including their position).
        
        If the agent is currently in the EXPOSED compartment but enough
        ticks have passed for them to become infectious, move them to
        the INFECTIOUS compartment. If the agent is currently in the
        INFECTIOUS compartment and enough ticks have passed for them to
        become symptomatic, the agent was set to self-isolate if they
        became symptomatic, and their case is not asymptomatic, start
        the agent's self-isolation. If the agent is currently in the
        INFECTIOUS compartment, enough ticks have passed for them to
        have already become symptomatic (even if they did not actually
        develop symptoms because their case was asymptomatic), and
        enough ticks have passed for them to no longer be infectious,
        stop their self-isolation if applicable, and randomly assign
        them to either the DECEASED or RECOVERED compartment, based on
        the CHANCE_OF_DEATH. If the agent is currently in the RECOVERED
        compartment and enough ticks have passed for them to no longer
        be immune, move them to the SUSCEPTIBLE compartment.
        
        As long as the agent is not self-isolating and is not in the
        DECEASED compartment, update their x and y coordinates such
        that they are moved 1 unit of Euclidean distance in a random
        direction.
        
        "Ticks" as referred to in this module are a unit relating to
        how often this method is called. This method should be called
        on all agents in a simulation consecutively; when this happens,
        a "tick" has occurred. Whether the amount of time between ticks
        stays consistent does not matter, but all agents should be
        ticked at the same rate, and a shorter interval between ticks
        causes the simulation to run faster.
        """
        if self._compartment is Compartment.EXPOSED:
            self._ticks_before_infectious -= 1
            self._ticks_before_symptomatic -= 1
            if self._ticks_before_infectious == 0:
                self._future_compartment = Compartment.INFECTIOUS
        elif self._compartment is Compartment.INFECTIOUS:
            # This value is decremented even after it reaches 0.
            self._ticks_before_symptomatic -= 1
            # If this is the first tick the agent has symptoms (or
            # would if their case were not asymptomatic)...
            if self._ticks_before_symptomatic == 0:
                self._ticks_infectious_left = (
                    Agent.TICKS_INFECTIOUS_AFTER_SYMPTOMATIC)
                if self.should_isolate and not self.is_asymptomatic:
                    self._is_isolating = True
            elif self._ticks_before_symptomatic < 0:
                self._ticks_infectious_left -= 1
                if self._ticks_infectious_left == 0:
                    self._is_isolating = False
                    if random.random() < Agent.CHANCE_OF_DEATH:
                        self._future_compartment = Compartment.DECEASED
                    else:
                        self._future_compartment = Compartment.RECOVERED
        elif (self._compartment is Compartment.RECOVERED
              and self._immunity_ticks_left == 0):
            self._future_compartment = Compartment.SUSCEPTIBLE
        
        # Self-isolating agents and deceased agents remain in place.
        if (not self._is_isolating
                and self._compartment is not Compartment.DECEASED):
            # Choose a random direction on the unit circle (in
            # radians).
            direction = random.uniform(0, 2 * math.pi)
            # Move the agent to the point 1 unit away from the agent's
            # current position, in the direction previously determined.
            self.x += math.cos(direction)
            self.y += math.sin(direction)
        
        if self._immunity_ticks_left > 0:
            self._immunity_ticks_left -= 1

        self._compartment = self._future_compartment
    
    def contact(self):
        """
        Attempt to infect the agent with the virus.
        
        If the agent is not currently infected and has not been
        successfully infected since the last tick, randomly determine
        whether or not this infection will be successful based on the
        INFECTION_PROBABILITY if the agent is not wearing a mask, or
        the product of the INFECTION_PROBABILITY and the
        MASK_INFECTION_FACTOR if the agent is wearing a mask. If the
        infection is successful, add 1 to the agent's total number of
        infections, and randomly determine whether or not the case is
        asymptomatic based on the ASYMPTOMATIC_PROBABILITY. Randomly
        determine the number of ticks that must pass before the agent
        can become symptomatic, according to a uniform distribution
        based on INCUBATION_MIN_TICKS and INCUBATION_MAX_TICKS. The
        number of ticks that must pass before the agent becomes
        infectious is calculated by subtracting
        TICKS_INFECTIOUS_BEFORE_SYMPTOMATIC from this value. If the
        number of ticks that must pass before the agent becomes
        infectious is zero or negative, they will be moved to the
        INFECTIOUS compartment at the end of the next tick; if it is
        positive, they will be moved to the EXPOSED compartment at the
        end of the next tick.
        """
        
        # If the agent is not infected (including earlier this tick)...
        if self._future_compartment is Compartment.SUSCEPTIBLE:
            transmission_probability = Agent.INFECTION_PROBABILITY
            if self.has_mask:
                transmission_probability *= Agent.MASK_INFECTION_FACTOR
            if random.random() < transmission_probability:
                self.num_infections += 1
                self._immunity_ticks_left = Agent.TICKS_IMMUNE
                if random.random() < Agent.ASYMPTOMATIC_PROBABILITY:
                    self.is_asymptomatic = True
                else:
                    self.is_asymptomatic = False
                self._ticks_before_symptomatic = random.randint(
                    Agent.INCUBATION_MIN_TICKS, Agent.INCUBATION_MAX_TICKS)
                self._ticks_before_infectious = (
                    self._ticks_before_symptomatic
                    - Agent.TICKS_INFECTIOUS_BEFORE_SYMPTOMATIC)
                if self._ticks_before_infectious <= 0:
                    self._future_compartment = Compartment.INFECTIOUS
                else:
                    self._future_compartment = Compartment.EXPOSED
