import json

class Language:
    def __init__(self, name, extension, comment, canHaveMultiLines, lineEnder):
        self.name = name
        self.extension = extension
        self.comment = comment
        self.canHaveMultiLines = canHaveMultiLines
        self.lineEnder = lineEnder

    def loadLanguages(path):
        with open(path) as f:
            langsDict = json.load(f)
        
        languages = []
        for lang in langsDict:
            language = Language(lang["name"], lang["extension"], lang["comment"], lang["canHaveMultiLines"], lang["lineEnder"])
            languages.append(language)
        return languages