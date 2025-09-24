from direct.showbase.DirectObject import DirectObject
from direct.showbase import Loader
from ursina import *

class Sfx_handler(DirectObject):
    def __init__(self):
        super().__init__()
        self.music_path = 'assets/music/'

        self.playlist = {
            "background": self.load_music("StockTune-Haunted Nocturne Winter Eve_1726915959.mp3"),
            "menu": self.load_music("top-down-fantasy-1.ogg"),
        }

        self.current_track = self.playlist["menu"]
        self._current_volume = 0.5


    def load_music(self, name):
        path = self.music_path
        return Audio(f"{path}/{name}", loop=True, autoplay=False)


    def play_music(self, track="menu", volume=0.5):
        self.current_track = self.playlist[track]
        self.current_track.volume = volume
        self.current_track.play()
