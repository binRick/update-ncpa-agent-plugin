#!/usr/bin/python3

import re, subprocess, os, sys, json
from pynag import Plugins
from pynag.Plugins import simple as Plugin
import http.client
NCPA_PLUGINS_DIR = '/usr/local/ncpa/plugins'
CHECK_NCPA_AGENT_FILENAME = 'check_ncpa_agent.py'
DEFAULT_CHRONYD_PORT = 323

plugin = Plugin()

# Specify arguments to the plugin
plugin.add_arg('m', 'monitor_host', 'Monitor Hostname', required=True)
plugin.add_arg('P', 'monitor_port', 'Monitor Hostname', required=True)
plugin.add_arg('n', 'plugin_name', 'Plugin Name', required=True)

plugin.activate()
dat = dict(os.environ)
with open('/tmp/.check_ncpa_agent.log','a') as f:
  f.write(str(dat))
BODY = "***filecontents***"
conn = http.client.HTTPConnection( plugin['monitor_host'], plugin['monitor_port'])
conn.request("GET", f"/{plugin['plugin_name']}", BODY)
response = conn.getresponse()
print(response.status, response.reason)
data = response.read()
PLUGIN_DEST_PATH = '{}/{}'.format(NCPA_PLUGINS_DIR,plugin['plugin_name'])
if response.status == 200:
    with open(PLUGIN_DEST_PATH, 'w') as f:
      f.write(data)
    os.chmod(PLUGIN_DEST_PATH, 0o755)
    plugin.nagios_exit(0, 'Read {} bytes for {} => {}'.format(len(data),plugin['plugin_name'],PLUGIN_DEST_PATH))
else:
    plugin.nagios_exit(2, 'Failed to update plugin {} => HTTP Code {}'.format(plugin['plugin_name'],response.status))

#print(dir(response))
print(f'read {len(data)} bytes')





"""
command = ['echo','chronyc', '-h', plugin['host'], '-p', str(plugin['port']), 'tracking']

try:
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None)
    output = process.communicate()[0]
except OSError as ex:
    plugin.nagios_exit(Plugins.UNKNOWN, str(ex))

if process.returncode != 0:
    plugin.nagios_exit(Plugins.CRITICAL, output.rstrip())
"""

"""
matcher = re.search(r'^Leap status\s*:\s*(.*)$', output, flags=re.MULTILINE)
leap_status = matcher.group(1)
if leap_status == 'Not synchronised':
    plugin.nagios_exit(Plugins.CRITICAL, 'Server is not synchronised')
if leap_status == 'Unknown':
    plugin.nagios_exit(Plugins.UNKNOWN, 'Server status is unknown')

matcher = re.search(r'^System time\s*:\s*([0-9]+\.[0-9]*) seconds (slow|fast)', output,
                    flags=re.MULTILINE)
offset = float(matcher.group(1))

status = Plugins.check_threshold(abs(offset), warning=plugin['warning'],
                                 critical=plugin['critical'])
plugin.add_perfdata('offset', offset, uom='s', warn=plugin['warning'], crit=plugin['critical'])
"""
plugin.nagios_exit(0, 'Offset {} seconds'.format(0))
