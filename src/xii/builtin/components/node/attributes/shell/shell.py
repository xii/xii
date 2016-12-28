import os

from xii import error, need
from xii.validator import String, List, Key, Dict

from xii.components.node import NodeAttribute


class ShellAttribute(NodeAttribute, need.NeedSSH, need.NeedLibvirt):
    atype = "shell"
    requires = ["ssh", "user"]

    keys = List(Dict([
        Key("start", String()),
        Key("stop", String()),
        Key("spawn", String()),
        Key("suspend", String()),
        Key("resume", String()),
        Key("shell", String())
    ]))

    def get_default_user(self):
        return self.other_attribute("user").get_default_user()

    def get_default_host(self):
        return self.domain_get_ip(self.component_entity())

    def after_start(self):
        for (script, shell) in self._get_shell_scripts("start"):
            self.say("[start] running shell provisioner ({})"
                     .format(script))
            self._run_shell(script, shell)

    def suspend(self):
        for (script, shell) in self._get_shell_scripts("suspend"):
            self.say("[suspend] running shell provisioner ({})"
                     .format(script))
            self._run_shell(script, shell)

    def after_resume(self):
        for (script, shell) in self._get_shell_scripts("resume"):
            self.say("[resume] running shell provisioner ({})"
                     .format(script))
            self._run_shell(script, shell)

    def stop(self):
        for (script, shell) in self._get_shell_scripts("stop"):
            self.say("[stop] running shell provisioner ({})"
                     .format(script))
            self._run_shell(script, shell)

    def _get_shell_scripts(self, action):
        scripts = []
        for script in self.settings():
            if action in script:
                shell = "/bin/bash"

                if "shell" in script:
                    shell = script["shell"]

                scripts.append((script[action], shell))
        return scripts

    def _run_shell(self, script, shell="/bin/bash"):
        if not os.path.isfile(script):
            raise error.NotFound("Could not find privisioner shell script ({})"
                                 .format(script))
        ssh = self.default_ssh()
        script_location = ssh.copy_to_tmp(script)
        ssh.run(shell + " " + script_location)
