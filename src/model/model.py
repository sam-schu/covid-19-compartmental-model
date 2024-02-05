"""
Contains the internal data model of the COVID-19 simulation.

Classes:
    Model - the COVID-19 simulation model.
"""

import math
import random
import bisect

from model import agent
from model.agent import Compartment, Agent


class Model:
    """
    Represents the data model for the simulation.
    
    The model tracks information about each agent and the overall state
    of the simulation. The model should be updated by calling its tick
    method, rather than calling the tick method on the agents directly.
    
    Class constants:
        MASK_TRANSMISSION_FACTOR - the relative probability of an agent
            *transmitting* (not contracting) COVID-19 when wearing a
            mask, compared to when not wearing a mask. (Independent of
            the Agent class's MASK_INFECTION_FACTOR, which affects the
            probability of contracting the virus when wearing a mask.)
    
    Instance variables:
        ticks_to_simulate - the number of times the tick method can be
            called before the simulation_running method returns False.
        infection_distance - the maximum Euclidean (straight-line)
            distance between two agents (according to their internal
            position) such that they can still attempt to infect one
            another.
        num_agents - the number of agents being simulated. (read-only
            property)
        tick_count - the number of times the tick method has been called
            so far. (read-only property)
        peak_cases - the maximum number of cases that have been present
            at the same time so far. (read-only property)
    """
    
    # Non-public instance variables:
    #    _agents - the list of Agent objects representing the agents
    #        being simulated.
    
    # The value used for this constant is the result of research
    # conducted in November and December 2020.
    MASK_TRANSMISSION_FACTOR = 0.24
    
    def __init__(self, grid_side_length, days_to_simulate,
                 percent_wearing_masks, percent_self_isolating,
                 infection_distance):
        """
        Create the model.
        
        Arguments:
            grid_side_length - the side length (in number of agents) of
                the square grid of agents to be modeled. (For example,
                if grid_side_length is 10, then 10 x 10 = 100 agents,
                arranged in a square 10 x 10 grid, will be modeled.)
            days_to_simulate - the number of simulated days the model
                should run for. Specifically, after the tick method has
                been called agent.TICKS_PER_DAY * days_to_simulate
                times, the simulation_running method will return False.
            percent_wearing_masks - the percentage of agents that should
                wear masks (affecting their probability of transmitting
                and contracting COVID-19).
            percent_self_isolating - the percentage of agents that
                should self-isolate if they become symptomatic (meaning
                they cannot move or infect other agents during the
                isolation period).
            infection_distance - the maximum Euclidean (straight-line)
                distance between two agents (according to their internal
                position) such that they can still attempt to infect one
                another.
            
        Create a grid of agents as specified by the given arguments, and
        space them by 2 * INFECTION_DISTANCE in each direction.
        """
        self.ticks_to_simulate = days_to_simulate * agent.TICKS_PER_DAY
        self.infection_distance = infection_distance

        self._num_agents = grid_side_length * grid_side_length
        num_agents_wearing_masks = round(
            (percent_wearing_masks / 100) * self._num_agents)
        num_agents_self_isolating = round(
            (percent_self_isolating / 100) * self._num_agents)
        
        # Create a randomly ordered list where True corresponds to the
        # agent at that position wearing a mask and False corresponds to
        # the agent at that position not wearing a mask, with the total
        # number of True and False matching the number of agents who
        # were determined to be wearing masks.
        has_mask_list = [True if i < num_agents_wearing_masks else False
                         for i in range(self._num_agents)]
        random.shuffle(has_mask_list)
        
        # Create a randomly ordered list where True corresponds to the
        # agent at that position self-isolating upon becoming
        # symptomatic and False corresponds to the agent at that
        # position not self-isolating upon becoming symptomatic, with
        # the total number of True and False matching the number of
        # agents who were determined to self-isolate upon becoming
        # symptomatic.
        should_isolate_list = [True if i < num_agents_self_isolating
                               else False for i in
                               range(self._num_agents)]
        random.shuffle(should_isolate_list)
        
        # Determine the index of the agent that will be created to be
        # initially infectious, which is the agent at the center of the
        # grid (or one of the agents closest to the center of the grid
        # if the grid side length is even).
        infectious_agent_index = (round((grid_side_length - 1) / 2)
                                  * grid_side_length
                                  + round((grid_side_length - 1) / 2))
        
        # Create the list of Agents based on the previously determined
        # parameters. Agents' x and y positions are such that they are
        # spaced by 2 * INFECTION_DISTANCE in each direction (meaning
        # that if the view is used, their visual square representations
        # are spaced by INFECTION_DISTANCE in each direction).
        self._agents = [Agent(
            self.infection_distance * (2 * (i % grid_side_length)
                                       - (grid_side_length - 1)),
            self.infection_distance * (2 * (i // grid_side_length)
                                       - (grid_side_length - 1)),
            has_mask_list[i], should_isolate_list[i],
            True if i == infectious_agent_index else False)
            for i in range(self._num_agents)]
        
        self._tick_count = 0
        self._peak_cases = 1
    
    @property
    def num_agents(self):
        """Get the number of agents simulated. (read-only property)"""
        return self._num_agents
    
    def get_agents(self):
        """Get a copy of the list of Agents simulated."""
        return list(self._agents)
    
    @property
    def tick_count(self):
        """
        Get the current tick count. (read-only property)
        
        Get the number of times the tick method has been called so far.
        """
        return self._tick_count
    
    @property
    def peak_cases(self):
        """
        Get the peak number of cases so far. (read-only property)
        
        Get the maximum number of cases that have been present at the
        same time so far.
        """
        return self._peak_cases
    
    def days_elapsed(self):
        """
        Get the number of days that have been simulated so far.
        
        The number of days simulated so far is the current tick count
        divided by agent.TICKS_PER_DAY, then rounded down.
        """
        return self._tick_count // agent.TICKS_PER_DAY
    
    def simulation_running(self):
        """
        Get whether the simulation is currently running.
        
        The simulation is currently running iff the current tick count
        is less than the number of ticks to simulate, as determined by
        the __init__ method (based on its days_to_simulate argument).
        """
        return self._tick_count < self.ticks_to_simulate
    
    def tick(self):
        """
        Update the state of the model.
        
        First, attempt to infect any agents that are close enough to an
        infectious agent. Then, update each agent by calling its tick
        method, update the model's peak cases if necessary, and update
        the tick count.
        """
        
        # Sort the list of agents by compartment so that binary search
        # can be used to quickly find the lower and upper index bounds
        # of the group of susceptible agents and the group of
        # infectious agents.
        self._agents.sort(key=lambda ag: ag.compartment.value)

        susceptible_agents = self._agents[0:bisect.bisect_right(
            self._agents, 0, key=lambda ag: ag.compartment.value)]
        susceptible_agents.sort(key=lambda ag: ag.x)
        susceptible_agents_x_pos = [ag.x for ag in susceptible_agents]

        infectious_left_index = bisect.bisect_left(
            self._agents, 2, key=lambda ag: ag.compartment.value)
        infectious_right_index = bisect.bisect_right(
            self._agents, 2, key=lambda ag: ag.compartment.value)

        # For each infectious agent, attempt to infect any susceptible
        # agents within the infection distance of it.
        for i in range(infectious_left_index, infectious_right_index):
            ag = self._agents[i]
            if not ag.is_isolating:
                # Determine the lower (inclusive) and upper (exclusive)
                # index bounds of the susceptible agents who are within
                # the infection distance of ag (an infectious agent) in
                # x.
                susceptible_left_index = bisect.bisect_left(
                    susceptible_agents_x_pos, ag.x - self.infection_distance)
                susceptible_right_index = bisect.bisect_right(
                    susceptible_agents_x_pos, ag.x + self.infection_distance)
                # Loop through only these agents, as it is impossible
                # for two agents to be within the infection distance of
                # each other if their x positions are not.
                for j in range(susceptible_left_index,
                               susceptible_right_index):
                    a = susceptible_agents[j]
                    # If the two agents are within a distance of the
                    # infection distance of each other, attempt to
                    # infect the susceptible agent.
                    if math.sqrt((a.x - ag.x) * (a.x - ag.x) + (a.y - ag.y)
                                 * (a.y - ag.y)) <= self.infection_distance:
                        # If the infectious agent is wearing a mask, the
                        # probability of their transmitting the virus is
                        # reduced.
                        if ag.has_mask:
                            if (random.random()
                                    < Model.MASK_TRANSMISSION_FACTOR):
                                a.contact()
                        else:
                            a.contact()
    
        # Update each agent's position and current state of infection,
        # and count to determine whether the peak number of cases has
        # been broken.
        current_cases = 0
        for ag in self._agents:
            ag.tick()
            if (ag.compartment is Compartment.EXPOSED
                    or ag.compartment is Compartment.INFECTIOUS):
                current_cases += 1
        
        if current_cases > self._peak_cases:
            self._peak_cases = current_cases
        
        self._tick_count += 1
    
    def get_simulation_stats(self):
        """
        Get current statistics about the simulation run by the model.
        
        Return a tuple consisting of the total number of cases, the
        total number of deaths, and the peak number of cases in the
        simulation. (The peak number of cases is updated when the
        model's tick method is called.)
        """
        num_cases = 0
        num_deaths = 0
        
        for ag in self._agents:
            num_cases += ag.num_infections
            if ag.compartment is Compartment.DECEASED:
                num_deaths += 1
        
        return num_cases, num_deaths, self._peak_cases
