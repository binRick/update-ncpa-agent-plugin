#!/usr/bin/python3

import re, subprocess, os, sys, json, argparse, hashlib, time
import http.client
NCPA_PLUGINS_DIR = '/usr/local/ncpa/plugins'
CHECK_NCPA_AGENT_FILENAME = 'check_ncpa_agent.py'
ALGORITHMS_AVAILABLE = hashlib.algorithms_available if hasattr(hashlib, "algorithms_available") else hashlib.algorithms

parser = argparse.ArgumentParser()

# Specify arguments to the plugin
parser.add_argument('--monitor_host','-m','--monitor-host', type=str, help='Monitor Host',)
parser.add_argument('--monitor_port','-P','--monitor-port', type=int, help='Monitor Port',)
parser.add_argument('--plugin_name','-n','--plugin-name', type=str, help='Plugin Name',)
parser.add_argument('--warning','-w', type=int, help='Warning',)
parser.add_argument('--critical','-c', type=int, help='Critical',)
args = parser.parse_args()
print(dict(args))

dat = {'args':args,'env':list(os.environ.keys())}
with open('/tmp/.check_ncpa_agent.log','a') as f:
  f.write(str(dat))
BODY = "***filecontents***"
conn = http.client.HTTPConnection( args.monitor_host, args.monitor_port)
URI = '/{}'.format(
  args.plugin_name,
)
conn.request("GET", URI, BODY)
response = conn.getresponse()
print(URI, response.status, response.reason)
data = response.read().decode()
PLUGIN_DEST_PATH = '{}/{}'.format(NCPA_PLUGINS_DIR, args.plugin_name)
msg = f'Read {len(data)} bytes for {args.plugin_name} and writing to {PLUGIN_DEST_PATH}'
#sys.stderr.write(msg+"\n")
if response.status == 200:
    with open(PLUGIN_DEST_PATH, 'w') as f:
      f.write(data)
    os.chmod(PLUGIN_DEST_PATH, 0o755)
    print('Read {} bytes for {} => {}'.format(len(data),args.plugin_name,PLUGIN_DEST_PATH))
    sys.exit(0)
else:
    print('Failed to update plugin {} => HTTP Code {}'.format(args.plugin_name,response.status))
    sys.exit(2)

#print(dir(response))
print(f'read {len(data)} bytes')





