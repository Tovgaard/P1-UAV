# Aau project 1, Networking and programming

import PySimpleGUI as gui, time
from djitellopy import tello

# Initialize and connect drone.
drone = tello.Tello()
drone.connect()

# Create the GUI, and window
layout = [[gui.Text('Flyv og land tello drone')],
          [gui.Button('Takeoff', key = '-button.takeoff-'), 
           gui.Button('Land', key = '-button.land-')]]

window = gui.Window('Network Probe', layout = layout, finalize = True, element_justification='center')


while True:
    event, values = window.read()
    
    # When button takeoff is pressed -> drone takeoff
    if event == '-button.takeoff-':
        try:
            print('Flyver nu!')
            drone.is_flying = True
            # Moves a minimum of 20cm, when using directions.
            drone.move('up', 20)
            time.sleep(1)
        except:
            print('Fejl ved fly op')

    # When button land is pressed -> drone land
    if event == '-button.land-':
        try:
            print('Lander nu!')
            drone.send_control_command("land", 0)
            drone.is_flying = False
            time.sleep(1)
        except:
            print("Fejl ved landing")
    
    if event == gui.WIN_CLOSED:

        # (failsafe) If window is closed while mid air -> drone land
        if drone.is_flying == True:
            drone.land()
            break
        else:
            break
