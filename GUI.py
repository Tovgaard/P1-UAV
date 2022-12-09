import numpy as np, matplotlib, matplotlib.pyplot as plt, PySimpleGUI as sg, socket, time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from operator import itemgetter
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
    
    
def make_fig(x,y):
    """
    Makes figure with plot
    """
    
    def f(x, y):
        return np.sin(np.sqrt(x ** 2 + y ** 2))

    x = np.linspace(-6, 6, 30)
    y = np.linspace(-6, 6, 30)

    X, Y = np.meshgrid(x, y)
    Z = f(X, Y)
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.contour3D(X, Y, Z, 50, cmap='binary')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    
    return fig

data_list = []

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  

host = '192.168.4.1'    # ip of raspberry pi pico W
port = 12345

close_server = False

connected = False

header_list = ['Latitude', 'Longitude', 'RSSI']

eval_data = []

sg.theme('DarkGrey6')

layout = [[sg.Text('')], [sg.Button('Find Jammer', key = "-start.button-")],
          [sg.Button('Connect',key = "-connect.to.pico-"), sg.Checkbox("",default=False, disabled=True, key='-check-')],
          [sg.Button('Emergency landing',key = "-emergency_landing-")],
          [sg.Button('Coordinates of jammer', key = "location"),sg.Table(headings = header_list, values = eval_data, key = '-data.table-', visible = True, justification = 'right', 
                     col_widths = [7, 11], auto_size_columns = False, sbar_background_color='grey25', num_rows=8, alternating_row_color='grey20')],
           [sg.Button('Show jammer', key = "-graph.button-")],
           [sg.Canvas(key = '-graph-')]]


window = sg.Window('Location of jammer',
                    layout = layout,
                    finalize = True,
                    element_justification='left')

fig_gui = None
"""
while connected == False:
    try:
        client_socket.connect((host, port))
        connected = True
    except Exception as error:
        print(error, 'try again')
        time.sleep(1)
"""
while True:
    event, values = window.read()

    if event == '-connect.to.pico-':
        while connected == False:
            try:
                client_socket.connect((host, port))
                window['-check-'].Update(True)
                connected = True
            except Exception as error:
                time.sleep(0.5)

    if event == '-graph.button-':
        if fig_gui != None:
            delete_fig(fig_gui)
        
        x = np.linspace(-6, 6, 30)
        y = np.linspace(-6, 6, 30)
        
        
        fig = make_fig(x,y)
        fig_gui = draw_figure(window['-graph-'].TKCanvas, fig)


    if event == '-start.button-':
        while True:
            event, values = window.read(timeout=150)
            
            # Emergency button
            if event == '-emergency_landing-':
                client_socket.sendall(b'emergency') # Send an emergency message, if an emergency occured.

            client_socket.sendall(b'Send data!')
            received_data_packet = client_socket.recv(64)
            decoded_data = received_data_packet.decode('utf-8')
            sg.Print(decoded_data)
            if "finished" in decoded_data:
                client_socket.close()
                sg.Print('DONE closing socket!')
                break

            else:
                try:
                    eval_data = eval(decoded_data)
                    data_list.append(eval_data)

                    data_list = sorted(data_list, key= lambda RSSI : RSSI[2], reverse=True)

                    window['-data.table-'].Update(header_list)
                    window['-data.table-'].Update(values=data_list)

                except Exception as a:
                    print(a)

    if event == sg.WIN_CLOSED:
        try:
            client_socket.sendall(b'exit')
            client_socket.close()
        except Exception:
            None

        break

plt.close('all')
window.close()


#heatmap agtig plot
"""
def f(x, y):
    return np.sin(np.sqrt(x ** 2 + y ** 2))

theta = 2 * np.pi * np.random.random(1000)
r = 6 * np.random.random(1000)
x = np.ravel(r * np.sin(theta))
y = np.ravel(r * np.cos(theta))
z = f(x, y)
fig = plt.figure()
ax = plt.axes(projection='3d')
ax.scatter(x, y, z, c=z, cmap='viridis', linewidth=0.5);
"""

# HEATMAP https://stackoverflow.com/questions/33282368/plotting-a-2d-heatmap

#scatter plot
"""
np.random.seed(19680801)


def randrange(n, vmin, vmax):
    return (vmax - vmin)*np.random.rand(n) + vmin

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

n = 100

# For each set of style and range settings, plot n random points in the box
# defined by x in [23, 32], y in [0, 100], z in [zlow, zhigh].
for m, zlow, zhigh in [('o', -50, -25), ('^', -30, -5)]:
    xs = randrange(n, 23, 32)
    ys = randrange(n, 0, 100)
    zs = randrange(n, zlow, zhigh)
    ax.scatter(xs, ys, zs, marker=m)

ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')
"""





