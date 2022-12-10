import numpy as np, matplotlib, matplotlib.pyplot as plt, PySimpleGUI as sg, socket, time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.use("TkAgg")

def draw_figure(canvas, figure):
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
    
    
def make_fig(data_list):
    """
    Makes figure with plot
    """

    lat, long, rssi = zip(*data_list)

    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.scatter(lat, long, rssi, c=rssi, cmap='viridis', linewidth=0.5)

    return fig


data_list = [[0, 0, 0]]

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  

host = '192.168.4.1'    # ip of raspberry pi pico W
port = 12345

server_address = (host, port)

header_list = ['Latitude', 'Longitude', 'RSSI']

eval_data = []

decoded_data = ''

fig_gui = None

draw = False

sg.theme('DarkGrey6')

input_layout = [[sg.Input('network', key = '-ssid.input-', size = (10, 10))],
                [sg.Input('5', key = '-scan_amount.input-', size = (10, 10))], 
                [sg.Input('8', key = '-gps_read_amount.input-', size = (10, 10))]]

layout = [[sg.Button('Connect',key = "-connect.to.pico-"), sg.Checkbox("",default=False, disabled=True, key='-check-'),sg.Text('', key = '-connecting.text-')],
          [sg.Text('Wi-Fi ssid:')],
          [sg.Text('Wi-Fi scan amount:')], 
          [sg.Text('GPS read amount:')],
          [sg.Button('Find Jammer', key = "-find.jammer.button-", disabled=True)], 
          [sg.Text('', key = '-error.text-')]]

data_layout = [[sg.Button('Emergency landing',key = "-emergency_landing-")],
               [sg.Table(headings = header_list, values = eval_data, key = '-data.table-', visible = True, justification = 'right', 
                     col_widths = [7, 11], auto_size_columns = False, sbar_background_color='grey25', num_rows=8, alternating_row_color='grey20')],
               [sg.Button('Show RSSI heatmap', key = "-graph.button-")],
               [sg.Canvas(key = '-graph-')]]

final_layout = [[sg.Column(layout, vertical_alignment = 'c'), sg.Column(input_layout, vertical_alignment = 'c')], data_layout]

window = sg.Window('Jammer locator',
                    layout = final_layout,
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
            window.Element('-connecting.text-').Update('')

        except Exception as error:
            window.Element('-connecting.text-').Update('Did not connect!')

    if event == '-find.jammer.button-':

        data_list = []
        network_message = 0


        while True:
            if (str(values['-ssid.input-']) != '') and (str(values['-scan_amount.input-']) != '') and (str(values['-gps_read_amount.input-']) != ''):
                if network_message == 0:
                    window.Element('-error.text-').Update('')
                    config_message = f"network {str(values['-ssid.input-'])} {str(values['-scan_amount.input-'])} {str(values['-gps_read_amount.input-'])}"
                    client_socket.sendall(bytes(config_message, 'utf-8'))
                    window['-find.jammer.button-'].Update(disabled=True)
                    network_message += 1
                else:
                    client_socket.sendall(b'Send data!')
            else:
                window.Element('-error.text-').Update('Fill missing fields!', background_color='red', text_color = 'black')
                break

            received_data_packet = client_socket.recv(128)
            decoded_data = received_data_packet.decode('utf-8')

            if "finished" in decoded_data:
                client_socket.close()
                break
            else:

                try:
                    eval_data = eval(decoded_data)
                    data_list.append(eval_data)

                    # Sort the data list received from the PicoW, sorting by the largest value, but in reverse.
                    data_list = sorted(data_list, key= lambda RSSI : RSSI[2], reverse=True)

                    window['-data.table-'].Update(header_list)
                    window['-data.table-'].Update(values=data_list)

                    
                    if draw == True:
                        if fig_gui != None:
                            delete_fig(fig_gui)
             
                        fig = make_fig(data_list)
                        fig_gui = draw_figure(window['-graph-'].TKCanvas, fig)

                    window.refresh()


                except Exception as a:
                    None

    if event == '-graph.button-':
        if draw == False:
            if fig_gui != None:
                delete_fig(fig_gui)
            
            fig = make_fig(data_list)
            fig_gui = draw_figure(window['-graph-'].TKCanvas, fig)
            draw = True

        elif draw == True:
            if fig_gui != None:
                delete_fig(fig_gui)
            draw = False



    if event == sg.WIN_CLOSED:
        client_socket.close()
        break

plt.close('all')
window.close()
