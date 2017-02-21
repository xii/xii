
import os
import pkgutil
import abc
import subprocess

from xii.need import NeedIO
from xii import error


class NeedAnsible(NeedIO):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def ansible_executable(self):
        pass

    def is_ansible_installed(self):
        result = self.io().which(self.ansible_executable())
        return result is not None

    def run_playbook(self, inventory, playbook, args=[], env={}):
        executable = self.io().which(self.ansible_executable())

        args.append("-i")
        args.append(inventory)

        for key, value in env.items():
            args.append('-e"{}={}"'.format(key, value))

        try:
            process = subprocess.Popen([executable] + args + [playbook],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    stdin=subprocess.PIPE,
                                    shell=False)

            recap = []
            has_recap = False
            is_verbose  = self.is_verbose()
            is_parallel = self.is_parallel()

            for output in iter(process.stdout.readline, ""):
                line = output.decode('utf-8').strip()

                if (not is_parallel) or is_verbose:
                    self.say("| " + line)
                else:
                    if line.startswith("PLAY RECAP *"):
                        has_recap = True
                    if has_recap:
                        recap.append(line)


            if has_recap:
                map(self.say, recap)

            if process.wait() != 0:
                return False
            return True

        except OSError as e:
            raise error.ExecError(["ansible failed:", e.__str__()])

        except KeyError as e:
            raise error.ExecError(["ansible called with invalid arguments:", __str__(e)])

