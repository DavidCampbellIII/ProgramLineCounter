import json

class Language:
    def __init__(self, name, extensions, comment, multiLineComments, canHaveMultiLines, lineEnder, lineBreaker):
        self.name = name
        self.extensions = extensions
        self.comment = comment
        self.multiLineComments = multiLineComments
        self.canHaveMultiLines = canHaveMultiLines
        self.lineEnder = lineEnder
        self.lineBreaker = lineBreaker

    @staticmethod
    def loadLanguages(path):
        with open(path) as f:
            langsDict = json.load(f)
        
        languages = {}
        for lang in langsDict:
            name = lang["name"]
            language = Language(name, lang["extensions"], lang["comment"], lang["multiLineComments"], lang["canHaveMultiLines"], lang["lineEnder"], lang["lineBreaker"])
            languages[name] = language
        return languages