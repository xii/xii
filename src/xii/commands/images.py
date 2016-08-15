import os
import argparse

from xii import definition, command, paths


class ImagesCommand(command.Command):
    name = ['images', 'i']
    help = "Manipulate already downloaded local images"

    def run(self):
        (action, image) = self.parse_command()

        if not action:
            action = "list"

        if action == "list":
            self._list_images()
        elif action == "del":
            self._delete_image(image)

    def parse_command(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("action", nargs="?", default=None, help="available action (list|del)")
        parser.add_argument("image", nargs="?", default=None, help="image name")

        args = parser.parse_args(self.args)

        return (args.action, args.image)

    def _list_images(self):
        user = os.path.expanduser('~')
        images_path = os.path.join(paths.storage_path(user), "images")
        for image in os.listdir(images_path):
            print(image)

    def _delete_image(self, image):
        pass

command.Register.register(ImagesCommand)
