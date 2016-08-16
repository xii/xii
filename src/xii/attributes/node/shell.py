import os

from xii import paths, error
from xii.need import NeedSSH, NeedLibvirt
from xii.attributes.base import NodeAttribute
from xii.validator import String, List, Required, Key, Dict


class ShellAttribute(NodeAttribute, NeedSSH, NeedLibvirt):
    entity = "shell"
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
        return self.get_parent().get_child("user").get_default_user()

    def get_default_host(self):
        return self.domain_get_ip(self.component_name())

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
        for script in self.settings:
            if action in script:
                shell = "/usr/bin/bash"

                if "shell" in script:
                    shell = script["shell"]

                scripts.append((script[action], shell))
        return scripts

    def _run_shell(self, script, shell="/usr/bin/bash"):
        if not os.path.isfile(script):
            raise error.NotFound("Could not find privisioner shell script ({})"
                                 .format(script))
        script_location = self.copy_default_to_tmp(script)
        return self.run_default_ssh(shell + " " + script_location)


ShellAttribute.register()
