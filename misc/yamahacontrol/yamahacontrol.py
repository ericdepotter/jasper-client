import requests


YAMAHA_CONTROL_URL = 'http://{}:80/YamahaRemoteControl/ctrl'


class YamahaControl:
    def __init__(self, config):
        self._ip_address = config['YAMAHA_IP']

    def send_command(self, cmd):
        request = '<YAMAHA_AV cmd="PUT"><Main_Zone>{}</Main_Zone></YAMAHA_AV>'.format(cmd)

        r = requests.post(YAMAHA_CONTROL_URL.format(self._ip_address), request, headers={'Content-Type': 'text/xml'})

        return r.status_code == 200

    def on(self):
        return self.send_command("<Power_Control><Power>On</Power></Power_Control>")

    def off(self):
        return self.send_command("<Power_Control><Power>Standby</Power></Power_Control>")

    def setsource(self, source):
        return self.send_command("<Input><Input_Sel>{}</Input_Sel></Input>".format(source))
