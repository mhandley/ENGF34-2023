# Audio based on code from Ethan Wood

from pa_settings import USE_SOUND
class Audio:
    def __init__(self):
        self.AUDIO = USE_SOUND
        try:
            import simpleaudio  
        except ImportError:
            print("Audio disabled.  To enable audio, install the python simpleaudio package")
            self.AUDIO = False

        if self.AUDIO:
            self.track = [simpleaudio.WaveObject.from_wave_file("./assets/eat.wav"),
                          simpleaudio.WaveObject.from_wave_file("./assets/melody.wav"),
                          simpleaudio.WaveObject.from_wave_file("./assets/died.wav"),
                          simpleaudio.WaveObject.from_wave_file("./assets/ghostdie.wav")]
            #self.background = simpleaudio.WaveObject.from_wave_file("./assets/loop2.wav")
            self.background_play = None
            self.track_play = [None, None, None, None, None, None]
            self.background_pause = False
            self.background_waiting = None

    def update(self):
        if self.AUDIO:
            return
            if self.background_waiting is not None and self.background_waiting.is_playing() == False:
                self.background_pause = False
            if self.background_play is None:
                self.background_play = self.background.play()
                self.background_play.stop()
            if not self.background_play.is_playing() and self.background_pause == False:
                self.background_play = self.background.play()

    def play(self, index):
        if self.AUDIO:
            if self.track_play[index] is None or not self.track_play[index].is_playing():
                self.track_play[index] = self.track[index].play()
                if not index == 0 and not index == 3:
                    self.background_waiting = self.track_play[index]
                    self.background_pause = True
                    if self.background_play is not None:
                        self.background_play.stop()
