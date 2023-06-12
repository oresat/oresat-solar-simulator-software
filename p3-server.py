import getopt
import sys
import socketio
import eventlet

from debugdata import pwm_vals

sio = socketio.Server(logger=False, async_mode= 'eventlet')
verbose = False

port = 8000 #port to listen on

print(pwm_vals)

# Dictionary to store client identifiers and corresponding sids
global client_sids #dictionary to hold the PB_ID and their sid
client_sids = {}

command_list = [''] #list to store the command
PB_ID = [] #array to store the id of the PB
try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:vc:i:", ["help", "output=","command=", "ID="])
except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        sys.exit(2)
output = None
verbose = False
for o, a in opts:
    if o == "-v":
        verbose = True
    elif o in ("-h", "--help"):
        #usage()
        sys.exit()
    elif o in ("-c", "--command"):
        command = a
        print('Arg is:',a)
        command_list[0] = a #adding the command to a list
        print("CMD",command_list)
    elif o in ("-i","--ID"):
        ID = a #for PB number
        PB_ID = a
        print("PB ID: ",PB_ID[0])
    elif o in ("-o", "--output"):
        output = a
    else:
        assert False, "unhandled option"

def ping_in_intervals():
    '''
    Primary server loop. Reads data from the source and emits a message to each client to set their PWM value.
    '''
    i = 0
    while True:
        if len(client_sids) == 4:
            for client in client_sids:
                sio.emit('pwm_comm', pwm_vals[i][client], room=client_sids[client])
        else:
            print(f'{len(client_sids)} connected')
        i += 1
        if i >= len(pwm_vals):
            i = 0
        # print(i)
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
    Executred upon client connect.
    '''
    print('Client connected:', sid)

@sio.event
def disconnect(sid):    
    '''
    Executred upon client disconnect.
    '''
    global client_sids
    print('Client disconnected:', sid)
    command_list = '' #clean up
    client_sids = {key:val for key, val in client_sids.items() if val != sid}

    
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
def sim_response(sid, data):
    '''
    Message sent by client with photodiode and thermister data.
    TODO: Will need to do processing here.
    '''
    print(data)

if __name__ == '__main__':
    app = socketio.WSGIApp(sio)
    thread = sio.start_background_task(ping_in_intervals)
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', port)), app) 
    
