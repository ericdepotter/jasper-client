import logging
import re
import sys
import time

from jasper import plugin
from misc.kodicontrol import KodiControl
from misc.yamahacontrol import YamahaControl


class KodiControlPlugin(plugin.SpeechHandlerPlugin):
    def __init__(self, *args, **kwargs):
        super(KodiControlPlugin, self).__init__(*args, **kwargs)

        self._logger = logging.getLogger(__name__)
        self._kodicontrol = KodiControl(self.profile)
        self._yamahacontrol = YamahaControl(self.profile)

    def is_valid(self, text):
        """
        Returns True if the input is related to movies/shows.

        Arguments:
        text -- user-input, typically transcribed speech
        """
        return any(phrase in text.upper() for phrase in self.get_phrases())

    def get_phrases(self):
        return [self.gettext('MOVIES'), self.gettext('MOVIE'), self.gettext('SHOWS'), self.gettext('SHOW')]

    def handle(self, text, mic):
        """
        Responds to user-input, typically speech text, by performing some actions on KODI.

        Arguments:
            text -- user-input, typically transcribed speech
            mic -- used to interact with the user (for both input and output)
        """

        mic.say(self.gettext('Starting home theater'))
        self._yamahacontrol.on()
        time.sleep(1)
        self._yamahacontrol.setsource('HDMI1')

        self.handlekodirequest(text, mic)

    def handlekodirequest(self, text, mic):
        while True:
            loop = True
            if self.saidword(text, ['MOVIE', 'MOVIES'], stop=2):
                self._kodicontrol.showmovies()
                loop = self.handlemovierequest(text, mic)

            elif self.saidword(text, ['STOP', 'EXIT', 'QUIT']):
                mic.say(self.gettext('Shutting down home theater'))
                self._yamahacontrol.off()
                return

            if not loop:
                return

            mic.say(self.gettext('What do you want to do now?'))
            text = mic.active_listen()

    def handlemovierequest(self, text, mic):
        if self.gettext('SEARCH') in text[0]:
            mic.say('Searching for movie {}'.format(text))
            self._kodicontrol.filter(text)

        elif self.gettext('PAUSE') in text[0]:
            mic.say(self.gettext('Pausing movie'))
            self._kodicontrol.pause()

        elif self.gettext('RESUME') in text[0] or (len(text) == 1 and self.saidword(text, ['PLAY', 'START'])):
            mic.say(self.gettext('Resuming movie'))
            self._kodicontrol.play()

        elif self.gettext('STOP') in text[0]:
            mic.say(self.gettext('Stopping movie'))
            self._kodicontrol.stop()

        else:
            movies = self._kodicontrol.getmovies()

            # format text for searching
            self.saidword(text, ['PLAY', 'START', 'OPEN', 'SHOW'], stop=1)
            self.saidword(text, ['AND', 'THE'])
            moviename = re.sub(r' ', '.*', text)

            matchedmovies = [movie for movie in movies if
                             re.search(moviename, re.sub(r'[^a-zA-Z\d\s]', '', movie['label'], re.IGNORECASE))]

            if len(matchedmovies) == 0:
                mic.say('No such movie found')
            elif len(matchedmovies) > 1:
                mic.say('Found multiple matching movies. Searching instead')
                self._kodicontrol.filter(text)
            else:
                mic.say('Starting movie')
                self._kodicontrol.playmovie(matchedmovies[0]['id'])

                return False

        return True

    def saidword(self, text, words, start=0, stop=sys.maxint):
        if not isinstance(words, list):
            words = [words]

        words = [self.gettext(word).upper() for word in words]
        stop = min(len(words), stop)

        for idx, word in enumerate(text[start:stop]):
            if word in words:
                del text[idx + start]
                return True

        return False

        # for word in text[start:stop]:
        #     word = self.gettext(word).upper()
        #
        #     try:
        #         index = text.index(word)
        #
        #         if start <= index < stop:
        #             text.remove(word)
        #             return True
        #     except ValueError:
        #         continue
        #
        # return False
