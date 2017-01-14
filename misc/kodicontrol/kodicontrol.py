import json
import logging
import requests


KODI_CONTROL_URL = 'http://{}/jsonrpc'

REQUEST_BASE = {
    "jsonrpc": "2.0"
}

OK = "OK"

class KodiControl:
    def __init__(self, config):
        self._logger = logging.getLogger(__name__)

        try:
            self._ip_address = config['KODI_IP']
        except KeyError:
            self._ip_address = 'localhost'
            self._logger.warning(
                "No Kodi ip-address supplied, using '%d' instead",
                self._ip_address)

    def send_command(self, cmds):
        request = []

        wrapped = False
        if not isinstance(cmds, list):
            cmds = [cmds]
            wrapped = True

        for i, cmd in enumerate(cmds):
            cmd["id"] = i
            request.append({key: value for (key, value) in (REQUEST_BASE.items() + cmd.items())})

        print 'Sending command ', request

        r = requests.post(KODI_CONTROL_URL.format(self._ip_address), json.dumps(request),
                          headers={'Content-Type': 'application/json'})

        response = r.json()

        if len(response) == 1 and wrapped:
            return response[0]

        return response

    def play(self):
        return self.send_command({
            "method": "Player.PlayPause",
            "params": {
                "playerid": 1,
                "play": True
            }
        })

    def pause(self):
        return self.send_command({
            "method": "Player.PlayPause",
            "params": {
                "playerid": 1,
                "play": False
            }
        })

    def stop(self):
        return self.send_command({
            "method": "Player.Stop",
            "params": {
                "playerid": 1
            }
        })

    def getmovies(self):
        return self.send_command({
            "method": "VideoLibrary.GetMovies"
        })['result']['movies']

    def playmovie(self, movieid):
        return self.send_command({
            "method": "Player.Open",
            "params": {
                "item": {
                    "movieid": movieid
                }
            }
        })

    def filter(self, text):
        responses = self.send_command([
            {
                "method": "Input.ExecuteAction",
                "params": {
                    "action": "filter"
                }
            },
            {
                "method": "Input.SendText",
                "params": {
                    "text": text
                }
            },
            {
                "method": "Input.ExecuteAction",
                "params": {
                    "action": "close"
                }
            }
        ])

        return all(response['result'] == OK for response in responses)

    def activatewindow(self, window, params):
        return self.send_command({
            "method": "GUI.ActivateWindow",
            "params": {
                "window": window,
                "parameters": params
            }
        })['result'] == OK

    def showmovies(self):
        return self.activatewindow("videos", ["MovieTitles"])

    def showtvshows(self):
        return self.activatewindow("videos", ["TvShowTitles"])
