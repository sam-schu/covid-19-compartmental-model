"""
A script to run the COVID-19 compartmental model.

To run the model, simply execute the script, and the command
line interface will ask for the side length of the agent grid, the
number of days to simulate, the percentage of agents who should wear
masks, the percentage of agents who should self-isolate upon becoming
symptomatic, and whether the simulation should be displayed. When the
simulation is complete, the command line output will provide the total
number of COVID-19 cases, the total number of deaths from COVID-19, and
the peak number of cases at a single time.

If the user chooses to display the simulation, a window will appear that
allows it to be viewed as it runs. The running display includes the
total number of agents, the number of frames that have elapsed, and the
number of days that have been modeled so far, as well as a rendering of
each agent at its current position. Pressing (and holding) the W, A, S,
or D key will move the display camera up, left, down, or right,
respectively; pressing and releasing the R key will reset the display to
its original position.

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

Module constants:
    INFECTION_DISTANCE - the maximum Euclidean (straight-line) distance
        between two agents (according to their internal position) such
        that they can still attempt to infect one another.

All variables and functions in this module should be considered
private.
"""

from model.model import Model
from view import View

INFECTION_DISTANCE = 5


def input_num(min_value, max_value, conversion_func):
    """
    Input, convert, validate, and return a number from the console.

    No initial input prompt is printed. If the conversion or validation
    fails, an error message is printed, and input is requested again
    until a valid input is provided, at which point the converted valid
    input is returned.

    Arguments:
        min_value - the minimum (converted) input value that should be
            considered valid. If None, the input is not checked
            against a minimum value.
        max_value - the maximum (converted) input value that should be
            considered valid. If None, the input is not checked
            against a maximum value.
        conversion_func - the function that should be used to convert
            the user input to a numeric format. The function must take
            a string and return a number; specifically, the return
            value must be comparable to min_value and max_value using
            numeric comparison operators. The function must raise a
            ValueError or an ArithmeticError if the conversion is not
            possible.
    """
    while True:
        try:
            user_input = conversion_func(input())
            if ((min_value is None or user_input >= min_value)
                    and (max_value is None or user_input <= max_value)):
                return user_input
        except (ValueError, ArithmeticError):
            pass
        
        print("Invalid input; please try again.")


def input_yes_no():
    """
    Input, validate, and return a yes/no response from the console.

    True is returned to represent a "yes" response, and False is
    returned to represent "no". Capitalization and leading and
    trailing whitespace are ignored. If the validation fails, an error
    message is printed, and input is requested again until a valid
    input is provided.
    """
    while True:
        user_input = input().lower().strip()
        if user_input == "yes":
            return True
        elif user_input == "no":
            return False
        else:
            print("Invalid input; please try again.")


# Input the necessary parameters from the user.

print("Hello, and welcome to the COVID-19 Compartmental Epidemic "
      + "Model!\n")
print("The agents in the model will be arranged in a square grid.")
print("Please enter the side length (in agents) of this grid:")

grid_side_length = input_num(1, None, int)

print("Please enter the number of days that you would like to")
print("simulate (as a whole number):")

days_to_simulate = input_num(1, None, int)

print("Please enter the percentage of agents who you would like")
print("to wear masks (from 0 to 100):")

percent_wearing_masks = input_num(0, 100, float)

print("Please enter the percentage of agents who you would like to")
print("self-isolate upon the development of COVID-19 symptoms (from 0 ")
print("to 100):")

percent_self_isolating = input_num(0, 100, float)

print('Would you like the progress of the simulation to be displayed')
print('visually while it runs? This will make the simulation take')
print('longer to run. Please enter "yes" or "no":')

should_display_simulation = input_yes_no()

model = Model(grid_side_length, days_to_simulate,
              percent_wearing_masks, percent_self_isolating,
              INFECTION_DISTANCE)

if should_display_simulation:
    view = View(model)

print("\nSimulation running...")

view_closed = False

while not view_closed:
    if should_display_simulation:
        view_closed = view.update()
    
    if not model.simulation_running():
        # Handle the end of the simulation, including counting total
        # cases and deaths.
        num_cases, num_deaths, peak_cases = model.get_simulation_stats()
        
        print("\nSimulation complete!")
        print("Total number of cases:", num_cases)
        print("Total number of deaths:", num_deaths)
        print("Peak number of cases:", peak_cases)
        
        break
    
    model.tick()

if should_display_simulation:
    view.quit()
