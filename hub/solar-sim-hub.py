import socketio
import eventlet
import argparse
import json
from debugdata import pwm_vals

# Load Config File
with open('options.conf', 'r') as jsonfile:
    data = json.load(jsonfile)
    # print('config loaded')

# Initialize ArgParse
parser = argparse.ArgumentParser(prog='solar-sim-server', description='oresat-solar-simulator server node', 
                                 epilog='https://github.com/oresat/oresat-solar-simulator')

parser.add_argument('-p', '--port', type=int, help='port hub is listening on',
                     required=False, default=data['port'])
parser.add_argument('-r', '--refresh',type=float, help='sets refresh rate in seconds', 
                    required=False, default=data['refresh-rate'])
parser.add_argument('clients', type=int, help='number of simulator clients connected',
                    choices=range(1,5), default=4)
parser.add_argument('-v', '--verbose', help='verbose mode',
                    action='store_true')
parser.add_argument('-s', '--simple', help='uses simple rotation rather than basilisk model',
                    action='store_true')

args = parser.parse_args()

# Setup SocketIO
sio = socketio.Server(logger=False, async_mode= 'eventlet')

# Dictionary to store client identifiers and corresponding sids
global client_sids 
client_sids = {}

simulators_running = False
verbose = args.verbose
if verbose:
    print('Verbose Mode Enabled!')


def ping_in_intervals():
    '''
    Primary server loop. Reads data from the source and emits a message to each client to set their PWM value.
    '''
    i = 0
    while True:
        if simulators_running:
            for client in client_sids:
                sio.emit('pwm_comm', pwm_vals[i][client], room=client_sids[client])
        else:
            print(f'{len(client_sids)} connected')
        i += 1
        if i >= len(pwm_vals):
            i = 0
        print(f'\nsending: {pwm_vals[i]}')
        print('received:')
        sio.sleep(1)
            # with open('output_file', 'r') as f:
            #     pwm_data = f.readline()
            #     print(pwm_data)
            #     sio.emit('pwm_comm', pwm_data)
            #     sio.sleep(0.1)

@sio.event
def connect(sid, environ):
    '''
    Executed upon client connect
    '''
    global simulators_running
    print('Client connected:', sid)
    if len(client_sids) == args.clients:
        simulators_running = True

@sio.event
def disconnect(sid):    
    '''
    Executred upon client disconnect.
    '''
    global client_sids; simulators_running
    print('Client disconnected:', sid)
    client_sids = {key:val for key, val in client_sids.items() if val != sid}
    simulators_running = False

    
@sio.event
def set_sid(sid, client_id):
    '''
    Message sent by client to set its client_id.
    '''
    print('Setting sid for client:', client_id)
    client_sids[client_id] = sid
    # print(client_sids)
    sio.emit('response',f'User {client_id} was added succesfully!!', room=sid)
        
    
@sio.event
def panel_response(sid, data):
    '''
    Message sent by client with photodiode and thermister data.

    :param sid: session id sending the message
    :param data: list containing client_id of sender, temp data, and photo data 
    TODO: Will need to do processing here.
    '''
    print(data)

if __name__ == '__main__':
    app = socketio.WSGIApp(sio)
    thread = sio.start_background_task(ping_in_intervals)
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', args.port)), app) 
    
