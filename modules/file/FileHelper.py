import json
from os import getcwd, mkdir
from os.path import exists


class FileHelper:
    def __init__(self, filename: str = False, directory: str = False):

        root = getcwd()

        if not directory:
            directory = f"{root}//datasets//"

        if not filename:
            filename = "output.json"

        self.filename = filename
        self.directory = directory


    def write(self, content: str):
        if not exists(self.directory):
            mkdir(self.directory)

        with open(self.directory + self.filename, 'a') as file:
            file.write(content)
