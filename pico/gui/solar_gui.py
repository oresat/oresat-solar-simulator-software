import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import serial

# ✏️ Update this to match your Pico's second serial port (the one used for `usb_cdc.data`)
# On Windows, it's usually COM4 or higher. Use `python -m serial.tools.list_ports` to check.
ser = serial.Serial('COM11', 115200, timeout=1)

def send_command(channel, value):
    # Convert GUI 0–255 range to 0–65535 for the Pico DAC/PWM
    scaled_value = int(value * 65535 / 255)
    cmd = f"SET {channel.upper()} {scaled_value}\n"
    print(f"Sending: {cmd.strip()}")
    ser.write(cmd.encode('utf-8'))

app = dash.Dash(__name__)
colors = ['violet', 'white', 'cyan', 'halogen']

app.layout = html.Div([
    html.H1("Solar Simulator Controller"),
    *[
        html.Div([
            html.Label(f"{color.capitalize()} Intensity"),
            dcc.Slider(0, 255, step=1, value=0, id=f"{color}-slider"),
        ], style={'marginBottom': '30px'}) for color in colors
    ]
])

# Register slider callbacks
for color in colors:
    app.callback(
        Output(f"{color}-slider", 'value'),
        Input(f"{color}-slider", 'value'),
        prevent_initial_call=True
    )(lambda value, c=color: (send_command(c, value), value)[1])

if __name__ == '__main__':
    app.run(debug=True)
