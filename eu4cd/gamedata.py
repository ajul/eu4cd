import pyradox.config
import pyradox.format
import pyradox.struct
import pyradox.txt
import os

from PyQt5.QtWidgets import (
    QComboBox,
    )

tags = []
tagFiles = []
tagNames = []
tagSelects = []
tagAdjectives = []
technologyGroups = []
religions = []
governments = []

ideas = []
ideaTrees = []

def readGameData(gamePath):
    global tags, tagFiles, tagNames, tagSelects, tagAdjectives, technologyGroups, religions, governments, ideas, ideaTrees

    pyradox.config.basedirs['EU4'] = gamePath
    pyradox.config.defaultGame = 'EU4'

    # tags
    tags = []
    tagFiles = []
    tagNames = []
    tagSelects = []
    tagAdjectives = []
    countryPath = os.path.join(gamePath, "history", "countries")
    for filename in os.listdir(countryPath):
        fullpath = os.path.join(countryPath, filename)
        if os.path.isfile(fullpath):
            root, ext = os.path.splitext(fullpath)
            if ext != ".txt": continue
            tag, name = pyradox.format.splitFilename(filename)
            if tag in ("NAT", "PIR", "REB", "XXX"): continue
            tags.append(tag)
            tagFiles.append(fullpath)

            name = pyradox.yml.getLocalization(tag, sources = ["text", "countries", "EU4"]) or ""
            tagSelects.append("%s - %s" % (tag, name))
            tagNames.append(name)
            tagAdjectives.append(pyradox.yml.getLocalization(tag + "_ADJ", sources = ["text", "countries", "EU4"]) or "")

    # tech groups
    techData = pyradox.txt.parseFile(os.path.join(gamePath, "common", "technology.txt"))
    technologyGroups = list(techData["groups"].keys())

    # religions
    
    religionData = pyradox.txt.parseMerge(os.path.join(gamePath, "common", "religions"))
    religions = []
    for _, group in religionData.items():
        for religion, data in group.items():
            if not isinstance(data, pyradox.struct.Tree): continue
            religions.append(religion)

    # governments
    governmentData = pyradox.txt.parseMerge(os.path.join(gamePath, "common", "governments"))
    governments = list(governmentData.keys())

    # ideas
    ideasData = pyradox.txt.parseMerge(os.path.join(gamePath, "common", "ideas"))
    ideas = []
    ideaTrees = []
    for key, data in ideasData.items():
        if "free" not in data: continue # national ideas only
        ideas.append(key)
        ideaTrees.append(data)

    ideas, ideaTrees = zip(*sorted(zip(ideas, ideaTrees)))

class TagSelect(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.reload()

    def reload(self):
        self.clear()
        self.addItems(tagSelects)

class TechnologyGroupSelect(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.reload()

    def reload(self):
        self.clear()
        self.addItems(technologyGroups)

class ReligionSelect(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.reload()

    def reload(self):
        self.clear()
        self.addItems(religions)

class GovernmentSelect(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.reload()

    def reload(self):
        self.clear()
        self.addItems(governments)

class MercantilismSelect(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.addItems(["10", "25"])

class IdeasSelect(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.reload()

    def reload(self):
        self.clear()
        self.addItems(ideas)