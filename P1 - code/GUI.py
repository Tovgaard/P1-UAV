import numpy as np, matplotlib, matplotlib.pyplot as plt, PySimpleGUI as sg, socket, time, _thread
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.use("TkAgg")

def draw_3D_graph(canvas, figure):
    """
    Draws figure on canvas for GUI
    """
    
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg

def delete_fig(fig):
    """
    Deletes figure from plot
    """
    fig.get_tk_widget().forget()
    plt.close('all')
    
    
def make_fig(data_lat, data_long, data_RSSI):
    """
    Makes figure with plot
    """
    
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.scatter(data_lat, data_long, data_RSSI, c=data_RSSI, cmap='viridis', linewidth=0.5)

    return fig

# Dummy list
data_list = [[]]

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  

host = '192.168.4.1'    # ip of raspberry pi pico W.
port = 12345

server_address = (host, port)

header_list = ['Index', 'Latitude', 'Longitude', 'RSSI', 'Direction went']

eval_data = []

location_guess = []

decoded_data = ''

fig_gui = None

draw = False

first = True

data_lat = []
data_long = []
data_RSSI = []

sg.theme('DarkGrey6')

input_layout = [[sg.Button('', disabled=True, button_color='grey25', border_width=0)],[sg.Input('network', key = '-ssid.input-', size = (10, 10))],
                [sg.Spin(values = [i for i in range(1, 1000)], key = '-scan_amount.spin-', size = (5, 0), initial_value=5)], 
                [sg.Spin(values = [i for i in range(1, 1000)], key = '-gps_read_amount.spin-', size = (5, 0), initial_value=10)]]

layout = [[sg.Button('Connect',key = "-connect.to.pico-"), sg.Checkbox("",default=False, disabled=True, key='-check-'),sg.Text('', key = '-connecting.text-')],
          [sg.Text('Wi-Fi ssid:')],
          [sg.Text('Wi-Fi scan amount:')], 
          [sg.Text('GPS read amount:')],
          [sg.Button('Find Jammer', key = "-find.jammer.button-", disabled=True)], 
          [sg.Text('', key = '-error.text-')]]

data_layout = [[sg.Text('Location Guess', font=('', 12))],
               [sg.Table(headings = header_list[0:4], values = location_guess, key = '-location.table-', visible = True, justification = 'right', 
                     col_widths = [7, 11], auto_size_columns = False, sbar_background_color='grey25', num_rows=1, alternating_row_color='grey20')], 
               [sg.Text('')],
               [sg.Text('Data Table', font=('', 12))],
               [sg.Table(headings = header_list, values = eval_data, key = '-data.table-', visible = True, justification = 'right', 
                     col_widths = [7, 11], auto_size_columns = False, sbar_background_color='grey25', num_rows=8, alternating_row_color='grey20')],
               [sg.Button('Show RSSI heatmap', key = "-graph.button-")],
               [sg.Canvas(key = '-graph-')]]

final_layout = [[sg.Column(layout, vertical_alignment = 'c'), sg.Column(input_layout, vertical_alignment = 'top')], data_layout]

window = sg.Window('Jammer locator', layout = final_layout,
                    finalize = True,
                    element_justification='left')

while True:
    event, values = window.read()
    
    if event == '-connect.to.pico-':
        try:
            client_socket.connect((host, port))
            window['-check-'].Update(True)
            window['-connect.to.pico-'].Update(disabled=True)
            window['-find.jammer.button-'].Update(disabled=False)
            window['-connecting.text-'].Update('')

        except Exception as error:
            window['-connecting.text-'].Update('Did not connect!')

    if event == '-find.jammer.button-':

        data_list = []
        network_message = 0

        while True:
            if (str(values['-ssid.input-']) != '') and (str(values['-scan_amount.spin-']) != '') and (str(values['-gps_read_amount.spin-']) != ''):
                if network_message == 0:
                    window['-error.text-'].Update('')
                    config_message = f"config {str(values['-ssid.input-'])} {str(values['-scan_amount.spin-'])} {str(values['-gps_read_amount.spin-'])}"
                    client_socket.sendall(bytes(config_message, 'utf-8'))
                    window['-find.jammer.button-'].Update(disabled=True)
                    network_message += 1
                    print(config_message)
                else:
                    client_socket.sendall(b'Send data!')
            else:
                window['-error.text-'].Update('Fill missing fields!', background_color='red', text_color = 'black')
                break

            received_data_packet = client_socket.recv(128)
            decoded_data = received_data_packet.decode('utf-8')

            if "finished" in decoded_data:
                # DEBUG
                print('finished')
                client_socket.close()
                break

            else:
                try:
                    eval_data = eval(decoded_data)
                    data_list.append(eval_data)

                    # Sort the data list received from the PicoW, sorting by the largest value, but in reverse.
                    data_sorted = sorted(data_list, key= lambda RSSI : RSSI[3], reverse=True)

                    location_guess = [[data_sorted[0][0], data_sorted[0][1], data_sorted[0][2], data_sorted[0][3]]]

                    data_lat.append(data_list[-1][-4])
                    data_long.append(data_list[-1][-3])
                    data_RSSI.append(data_list[-1][-2])

                    window['-location.table-'].Update(values=location_guess)

                    window['-data.table-'].Update(values=data_list)

                    
                    if draw == True:
                        if fig_gui != None:
                            delete_fig(fig_gui)
             
                        fig = make_fig(data_lat, data_long, data_RSSI)
                        fig_gui = draw_3D_graph(window['-graph-'].TKCanvas, fig)

                    window.refresh()


                except Exception as a:
                    None

    if event == '-graph.button-':
        if draw == False:
            if fig_gui != None:
                delete_fig(fig_gui)
            
            fig = make_fig(data_lat, data_long, data_RSSI)
            fig_gui = draw_3D_graph(window['-graph-'].TKCanvas, fig)
            draw = True

        elif draw == True:
            if fig_gui != None:
                delete_fig(fig_gui)
            draw = False

    if event == sg.WIN_CLOSED:
        time.sleep(1)
        client_socket.close()
        break

plt.close('all')
window.close()