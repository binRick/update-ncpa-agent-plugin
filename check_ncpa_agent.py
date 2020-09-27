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
parser.add_argument('--query_plugins_mode','-M','--query-plugins-mode', dest='query_plugins_mode', default=False, required=False, help='Query Agent Plugins Mode',)
parser.add_argument('--monitor_host','-m','--monitor-host', type=str, help='Monitor Host',)
parser.add_argument('--monitor_port','-P','--monitor-port', type=int, help='Monitor Port',)
parser.add_argument('--monitor_prefix','-F','--monitor-prefix', type=str, help='Path Prefix',)
parser.add_argument('--plugin_name','-n','--plugin-name', type=str, help='Plugin Name',)
parser.add_argument('--warning','-w', type=int, help='Warning',)
parser.add_argument('--critical','-c', type=int, help='Critical',)
args = parser.parse_args()
####print(dict(args))

def get_ncpa_cfg():
    return '{}/{}'.format(
        NCPA_ETC_DIR,
        NCPA_ETC_FILE_NAME,
    )

def read_ncpa_cfg():
  with open(get_ncpa_cfg(),'r') as f:
    return f.read()

def get_run_with_sudos():
  S = []
  for l in str(read_ncpa_cfg()).splitlines():
    if l.lstrip().startswith('run_with_sudo '):
      S.append(l)
  return S

if args.query_plugins:
  plugins = [os.path.basename(f) for f in glob.glob('{}/{}'.format(NCPA_PLUGINS_DIR,'*'))]
  file_hashes = {}
  for f in plugins:
    file_hashes[f] = hashlib.md5(pathlib.Path('{}/{}'.format(NCPA_PLUGINS_DIR,f)).read_bytes()).hexdigest()
  sudo_plugins = []
  sudos = get_run_with_sudos()
  if len(sudos) > 0:
    SUDO = sudos.pop()
    ss = SUDO.split('=')
    if len(ss) == 2 and ss[0].strip() == 'run_with_sudo':
      sudo_plugins = ss[1].strip().split(',')

  if args.query_plugins_mode == 'plugins':
    print('OK- {plugins_qty} Plugins|plugins_qty={plugins_qty};;;;\n'.format(
      plugins_qty=len(plugins),
    )+"\n".join(plugins))
  elif args.query_plugins_mode == 'sudo_plugins':
    print('OK- {sudo_plugins_qty} Sudo Plugins|sudo_plugins_qty={sudo_plugins_qty};;;;\n'.format(
      sudo_plugins_qty=len(sudo_plugins),
    )+"\n".join(sudo_plugins))
  else:
    print('OK- NCPA Agent Active|plugins_qty={plugins_qty};;;;sudo_plugins_qty={sudo_plugins_qty};;;;\n'.format(
        plugins_qty=len(plugins),            
        sudo_plugins_qty=len(sudo_plugins),            
       )+json.dumps({
     'plugins': list(plugins),
     'sudo_plugins': list(sudo_plugins),
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
data = response.read()

ef =  '{}/{}'.format(NCPA_PLUGINS_DIR, args.plugin_name)
if os.path.exists(ef):
  h = hashlib.md5(ef).read_bytes().encode().hexdigest()
  print('OK- plugin exists already with hash {} :: {}'.format(h, args.plugin_name))
  sys.exit(0)

PLUGIN_DEST_PATH = '{}/{}'.format(NCPA_PLUGINS_DIR, args.plugin_name)
msg = 'OK- Read {data_len} bytes for {args.plugin_name} and wrote to {PLUGIN_DEST_PATH}'.format(
    data_len=len(data),
    args=args,
    PLUGIN_DEST_PATH=PLUGIN_DEST_PATH,
)
#sys.stderr.write(msg+"\n")
if response.status == 200:
    with open(PLUGIN_DEST_PATH, 'wb') as f:
      f.write(data)
    os.chmod(PLUGIN_DEST_PATH, 0o755)
    print('OK- Read {} bytes for {} => {}'.format(len(data),args.plugin_name,PLUGIN_DEST_PATH))
    sys.exit(0)
else:
    print('CRITICAL- Failed to update plugin {} => HTTP Code {}'.format(args.plugin_name,response.status))
    sys.exit(2)

