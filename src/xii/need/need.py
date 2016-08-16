from abc import ABCMeta, abstractmethod

from xii.ui import HasOutput


class Need(HasOutput):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_ui(self):
        pass
