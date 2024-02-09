# COVID-19 Compartmental Epidemic Model

A simplified compartmental disease model (with
optional visual display) to
simulate the spread of COVID-19 through a population, and the effects of
masks and self-isolation on this spread.

[View a demonstration video here!](https://www.youtube.com/watch?v=OvAe2XQ7rRM)

### Purpose

This program does not aim to be a fully accurate simulation of the
real-world spread of the virus causing COVID-19. Rather, it
serves as an easily understandable
demonstration of virus spread through a population and the positive
impact that can be achieved through virus control measures employed
during the COVID-19 pandemic — namely, mask-wearing and self-isolation.

### Getting Started

First, make sure you have installed the pygame package for your Python
interpreter. Then, to run the program, simply execute main_script.py and
follow the input prompts in the console. You will be able to choose the
number of agents simulated, the amount of time simulated, the
proportions of agents wearing masks and willing to self-isolate, and
whether to show the visual simulation display. Note that agents wearing
masks have a decreased chance of transmitting and contracting COVID-19,
and that self-isolation (which can only be triggered if an agent
contracts a symptomatic case) causes an agent to stop moving and stop
being able to transmit the virus. After you have inputted the necessary
parameters, the simulation (as well as the
visual display if enabled) will start automatically, and the simulation
statistics (total cases, total deaths, and peak cases) will be printed
in the console when the simulation is
complete. *Please note that enabling the visual display may
significantly increase the amount of time needed for the simulation to
run.*

### Key Terminology

- **Tick:** a single unit of time. Each tick, the model (including all
its agents) is updated, and the view is updated if it is enabled.
- **Agent:** an object representing a single person in the simulation.
- **Compartment:** a category agents can be assigned to representing
their infection status.

### Program Description

The program simulates the spread of COVID-19 through a
hypothetical group of agents who are initially arranged in a square
grid, and then move in a random direction each tick. For
each tick that two agents are close enough to each other, an infectious
agent has a chance to infect a susceptible agent. This is not possible
if the infectious agent is self-isolating, and the chance of infection
is reduced if the infectious or susceptible agent is wearing a mask.
Once an agent is infected, they will become infectious after a certain
period of time, and they will also potentially become symptomatic
after a period of time; some agents will self-isolate upon
showing symptoms, meaning that they can no longer move or infect other
agents. After enough time has passed, an infected agent will either die
or recover with temporary immunity. The size of the agent grid,
simulated time, percentage of agents wearing masks, and percentage of
agents self-isolating upon becoming symptomatic are customizable by the
user. After the simulation ends, the total number of cases, total number
of deaths, and peak number of cases at any one time are displayed.

The visual display is an optional feature of the program that allows the
user to see the progress of the simulation as it is running. If enabled,
the visual display appears as a separate window when the simulation
starts, and it is updated every tick (one display frame equals one model
tick). Each agent is displayed as a small square, and whether two
agents' display squares overlap can be used as a rough approximation for
whether they are close enough for one to be able to infect the other.
The following color key is used when drawing the agents:

* **Susceptible:** white
* **Exposed:** yellow
* **Infectious:**
    * light red if the agent is not self-isolating and the case is /
      will be symptomatic
    * dark red if the agent is not self-isolating and the case is / will
      be asymptomatic
    * dark blue if the agent is self-isolating
* **Recovered:** light green
* **Deceased:** dark gray

The display also shows the total number of agents, the number of
frames that have elapsed so far, and the number of simulated full days
that have passed so far. The W, A, S, and D keys can be used to move the
display camera up, left, down, and right, respectively; the R key can be
used to reset the camera to its default position.

### Project Structure

This project is structured based on a modified version of the
model-view-controller (MVC) architecture. Specifically, the model and
the view are separated both to ensure that either could be modified in
the future without needing to alter the other, and so that the
simulation
can be run with only the model (the view consists only of the visual
simulation display, and is not involved with console input/output).
After the initial setup code, the main script serves the function of a
simple controller; no explicit controller was designed because of the
additional complexity this would add for the implementation of the very
basic mouse and
keyboard actions used in the view, which are not likely to change.

Within the model package, the agent.py file contains the Agent class,
which represents a single
simulated agent, while the model.py file is concerned with updating all
the agents in the simulation, handling virus transmission between
agents, and keeping track of overall simulation statistics. The project
also contains two top-level source files: view.py and main_script.py.
view.py
contains the View class, which represents the simulation display window
and also handles keyboard and mouse inputs to the window. main_script.py
is the script that handles important pre- and post-simulation tasks,
such as getting the necessary inputs from the user and printing
simulation statistics, as well as coordinating the process of updating
the model and view.
