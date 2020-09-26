#!/usr/bin/env python3

import re, subprocess, os, sys, json, argparse, hashlib, time, glob, pathlib
import http.client
NCPA_PLUGINS_DIR = '/usr/local/ncpa/plugins'
NCPA_ETC_DIR = '/usr/local/ncpa/etc'
NCPA_ETC_FILE_NAME = 'ncpa.cfg'
CHECK_NCPA_AGENT_FILENAME = 'check_ncpa_agent.py'
ALGORITHMS_AVAILABLE = hashlib.algorithms_available if hasattr(hashlib, "algorithms_available") else hashlib.algorithms

parser = argparse.ArgumentParser()

# Specify arguments to the plugin
parser.add_argument('--query_plugins','-q','--query-plugins', dest='query_plugins', default=False, action='store_true', help='Query Agent Plugins',)
parser.add_argument('--monitor_host','-m','--monitor-host', type=str, help='Monitor Host',)
parser.add_argument('--monitor_port','-P','--monitor-port', type=int, help='Monitor Port',)
parser.add_argument('--monitor_prefix','-F','--monitor-prefix', type=str, help='Path Prefix',)
parser.add_argument('--plugin_name','-n','--plugin-name', type=str, help='Plugin Name',)
parser.add_argument('--warning','-w', type=int, help='Warning',)
parser.add_argument('--critical','-c', type=int, help='Critical',)
args = parser.parse_args()
####print(dict(args))

if args.query_plugins:
  file_list = [os.path.basename(f) for f in glob.glob('{}/{}'.format(NCPA_PLUGINS_DIR,'*'))]
  file_hashes = {}
  for f in file_list:
    file_hashes[f] = hashlib.md5(pathlib.Path('{}/{}'.format(NCPA_PLUGINS_DIR,f)).read_bytes()).hexdigest()
  print(json.dumps({
   'plugins': list(file_list),
   'algs': list(ALGORITHMS_AVAILABLE),
   'file_hashes': dict(file_hashes),
  }))
  sys.exit(0)


dat = {'args':args,'env':list(os.environ.keys())}
with open('/tmp/.check_ncpa_agent.log','a') as f:
  f.write(str(dat))
BODY = "***filecontents***"
conn = http.client.HTTPConnection( args.monitor_host, args.monitor_port)
URI = '/{}{}'.format(
  args.monitor_prefix,
  args.plugin_name,
)
conn.request("GET", URI, BODY)
response = conn.getresponse()
print(URI, response.status, response.reason)
data = response.read().decode()
PLUGIN_DEST_PATH = '{}/{}'.format(NCPA_PLUGINS_DIR, args.plugin_name)
msg = 'Read {data_len} bytes for {args.plugin_name} and writing to {PLUGIN_DEST_PATH}'.format(
    data_len=len(data),
    args=args,
    PLUGIN_DEST_PATH=PLUGIN_DEST_PATH,
)
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
print('read {data_len} bytes'.format(data_len=len(data)))





"""
def get_ncpa_cfg():
    return '{}/{}'.format(
        NCPA_ETC_DIR,
        NCPA_ETC_FILE_NAME,
    )

def read_ncpa_cfg():
    return with open(get_ncpa_cfg(),'r') as f:
        return f.read().decode()
"""


