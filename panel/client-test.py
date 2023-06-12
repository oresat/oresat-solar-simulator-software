import argparse
import json

with open('client-options.conf', 'r') as jsonfile:
    data = json.load(jsonfile)
    # print('config loaded')


parser = argparse.ArgumentParser(prog='solar-sim-client', description='oresat-solar-simulator client node', 
                                 epilog='https://github.com/oresat/oresat-solar-simulator')


parser.add_argument('-i', '--ipaddress',type=str, help='ip-address of the server', 
                    required=False, default=data['server-ip'], metavar='192.168.X.2')
parser.add_argument('-c', '--clientid', type=int, help='id the client will report to server', 
                    required=False, default=data['client-id'], choices=range(0,4))

args = parser.parse_args()
print(f"arg value: {args.ipaddress}")
print(f"conf value: {data['server-ip']}")

server_id = args.ipaddress
client_id = args.clientid

print(f'server_id: {server_id}')
print(f'client_id: {client_id}')