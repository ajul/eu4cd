import re

import eu4cd.gamedata
import eu4cd.ideaoptions
import pyradox.struct
import pyradox.yml

from collections import OrderedDict

from PyQt5.QtCore import (
    pyqtSignal,
    QRegExp,
    )
from PyQt5.QtGui import (
    QRegExpValidator,
    )
from PyQt5.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    )

class IdeasWidget(QWidget):
    costChanged = pyqtSignal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # loader
        self.loader = QWidget()
        
        loaderLayout = QHBoxLayout()

        self.ideasSelect = eu4cd.gamedata.IdeasSelect()
        loaderLayout.addWidget(self.ideasSelect)

        self.loadButton = QPushButton("Load")
        loaderLayout.addWidget(self.loadButton)

        self.loader.setLayout(loaderLayout)

        # header
        self.header = QWidget()
        headerLayout = QFormLayout()

        self.internalName = QLineEdit()
        headerLayout.addRow(QLabel("Internal name:"), self.internalName)
        self.name = QLineEdit()
        headerLayout.addRow(QLabel("Name:"), self.name)

        headerLayout.addRow(QLabel("Load ideas:"), self.loader)
        
        self.header.setLayout(headerLayout)

        layout = QVBoxLayout()
        layout.addWidget(self.header)
        
        # tabs
        self.tabs = IdeasTabWidget()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

        # signals
        self.loadButton.clicked.connect(self.handleIdeasLoaded)
        self.tabs.costChanged.connect(self.handleCostChanged)

    def handleIdeasLoaded(self):
        ideasIndex = self.ideasSelect.currentIndex()
        ideasInternalName = eu4cd.gamedata.ideas[ideasIndex]
        tree = eu4cd.gamedata.ideaTrees[ideasIndex]
        self.tabs.setTree(ideasInternalName, tree)

    def reload(self):
        self.ideasSelect.reload()
        self.tabs.reload()

    def getTree(self, tag):
        return self.tabs.getTree(tag)

    def getCost(self):
        return self.tabs.getCost()

    def getLocalization(self, tag):
        return self.tabs.getLocalization(tag, self.getInternalName())

    def getPenalties(self):
        return self.tabs.getPenalties()

    def getInternalName(self):
        return self.internalName.text()

    def setInternalName(self, internalName):
        self.internalName.setText(internalName)

    def setName(self, name):
        self.name.setText(name)

    def handleCostChanged(self, cost):
        self.costChanged.emit(cost)

class IdeasTabWidget(QTabWidget):
    costChanged = pyqtSignal(float)
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
        self.ideas = []

        self.traditions = Idea("traditions")
        self.addTab(self.traditions, "Traditions")
        self.traditions.setName("Custom Traditions")
        self.traditions.costChanged.connect(self.handleCostChanged)
        
        for i in range(7):
            idea = Idea()
            self.ideas.append(idea)
            self.addTab(idea, "Idea %d" % (i + 1) )
            idea.setInternalName("custom_idea_%d" % (i + 1) )
            idea.setName("Custom Idea %d" % (i + 1) )
            idea.costChanged.connect(self.handleCostChanged)

        self.ambitions = Idea("ambitions")
        self.addTab(self.ambitions, "Ambitions")
        self.ambitions.setName("Custom Ambitions")
        self.ambitions.costChanged.connect(self.handleCostChanged)

    def reload(self):
        self.traditions.reload()
        for idea in self.ideas:
            idea.reload()
        self.ambitions.reload()

    def getTree(self, tag):
        tree = pyradox.struct.Tree()
        tree.append("start", self.traditions.getTree())
        tree.append("bonus", self.ambitions.getTree())
        trigger = pyradox.struct.Tree()
        trigger.append("tag", tag)
        tree.append("trigger", trigger)
        tree.append("free", True)

        for idea in self.ideas:
            tree.append(idea.getInternalName(), idea.getTree())
        return tree

    def setTree(self, ideasInternalName, tree):
        i = 0
        for bonusKey, bonusData in tree.items():
            if bonusKey == "start": self.traditions.setTree(ideasInternalName, bonusKey, bonusData)
            elif bonusKey == "bonus": self.ambitions.setTree(ideasInternalName, bonusKey, bonusData)
            elif bonusKey not in ("category", "trigger", "ai_will_do", "important", "free"):
                self.ideas[i].setTree(ideasInternalName, bonusKey, bonusData)
                i += 1

    def getCost(self):
        cost = 0.0
        for idea in self.getAllIdeas():
            cost += idea.getCost()
        return cost

    def getLocalization(self, tag, ideasInternalName):
        result = {}

        result[ideasInternalName + "_start"] = self.traditions.getName()
        result[ideasInternalName + "_bonus"] = self.ambitions.getName()
        
        for idea in self.ideas:
            internalName = idea.getInternalName()
            result[internalName] = idea.getName()
            result[internalName + "_desc"] = idea.getDescription()
        return result

    def getPenalties(self):
        yellowCards = []
        redCards = []
        cost = self.getCost()
        if cost > 15.0:
            redCards.append("National ideas exceed 15 points.")
        elif cost > 10.0:
            yellowCards.append("National ideas exceed 10 points.")

        # duplicate ideas
        bonusTypes = []
        for idea in self.getAllIdeas():
            bonusTypes += list(idea.ideaBonuses.getBonusTypes())

        for i, bonusType in enumerate(bonusTypes):
            if bonusType in bonusTypes[i+1:]:
                redCards.append("Duplicate bonus %s." % (bonusType,))

        return yellowCards, redCards

    def getAllIdeas(self):
        yield self.traditions
        for idea in self.ideas: yield idea
        yield self.ambitions

    def handleCostChanged(self):
        cost = self.getCost()
        self.costChanged.emit(cost)

class Idea(QWidget):
    costChanged = pyqtSignal()
    
    def __init__(self, ideaType=None, parent=None):
        super().__init__(parent=parent)
        
        layout = QVBoxLayout()

        self.ideaBonuses = IdeaBonuses()
        layout.addWidget(self.ideaBonuses)
        self.ideaBonuses.costChanged.connect(self.handleCostChanged)

        self.ideaText = IdeaText(ideaType=ideaType)
        layout.addWidget(self.ideaText)
        
        self.setLayout(layout)

    def reload(self):
        # TODO: clear?
        pass

    def getInternalName(self):
        return self.ideaText.internalName.text()

    def setInternalName(self, name):
        self.ideaText.internalName.setText(name)

    def getName(self):
        return self.ideaText.name.text()

    def setName(self, name):
        self.ideaText.name.setText(name)

    def getDescription(self):
        return self.ideaText.description.toPlainText()

    def getTree(self):
        return self.ideaBonuses.getTree()

    def setTree(self, ideasInternalName, bonusKey, bonusData):
        self.ideaText.setTree(ideasInternalName, bonusKey)
        self.ideaBonuses.setTree(bonusData)

    def getCost(self):
        return self.ideaBonuses.getCost()

    def handleCostChanged(self):
        self.costChanged.emit()

class IdeaText(QGroupBox):
    def __init__(self, ideaType=None, parent=None):
        super().__init__("Text", parent=parent)
        layout = QFormLayout()

        # internal name
        if ideaType is None:
            self.internalName = QLineEdit()
            self.internalName.setValidator(QRegExpValidator(QRegExp("\w+")))

            layout.addRow(QLabel("Internal name:"), self.internalName)

        # human name
        self.name = QLineEdit()
        layout.addRow(QLabel("Name:"), self.name)

        if ideaType is None:
            self.description = QTextEdit()

            layout.addRow(QLabel("Description:"), self.description)
        
        self.setLayout(layout)

    def setTree(self, ideasInternalName, bonusKey):
        if bonusKey in ("start", "bonus"):
            self.name.setText(pyradox.yml.getLocalization(ideasInternalName + "_" + bonusKey, sources = ["text", "countries", "EU4", "powers_and_ideas"]) or "")
        else:
            self.internalName.setText(bonusKey + "_custom")
            self.name.setText(pyradox.yml.getLocalization(bonusKey, sources = ["text", "countries", "EU4", "powers_and_ideas"]) or "")
            self.description.setText(pyradox.yml.getLocalization(bonusKey + "_desc", sources = ["text", "countries", "EU4", "powers_and_ideas"]) or "")
        

class IdeaBonuses(QGroupBox):
    costChanged = pyqtSignal()

    nBonuses = 3
    
    def __init__(self, parent=None):
        super().__init__("Bonuses", parent=parent)

        layout = QFormLayout()

        self.bonuses = []
        for i in range(self.nBonuses):
            ideaBonus = IdeaBonus()
            ideaBonus.costChanged.connect(self.handleCostChanged)
            self.bonuses.append(ideaBonus)
            layout.addRow(QLabel("Bonus %d:" % (i + 1,)), self.bonuses[i])
        
        self.setLayout(layout)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

    def getTree(self):
        tree = pyradox.struct.Tree()
        for bonus in self.bonuses:
            bonusType = bonus.getType()
            bonusValue = bonus.getValue()
            if bonusValue is not None:
                tree.append(bonusType, bonusValue)
        return tree

    def setTree(self, bonuses):
        for i, bonus in enumerate(self.bonuses):
            if len(bonuses) > i:
                bonusType, bonusValue = bonuses.at(i)
                if bonusType not in eu4cd.ideaoptions.bonusTypes: continue
                bonus.bonusTypeSelect.setCurrentIndex(eu4cd.ideaoptions.bonusTypes.index(bonusType))
                valueIndex = eu4cd.ideaoptions.getClosestValueIndex(bonus.values, bonusValue)
                bonus.bonusValueSelect.setCurrentIndex(valueIndex)
            else:
                bonus.bonusTypeSelect.setCurrentIndex(0)

    def getCost(self):
        return sum(bonus.getCost() for bonus in self.bonuses)

    def handleCostChanged(self):
        self.costChanged.emit()

    def getBonusTypes(self):
        for bonus in self.bonuses:
            if bonus.getIndex() > 0:
                yield bonus.getType()

class IdeaBonus(QWidget):
    costChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        layout = QHBoxLayout()
        self.bonusTypeSelect = QComboBox()
        self.bonusTypeSelect.addItems(eu4cd.ideaoptions.bonusTypes)
        layout.addWidget(self.bonusTypeSelect)

        self.bonusValueSelect = QComboBox()
        
        layout.addWidget(self.bonusValueSelect)
        self.setLayout(layout)

        self.resetBonusValue(0)

        self.bonusTypeSelect.currentIndexChanged.connect(self.resetBonusValue)
        self.bonusValueSelect.currentIndexChanged.connect(self.handleCostChanged)

    def resetBonusValue(self, index):
        options, self.values, self.costs = eu4cd.ideaoptions.generateOptions(index)
        defaultIndex = eu4cd.ideaoptions.getClosestValueIndex(self.values, eu4cd.ideaoptions.bonusNormalValue[index])
        self.bonusValueSelect.clear()
        self.bonusValueSelect.addItems(options)
        self.bonusValueSelect.setCurrentIndex(defaultIndex)

    def getIndex(self):
        return self.bonusTypeSelect.currentIndex()

    def getType(self):
        return eu4cd.ideaoptions.bonusTypes[self.bonusTypeSelect.currentIndex()]

    def getValue(self):
        return self.values[self.bonusValueSelect.currentIndex()]

    def getCost(self):
        return self.costs[self.bonusValueSelect.currentIndex()]

    def handleCostChanged(self):
        self.costChanged.emit()


