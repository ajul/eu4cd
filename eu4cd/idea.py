import re

import eu4cd.gamedata
import eu4cd.ideaoptions
import pyradox.struct
import pyradox.yml

from collections import OrderedDict

from PyQt4.QtCore import (
    pyqtSignal,
    QRegExp,
    )
from PyQt4.QtGui import (
    QRegExpValidator,
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
internalNameValidator = QRegExpValidator(QRegExp("(?!(start|bonus|category|trigger|ai_will_do|important|free)$)[a-zA-Z]\w*"))

class IdeasWidget(QWidget):
    """
    Widget for selecting national ideas.
    """
    costChanged = pyqtSignal(list)
    ideaNamesChanged = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # loader
        self.loader = QWidget()
        
        loaderLayout = QHBoxLayout()

        self.ideasSelect = eu4cd.gamedata.IdeasSelect()
        loaderLayout.addWidget(self.ideasSelect)

        self.loadButton = QPushButton("Load")
        self.loadButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        loaderLayout.addWidget(self.loadButton)

        self.loader.setLayout(loaderLayout)

        # header
        self.header = QWidget()
        headerLayout = QFormLayout()

        self.internalName = QLineEdit()
        self.internalName.setValidator(internalNameValidator)
        
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
        self.tabs.nameChanged.connect(self.handleIdeaNamesChanged)

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

    def getCosts(self):
        return self.tabs.getCosts()

    def getLocalization(self, tag):
        result = self.tabs.getLocalization(tag, self.getInternalName())
        result[self.getInternalName()] = self.getName()
        return result

    def getPenalties(self):
        return self.tabs.getPenalties()

    def getInternalName(self):
        result = self.internalName.text()
        if len(result) == 0: result = "unnamed"
        return result

    def setInternalName(self, internalName):
        self.internalName.setText(internalName)

    def getName(self):
        return self.name.text()

    def setName(self, name):
        self.name.setText(name)

    def handleCostChanged(self, costs):
        self.costChanged.emit(costs)

    def handleIdeaNamesChanged(self, names):
        self.ideaNamesChanged.emit(names)

class IdeasTabWidget(QTabWidget):
    """
    Set of tabs, one for each idea.
    """
    costChanged = pyqtSignal(list)
    nameChanged = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        
        self.ideas = []

        self.traditions = Idea(ideaType = "traditions")
        self.addTab(self.traditions, "Traditions")
        self.traditions.setName("Custom Traditions")
        self.traditions.costChanged.connect(self.handleCostChanged)
        self.traditions.nameChanged.connect(self.handleNameChanged)
        
        for i in range(7):
            idea = Idea()
            self.ideas.append(idea)
            self.addTab(idea, "Idea %d" % (i + 1) )
            idea.setInternalName("custom_idea_%d" % (i + 1) )
            idea.setName("Custom Idea %d" % (i + 1) )
            idea.costChanged.connect(self.handleCostChanged)
            idea.nameChanged.connect(self.handleNameChanged)

        self.ambitions = Idea(ideaType = "ambitions")
        self.addTab(self.ambitions, "Ambitions")
        self.ambitions.setName("Custom Ambitions")
        self.ambitions.costChanged.connect(self.handleCostChanged)
        self.ambitions.nameChanged.connect(self.handleNameChanged)

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
        return sum(idea.getCost() for idea in self.getAllIdeas())

    def getCosts(self):
        return [idea.getCost() for idea in self.getAllIdeas()]

    def getNames(self):
        return [idea.getName() for idea in self.getAllIdeas()]

    def getNegativeCost(self):
        return sum(idea.getNegativeCost() for idea in self.getAllIdeas())

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
            redCards.append("National ideas cost more than 15.00 points.")
        elif cost > 11.0:
            yellowCards.append("National ideas cost more than 11.00 points.")

        # idea cost limits
        for idea in self.getAllIdeas():
            y, r = idea.getPenalties()
            yellowCards += y
            redCards += r

        # duplicate bonuses
        bonusTypes = []
        for idea in self.getAllIdeas():
            bonusTypes += list(idea.ideaBonuses.getBonusTypes())

        for i, bonusType in enumerate(bonusTypes):
            if bonusType in bonusTypes[i+1:] and not eu4cd.ideaoptions.allowDuplicate(bonusType):
                redCards.append("Duplicate bonus in %s." % (bonusType,))

        # excessive negatives
        negativeCost = self.getNegativeCost()
        if negativeCost < -1.0:
            redCards.append("Negative bonuses costing less than -1.0 points.")

        return yellowCards, redCards

    def getAllIdeas(self):
        yield self.traditions
        for idea in self.ideas: yield idea
        yield self.ambitions

    def handleCostChanged(self):
        costs = self.getCosts()
        self.costChanged.emit(costs)

    def handleNameChanged(self):
        names = self.getNames()
        self.nameChanged.emit(names)

class Idea(QWidget):
    costChanged = pyqtSignal()
    nameChanged = pyqtSignal()
    
    def __init__(self, ideaType=None, parent=None):
        super().__init__(parent=parent)

        self.ideaType = ideaType
        
        layout = QVBoxLayout()

        self.ideaBonuses = IdeaBonuses(ideaType = ideaType)
        layout.addWidget(self.ideaBonuses)
        self.ideaBonuses.costChanged.connect(self.handleCostChanged)

        self.ideaText = IdeaText(ideaType=ideaType)
        layout.addWidget(self.ideaText)

        self.ideaText.nameChanged.connect(self.handleNameChanged)
        
        self.setLayout(layout)

    def reload(self):
        # TODO: clear?
        pass

    def getInternalName(self):
        result = self.ideaText.internalName.text()
        if len(result) == 0:
            result = "unnamed"
        return result

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
        self.ideaText.setTree(bonusKey)
        self.ideaBonuses.setTree(bonusData)

    def getCost(self):
        return self.ideaBonuses.getCost()

    def getNegativeCost(self):
        return self.ideaBonuses.getNegativeCost()

    def getPenalties(self):
        yellowCards, redCards = [], []
        
        # check exessive cost
        cost = self.getCost()
        if cost < 0.0:
            redCards.append("Idea %s has negative cost." % (self.getName(),))

        if self.ideaType == "traditions":
            if cost > 4.0:
                yellowCards.append("Cost of traditions exceeds 4.00.")
        elif self.ideaType is None:
            if cost > 3.0:
                yellowCards.append("Cost of idea %s exceeds 3.00." % (self.getName(),))


        # duplicate bonuses in same idea

        bonusTypes = list(self.ideaBonuses.getBonusTypes())

        for i, bonusType in enumerate(bonusTypes):
            if bonusType in bonusTypes[i+1:]:
                redCards.append("Idea %s has duplicate bonuses in %s." % (self.getName(), bonusType,))

        return yellowCards, redCards

    def handleCostChanged(self):
        self.costChanged.emit()

    def handleNameChanged(self):
        self.nameChanged.emit()

    def isEmpty(self):
        return not any(bonus.getValue() is not None for bonus in self.ideaBonuses.bonuses) 

class IdeaText(QGroupBox):
    nameChanged = pyqtSignal()
    
    def __init__(self, ideaType=None, parent=None):
        super().__init__("Text", parent=parent)
        layout = QFormLayout()

        # internal name
        if ideaType is None:
            self.internalName = QLineEdit()
            self.internalName.setValidator(internalNameValidator)

            layout.addRow(QLabel("Internal name:"), self.internalName)

        # human name
        self.name = QLineEdit()
        layout.addRow(QLabel("Name:"), self.name)

        if ideaType is None:
            self.description = QTextEdit()

            layout.addRow(QLabel("Description:"), self.description)
        
        self.setLayout(layout)

        # signal
        self.name.textChanged.connect(self.handleNameChanged)

    def setTree(self, bonusKey):
        if bonusKey not in ("start", "bonus"):
            self.internalName.setText(bonusKey + "_custom")
            self.name.setText(pyradox.yml.getLocalization(bonusKey, sources = eu4cd.gamedata.localizationSources) or "")
            self.description.setText(pyradox.yml.getLocalization(bonusKey + "_desc", sources = eu4cd.gamedata.localizationSources) or "")

    def handleNameChanged(self):
        self.nameChanged.emit()
        

class IdeaBonuses(QGroupBox):
    costChanged = pyqtSignal()
    
    def __init__(self, ideaType = None, parent=None):
        super().__init__("Bonuses", parent=parent)

        self.ideaType = ideaType

        layout = QFormLayout()

        self.bonuses = []

        if ideaType == "traditions":
            self.nBonuses = 2
        elif ideaType == "ambitions":
            self.nBonuses = 1
        else:
            self.nBonuses = 3

        for i in range(self.nBonuses):
            allowNone = (ideaType is None) and i > 0
            if allowNone:
                initialIndex = 0
            else:
                initialIndex = i + 1
            ideaBonus = IdeaBonus(initialIndex = initialIndex, allowNone = allowNone)
            ideaBonus.costChanged.connect(self.handleCostChanged)
            self.bonuses.append(ideaBonus)
            layout.addRow(QLabel("Bonus %d:" % (i + 1,)), self.bonuses[i])
        
        self.setLayout(layout)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        self.setToolTip("Total cost for each idea should not be negative or too large. Taking duplicates of some bonuses will result in penalty cards.")

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
                if bonusType not in eu4cd.ideaoptions.bonusTypes: 
                    print("Unknown bonus type %s." % bonusType)
                    continue
                bonus.setBonusTypeIndex(eu4cd.ideaoptions.bonusTypes.index(bonusType))
                valueIndex = eu4cd.ideaoptions.getClosestValueIndex(bonus.values, bonusValue)
                bonus.bonusValueSelect.setCurrentIndex(valueIndex)
            else:
                bonus.setBonusTypeIndex(0)

    def getCost(self):
        return sum(bonus.getCost() for bonus in self.bonuses)

    def getNegativeCost(self):
        return sum(min(bonus.getCost(), 0.0) for bonus in self.bonuses)

    def handleCostChanged(self):
        self.costChanged.emit()

    def getBonusTypes(self):
        for bonus in self.bonuses:
            if bonus.getValue() is not None:
                yield bonus.getType()

class IdeaBonus(QWidget):
    costChanged = pyqtSignal()
    
    def __init__(self, initialIndex = 0, allowNone = True, parent=None):
        super().__init__(parent=parent)

        self.allowNone = allowNone

        layout = QHBoxLayout()
        self.bonusTypeSelect = QComboBox()

        if allowNone:
            self.bonusTypeSelect.addItems(eu4cd.ideaoptions.bonusTypes)
        else:
            self.bonusTypeSelect.addItems(eu4cd.ideaoptions.bonusTypes[1:])
        layout.addWidget(self.bonusTypeSelect)

        self.bonusValueSelect = QComboBox()
        
        layout.addWidget(self.bonusValueSelect)
        self.setLayout(layout)

        self.bonusTypeSelect.currentIndexChanged.connect(self.resetBonusValue)
        self.bonusValueSelect.currentIndexChanged.connect(self.handleCostChanged)

        # TODO: clean this up
        self.resetBonusValue(0)
        self.setBonusTypeIndex(initialIndex)

    def resetBonusValue(self, selectIndex):
        if self.allowNone:
            index = selectIndex
        else:
            index = selectIndex + 1
        
        options, self.values, self.costs = eu4cd.ideaoptions.generateOptions(index)
        defaultIndex = eu4cd.ideaoptions.getClosestValueIndex(self.values, eu4cd.ideaoptions.bonusNormalValues[index])
        self.bonusValueSelect.clear()
        self.bonusValueSelect.addItems(options)
        self.bonusValueSelect.setCurrentIndex(defaultIndex)

    def getBonusTypeIndex(self):
        if self.allowNone:
            return self.bonusTypeSelect.currentIndex()
        else:
            return self.bonusTypeSelect.currentIndex() + 1

    def setBonusTypeIndex(self, index):
        if self.allowNone:
            self.bonusTypeSelect.setCurrentIndex(index)
        else:
            self.bonusTypeSelect.setCurrentIndex(max(index - 1, 0))

    def getType(self):
        return eu4cd.ideaoptions.bonusTypes[self.getBonusTypeIndex()]

    def getValue(self):
        return self.values[self.bonusValueSelect.currentIndex()]

    def getCost(self):
        return self.costs[self.bonusValueSelect.currentIndex()]

    def handleCostChanged(self):
        self.costChanged.emit()


