from threading import Thread, Lock
from multiprocessing import Pool
from functools import partial
from time import sleep
import sys
import os


def width():
    _, columns = os.popen('stty size', 'r').read().split()
    return int(columns)

class Progressbar():
    def __init__(self, ui, target, msg, full):
        self._ui = ui
        self._target = target
        self._msg = msg
        self._full = full
        self._current = 0

    def init(self):
        self.render()

    def done(self, msg):
        self._ui.remove_bar(self, self._target, msg)

    def render(self):
        w = int(width() * 0.2)
        p = int(self._current / (self._full / 100)) + 1
        c = int((w * p) / 100)
        e = w - c
        bar = "[{}{}]{:>4}%".format("#" * c, " " * e, p)

        self._ui._line(self._target, "{:25} {}".format(self._msg, bar))

    def update(self, state):
        self._current = state
        self._ui.render()


class UI():

    def __init__(self):
        self._bars = []
        self.lock = Lock()

    def say(self, target, msg):
        self.lock.acquire()

        self.up(len(self._bars))
        self._line(target, msg)
        self._render_bars()

        self.lock.release()

    def progressbar(self, target, msg, full):
        self.lock.acquire()
        bar = Progressbar(self, target, msg, full)
        self._bars.append(bar)
        bar.render()
        self._render_bars()

        self.lock.release()
        return bar

    def remove_bar(self, rm, target, msg):
        self.lock.acquire()

        self.up(len(self._bars))

        if rm in self._bars:
            self._bars.remove(rm)

        self._line(target, msg)

        self._render_bars()

        self.lock.release()

    def render(self):
        self.lock.acquire()

        self._render_bars()

        self.lock.release()

    def clear(self):
        sys.stdout.write("\033[2K")
        sys.stdout.flush()

    def up(self, n):
        if n < 1:
            return
        sys.stdout.write("\033[{}F".format(n))
        sys.stdout.flush()

    def _line(self, target, msg):
        w = width()
        out = "{:15} {}".format(target, msg)
        print(out + " " * (w - len(out)))

    def _render_bars(self):
        self._update_bars()
        self.up(len(self._bars))
        for bar in self._bars:
            bar.render()

    def _update_bars(self):
        def get_state(bar):
            return int(bar._current / (bar._full / 100)) + 1
        self._bars = list(reversed(sorted(self._bars, key=get_state)))


def progress(ui, s, t):
    name = "[" + t + "]"
    ui.say(name, "Starting fast progress")
    sleep(1)
    ui.say(name, "Running some funny things")

    for _ in range(100):
        sleep(1)
        ui.say(name, "About to start a progressbar")
        progress = ui.progressbar(name, "collecting 100 items", 100)
        for i in range(100):
            sleep(s)
            progress.update(i)
        progress.done("successfull!")
        ui.say(name, "funny thing...sleeping")
        sleep(5)


def spammer(ui):
    for i in range(4000):
        ui.say("[spammer]", "Tick Tick {}".format(i))
        sleep(2)


if __name__ == "__main__":

    ui = UI()
    threads = [Thread(target=progress, args=(ui, 0.1, "fast1")),
               Thread(target=progress, args=(ui, 0.15, "fast2"))]
               #Thread(target=progress, args=(ui, 0.01, "ultrafast"))]


               #Thread(target=progress, args=(ui, 0.01, "ultrafast")),
               #Thread(target=progress, args=(ui, 0.3, "normal"))]
#               Thread(target=progress, args=(ui, 0.5, "slow")),
#               Thread(target=progress, args=(ui, 1, "ultraslow"))]

    #[Thread(target=progress, args=(ui, 0.1, "fast"))]
    #threads = #[Thread(target=spammer, args=(ui,))]
               #Thread(target=progress, args=(ui, 0.01, "ultrafast")),
               #Thread(target=progress, args=(ui, 0.3, "normal"))]
#               Thread(target=progress, args=(ui, 0.5, "slow")),
#               Thread(target=progress, args=(ui, 1, "ultraslow"))]


    map(lambda t: t.start(), threads)
    map(lambda t: t.join(), threads)
