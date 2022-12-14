import numpy as np, matplotlib, matplotlib.pyplot as plt, PySimpleGUI as sg, socket, time, _thread
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.use("TkAgg")

# Create functions.

def draw_3D_graph(canvas, graph):
    """
    Description:

    Draws the 3D graph in the GUI.

    Parameters:

    canvas      ; The window and key the graph should be drawn on.

    graph       ; A graph of type matplotlib.figure().

    Returns:

    graph_3D    ; the 3D graph drawn onto the chosen key in the window.
    """
    # Draw graph
    graph_3D = FigureCanvasTkAgg(graph, canvas)
    graph_3D.draw()
    graph_3D.get_tk_widget().pack(side="top", fill="both", expand=1)

    return graph_3D


def delete_graph(graph):
    """
    Description:

    Deletes the drawn graph.

    Parameters:

    graph       ; The graph to be deleted.
    """
    fig.get_tk_widget().forget()
    plt.close('all')
    
    
def create_3D_graph(data_lat, data_long, data_RSSI):
    """
    Description:

    Create a 3D scatter plot, that displays the parameters as (data_lat (x), data_long (y), data_RSSI (z))

    Parameters:

    data_lat        ; List of floats, (x).

    data_long       ; List of floats, (y).

    data_RSSI       ; List of floats, each between 0 and -255, (z).

    Returns:

    graph       ; The scatterplot created in the function.
    """
    graph = plt.figure()
    ax = plt.axes(projection='3d')
    ax.scatter(data_lat, data_long, data_RSSI, c=data_RSSI, cmap='viridis', linewidth=0.5)

    return graph

# Create a list for the incoming data, from the pico.
data_list = [[]]

# Assign a variable to the TCP client.
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  

# Assign the host and port, that the data will be streaming through.
host = '192.168.4.1'
port = 12345

server_socket_address = (host, port)

# Create a header_list for the tables in the GUI.
header_list = ['Index', 'Latitude', 'Longitude', 'RSSI', 'Direction went']

# Assign some more variables.
eval_data = []
location_guess = []
decoded_data = ''
fig_gui = None
draw = False
first = True
data_lat = []
data_long = []
data_RSSI = []

# Set the theme of the gui, this is actually mainly so we can actually see the unchecked checkbox, since its color cannot be changed.
sg.theme('DarkGrey6')

# Assign the layout of inputs in the gui to a variable.
input_layout = [[sg.Button('', disabled=True, button_color='grey25', border_width=0)],[sg.Input('network', key = '-ssid.input-', size = (10, 10))],
                [sg.Spin(values = [i for i in range(1, 1000)], key = '-scan_amount.spin-', size = (5, 0), initial_value=5)], 
                [sg.Spin(values = [i for i in range(1, 1000)], key = '-gps_read_amount.spin-', size = (5, 0), initial_value=10)]]

# Assign the general layout of the gui to a variable.
layout = [[sg.Button('Connect',key = "-connect.to.pico-"), sg.Checkbox("",default=False, disabled=True, key='-check-'),sg.Text('', key = '-connecting.text-')],
          [sg.Text('Wi-Fi ssid:')],
          [sg.Text('Wi-Fi scan amount:')], 
          [sg.Text('GPS read amount:')],
          [sg.Button('Find Jammer', key = "-find.jammer.button-", disabled=True)], 
          [sg.Text('', key = '-error.text-')]]

# Assign the data containers in the gui to a variable.
data_layout = [[sg.Text('Location Guess', font=('', 12))],
               [sg.Table(headings = header_list[0:4], values = location_guess, key = '-location.table-', visible = True, justification = 'right', 
                     col_widths = [7, 11], auto_size_columns = False, sbar_background_color='grey25', num_rows=1, alternating_row_color='grey20')], 
               [sg.Text('')],
               [sg.Text('Data Table', font=('', 12))],
               [sg.Table(headings = header_list, values = eval_data, key = '-data.table-', visible = True, justification = 'right', 
                     col_widths = [7, 11], auto_size_columns = False, sbar_background_color='grey25', num_rows=8, alternating_row_color='grey20')],
               [sg.Button('Show RSSI heatmap', key = "-graph.button-")],
               [sg.Canvas(key = '-graph-')]]

# Assign the complete layout of he gui to a variable.
final_layout = [[sg.Column(layout, vertical_alignment = 'c'), sg.Column(input_layout, vertical_alignment = 'top')], data_layout]

# Create the gui window.
window = sg.Window('Jammer locator', layout = final_layout,
                    finalize = True,
                    element_justification='left')

# Run the reading button presses and inputs etc.
while True:
    event, values = window.read()
    
    # Try to connect to the pico W's access point, if an exception occurs print this in the gui.
    if event == '-connect.to.pico-':
        try:
            client_socket.connect(server_socket_address)
            window['-check-'].Update(True)
            window['-connect.to.pico-'].Update(disabled=True)
            window['-find.jammer.button-'].Update(disabled=False)
            window['-connecting.text-'].Update('')

        except Exception as error:
            window['-connecting.text-'].Update('Did not connect!')

    # If the find jammer button is pressed.
    if event == '-find.jammer.button-':
        
        # Empty the data_list, the one assigned in the beginning of the code is only used to generate an empty graph, 
        # only if that button is pressed before the find jammer button is pressed.
        data_list = []
        network_message = 0

        while True:
            # If the inputs and spins are not empty, stitch a string together with config at the start, and send it to the pico W, 
            # to configurate the program.
            if (str(values['-ssid.input-']) != '') and (str(values['-scan_amount.spin-']) != '') and (str(values['-gps_read_amount.spin-']) != ''):
                if network_message == 0:
                    window['-error.text-'].Update('')
                    config_message = f"config {str(values['-ssid.input-'])} {str(values['-scan_amount.spin-'])} {str(values['-gps_read_amount.spin-'])}"
                    client_socket.sendall(bytes(config_message, 'utf-8'))
                    window['-find.jammer.button-'].Update(disabled=True)
                    # Add one to the network message, so a config message is not send twice.
                    network_message += 1
                    window.refresh()
                else:
                    # Reply to the pico W TCP server, saying that we are ready for new data to be send.
                    client_socket.sendall(b'Send data!')
            else:
                # If the spin and inputs fields have not been filled print an error in the gui.
                window['-error.text-'].Update('Fill missing fields!', background_color='red', text_color = 'black')
                break
            
            # Receive data from the pico W TCP server, of a total size of 128 bytes. 
            # Since the received message is send using utf-8 encoding, each normal symbol is equivalent to 1 byte.
            received_data_packet = client_socket.recv(128)
            decoded_data = received_data_packet.decode('utf-8')
            # If the message from the pico W TCP server includes the string 'finished', when the program is done and the socket should close.
            if "finished" in decoded_data:
                client_socket.close()
                break
            # If the message does not include 'finished', perform data operations.
            else:
                try:
                    # Evaluate the data so it becomes a list, since it was send as one.
                    eval_data = eval(decoded_data)

                    # Append the list to another list.
                    data_list.append(eval_data)

                    # Sort the data list received from the PicoW, sorting by the RSSI value closest to 0.
                    data_sorted = sorted(data_list, key= lambda RSSI : RSSI[3], reverse=True)

                    # Take the data_sorted and put the data with the smallest rssi value in another list.
                    location_guess = [[data_sorted[0][0], data_sorted[0][1], data_sorted[0][2], data_sorted[0][3]]]

                    # Add the location_guess to a the location guess table and update its values so the closets value is the one shown.
                    window['-location.table-'].Update(values=location_guess)

                    # Append the different values from the data_list to seperate lists,
                    # this is because plt.scatter wants three seperate lists with x, y, z and not a tuple for each point containg (x, y, z).
                    data_lat.append(data_list[-1][-4])
                    data_long.append(data_list[-1][-3])
                    data_RSSI.append(data_list[-1][-2])

                    # Update the normal table with these values
                    window['-data.table-'].Update(values=data_list)

                    # If the show RSSI heatmap button has been pressed, 
                    # update the graph each time a new data point is received from the pico W TCP server.
                    if draw == True:
                        if fig_gui != None:
                            delete_graph(fig_gui)

                        # Create the scatter plot graph, using lists containing x, y, z.
                        fig = create_3D_graph(data_lat, data_long, data_RSSI)
                        fig_gui = draw_3D_graph(window['-graph-'].TKCanvas, fig)

                    # Refresh the window so the values are shown in the gui and the plot if chosen.
                    window.refresh()
                except Exception as a:
                    None

    # If the show rssi heatmap button is pressed.
    if event == '-graph.button-':
        # If draw is false draw the entire graph.
        if draw == False:
            # Delete the graph if it exit.
            if fig_gui != None:
                delete_graph(fig_gui)
            
            # Make a new graph and set draw to true.
            fig = create_3D_graph(data_lat, data_long, data_RSSI)
            fig_gui = draw_3D_graph(window['-graph-'].TKCanvas, fig)
            draw = True

        # if draw is True delete the graph if it exit and set draw to false.
        else:
            if fig_gui != None:
                delete_graph(fig_gui)
            draw = False

    # if the window is closed, close the client socket and sever the connection.
    if event == sg.WIN_CLOSED:
        time.sleep(1)
        client_socket.close()
        break

# If the while loop has ended, it means the gui was closed, because of this close all graphs and close the gui window.
plt.close('all')
window.close()