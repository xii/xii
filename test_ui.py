from multiprocessing import Pool
from functools import partial
from time import sleep
import sys

class Progressbar():
    def __init__(self, ui, target, msg, full):
        self._ui = ui
        self._target = target
        self._msg = msg
        self._full = full
        self._current = 0

    def init(self):
        self.render()

    def render(self):
        self._ui.line(self._target, self._msg + " {}%".format(self._current))

    def update(self, state):
        self._current = state
        self._ui.render_progressbars()

class UI():

    def __init__(self):
        self._bars = []
        self._locked = False


    def line(self, target, msg):
        print(target + " " + msg)

    def say(self, target, msg):
        print(len(self._bars))
        self.up(len(self._bars))
        self.clear()
        self.line(target, msg)

        for bar in self._bars:
            bar.render()

    def progressbar(self, target, msg, full):
        bar = Progressbar(self, target, msg, full)
        self._bars.append(bar)
        bar.init()
        return bar

    def render_progressbars(self):
        self.up(len(self._bars))
        for bar in self._bars:
            bar.render()

    def clear(self):
        print("clear")
        #sys.stdout.write("\033[2K")
        #sys.stdout.flush()
                
    def up(self, n):
        print("up x " + str(n))
        #sys.stdout.write("\033[{}F".format(n))
        #sys.stdout.flush()


def fast_progress(ui):
    name = "[fast_progress]"
    ui.say(name, "Starting fast progress")
    sleep(1)
    ui.say(name, "Running some funny things")
    
    for _ in range(5):
        sleep(1)
        ui.say(name, "About to start a progressbar")
        progress = ui.progressbar(name, "collecting 100 items", 100)
        for i in range(100):
            sleep(4)
            progress.update(i)
        progress.done("successfull!")
        ui.say(name, "funny thing...sleeping")
        sleep(5)

def slow_progress(ui):
    name = "[slow_progress]"
    ui.say(name, "Starting...")
    sleep(4)
    
    for _ in range(5):
        sleep(4)
        ui.say(name, "About to start a progressbar")
        progress = ui.progressbar(name, "collecting 100 items", 100)
        for i in range(100):
            sleep(3)
            progress.update(i)
        progress.done("successfull!")
        ui.say(name, "funny thing...sleeping")
        sleep(10)

def spammer(ui):
  for i in range(300):
    ui.say("[spammer]", "Tick Tick {}".format(i))
    sleep(3)
    

ui = UI()

def run(f):
    f(ui)

if __name__ == "__main__":
    pool = Pool(3)
    pool.map(run, [spammer, fast_progress])
