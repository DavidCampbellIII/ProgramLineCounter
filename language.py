import json

class Language:
    def __init__(self, name, extension, comment, canHaveMultiLines, lineEnder):
        self.name = name
        self.extension = extension
        self.comment = comment
        self.canHaveMultiLines = canHaveMultiLines
        self.lineEnder = lineEnder

    def loadLanguages(path):
        langsDict = json.loads(path)
        return langsDict