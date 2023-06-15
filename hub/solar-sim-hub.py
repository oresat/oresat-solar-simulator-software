import socketio
import eventlet
import argparse
import json

# Load Config File
with open('hub-options.conf', 'r') as jsonfile:
    data = json.load(jsonfile)
    # print('config loaded')

# Initialize ArgParse
parser = argparse.ArgumentParser(prog='solar-sim-server', description='oresat-solar-simulator server node', 
                                 epilog='https://github.com/oresat/oresat-solar-simulator')

parser.add_argument('-f', '--file', type=str, help='uses simple rotation rather than basilisk model',
                    required=False, default='out.json')
parser.add_argument('-p', '--port', type=int, help='port hub is listening on',
                     required=False, default=data['port'])
parser.add_argument('-r', '--refresh',type=float, help='sets refresh rate in seconds', 
                    required=False, default=data['refresh-rate'])
parser.add_argument('clients', type=int, help='number of simulator clients connected',
                    choices=range(1,5), default=4)
parser.add_argument('-v', '--verbose', help='verbose mode',
                    action='store_true')
parser.add_argument('-s', '--safe', help='engages safe mode, limits output and turns UV off',
                    action='store_true')

args = parser.parse_args()

# Setup SocketIO
sio = socketio.Server(logger=False, async_mode= 'eventlet')

# Dictionary to store client identifiers and corresponding sids
global client_sids 
client_sids = {}



def ping_in_intervals():
    '''
    Primary server loop. Reads data from the source and emits a message to each client to set their PWM value.
    '''
    current_state = -1
    i = 0
    while True:
        if new_state != current_state:
            current_state = new_state
            sio.emit('set_state', current_state, room=any)
        if len(client_sids) == args.clients:
            for client in client_sids:
                sio.emit('pwm_comm', pwm_vals[f'{client}'][i], room=client_sids[client])
                if verbose:
                    print(f"\nsending: 0:{pwm_vals['0'][i]} 1:{pwm_vals['1'][i]} 2:{pwm_vals['2'][i]} 3:{pwm_vals['3'][i]}")
                    print('received:')
        else:
            if verbose:
                print(f'{len(client_sids)} connected, waiting for {args.clients}')
        if verbose:
            print(f'Current state: {current_state}')

        i += 1
        if i >= len(pwm_vals['0']):
            i = 0
        sio.sleep(1)

@sio.event
def connect(sid, environ):
    '''
    Executed upon client connect
    '''
    if verbose:
        print('Client connected:', sid)

@sio.event
def disconnect(sid):    
    '''
    Executred upon client disconnect.
    '''
    global client_sids
    if verbose:
        print('Client disconnected:', sid)
    client_sids = {key:val for key, val in client_sids.items() if val != sid}

    
@sio.event
def set_sid(sid, client_id):
    '''
    Message sent by client to set its client_id.
    '''
    if verbose:
        print('Setting sid for client:', client_id)
    client_sids[client_id] = sid
    # print(client_sids)
    sio.emit('response',f'User {client_id} added', room=sid)
        
    
@sio.event
def panel_response(sid, data):
    '''
    Message sent by client with photodiode and thermister data.

    :param sid: session id sending the message
    :param data: list containing client_id of sender, temp data, and photo data 
    TODO: Will need to do processing here.
    '''
    global new_state
    bad_state = False
    if verbose:
        print(data)
    if bad_state:
        new_state = 0

if __name__ == '__main__':
    system_halt = False
    verbose = args.verbose
    if args.safe:
        running_mode = 2
    else:
        running_mode = 1
    new_state = running_mode
    if verbose:
        print('Verbose Mode Enabled!')

    # Load data    
    with open(args.file, 'r') as jsonfile:
        pwm_vals = json.load(jsonfile)
        if verbose:
            print(f"Loaded data from {args.file}")
        
    app = socketio.WSGIApp(sio)
    thread = sio.start_background_task(ping_in_intervals)
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', args.port)), app) 
    
