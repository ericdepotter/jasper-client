import requests


YAMAHA_CONTROL_URL = 'http://{}:80/YamahaRemoteControl/ctrl'


def send_command(ip, cmd):
    request = '<YAMAHA_AV cmd="PUT"><Main_Zone>{}</Main_Zone></YAMAHA_AV>'.format(cmd)

    r = requests.post(YAMAHA_CONTROL_URL.format(ip), request, headers={'Content-Type': 'text/xml'})

    return r.status_code == 200


class YamahaControl:
    def __init__(self, config):
        self._ip_address = config['YAMAHA_IP']

    def on(self):
        return send_command(self._ip_address, "<Power_Control><Power>On</Power></Power_Control>")

    def off(self):
        return send_command(self._ip_address, "<Power_Control><Power>Standby</Power></Power_Control>")
