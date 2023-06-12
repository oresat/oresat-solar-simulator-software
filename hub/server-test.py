import argparse
import json

with open('server-options.conf', 'r') as jsonfile:
    data = json.load(jsonfile)
    # print('config loaded')


parser = argparse.ArgumentParser(prog='solar-sim-server', description='oresat-solar-simulator server node', 
                                 epilog='https://github.com/oresat/oresat-solar-simulator')


parser.add_argument('-r', '--refresh',type=float, help='sets refresh rate in seconds', 
                    required=False, default=data['refresh-rate'])
parser.add_argument('clients', type=int, help='number of simulator clients connected',
                    choices=range(1,5), default=4)
parser.add_argument('-v', '--verbose', help='verbose mode',
                    action='store_true')
parser.add_argument('-s', '--simple', help='uses simple rotation rather than basilisk model',
                    action='store_true')

args = parser.parse_args()
print(f"arg value: {args}")
print(f"conf value: {data}")
