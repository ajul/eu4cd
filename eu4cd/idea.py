import re

import eu4cd.gamedata
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
        cost += self.traditions.getCost()
        for idea in self.ideas:
            cost += idea.getCost()
        cost += self.ambitions.getCost()
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

        return yellowCards, redCards

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
            self.internalName.setText(bonusKey)
            self.name.setText(pyradox.yml.getLocalization(bonusKey, sources = ["text", "countries", "EU4", "powers_and_ideas"]) or "")
            self.description.setText(pyradox.yml.getLocalization(bonusKey + "_desc", sources = ["text", "countries", "EU4", "powers_and_ideas"]) or "")
        

class IdeaBonuses(QGroupBox):
    costChanged = pyqtSignal()

    nBonuses = 2
    
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
        for i in range(self.nBonuses):
            if len(bonuses) > i:
                bonusType, bonusValue = bonuses.at(i)
                if bonusType not in bonusTypes: continue
                self.bonuses[i].bonusTypeSelect.setCurrentIndex(bonusTypes.index(bonusType))
                valueIndex = getClosestValueIndex(self.bonuses[i].values, bonusValue)
                self.bonuses[i].bonusValueSelect.setCurrentIndex(valueIndex)
            else:
                self.bonuses[i].bonusTypeSelect.setCurrentIndex(0)

    def getCost(self):
        return sum(bonus.getCost() for bonus in self.bonuses)

    def handleCostChanged(self):
        self.costChanged.emit()

class IdeaBonus(QWidget):
    costChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        layout = QHBoxLayout()
        self.bonusTypeSelect = QComboBox()
        self.bonusTypeSelect.addItems(bonusTypes)
        layout.addWidget(self.bonusTypeSelect)

        self.bonusValueSelect = QComboBox()
        
        layout.addWidget(self.bonusValueSelect)
        self.setLayout(layout)

        self.resetBonusValue(0)

        self.bonusTypeSelect.currentIndexChanged.connect(self.resetBonusValue)
        self.bonusValueSelect.currentIndexChanged.connect(self.handleCostChanged)

    def resetBonusValue(self, index):
        options, self.values, self.costs = generateOptions(bonusNormalValue[index], bonusRange[index])
        defaultIndex = getClosestValueIndex(self.values, bonusNormalValue[index])
        self.bonusValueSelect.clear()
        self.bonusValueSelect.addItems(options)
        self.bonusValueSelect.setCurrentIndex(defaultIndex)

    def getType(self):
        return bonusTypes[self.bonusTypeSelect.currentIndex()]

    def getValue(self):
        return self.values[self.bonusValueSelect.currentIndex()]

    def getCost(self):
        return self.costs[self.bonusValueSelect.currentIndex()]

    def handleCostChanged(self):
        self.costChanged.emit()


def generateOptions(normalValue, valueRange):
    if normalValue > 0:
        sign = 1
    else:
        sign = -1
    
    if valueRange[0] is None:
        options = ["(none): 0.00 point(s)"]
        values = [None]
        costs = [0.0]
    elif isinstance(valueRange[0], bool):
        cost = 1.0 / normalValue
        options = ["yes: %0.2f point(s)" % (cost,)]
        values = [True]
        costs = [cost]
    elif isinstance(valueRange[0], int):
        options = []
        values = []
        costs = []

        i = 0

        for value in range(valueRange[0] * sign, valueRange[1] * sign + 1):
            cost = value / normalValue * sign
            options.append("%d: %0.2f point(s)" % (value * sign, cost))
            values.append(value * sign)
            costs.append(cost)

            i += 1
            
    else: # float
        options = []
        values = []
        costs = []

        i = 0

        for value in floatValues:
            if value < valueRange[0] * sign: continue
            if value > valueRange[1] * sign: continue

            cost = value / normalValue * sign
            options.append("%0.3f: %0.2f point(s)" % (value * sign, cost))
            values.append(value * sign)
            costs.append(cost)

            i += 1

    return options, values, costs

def getClosestValueIndex(values, target):
    if values[0] is True or values[0] is None: return 0
    
    difference = abs(values[0] - target)
    result = 0
    for i, value in enumerate(values):
        currDifference = abs(value - target)
        if currDifference < difference:
            difference = currDifference
            result = i
    return result
    

floatValues = (
    0.002, 0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.05, 0.06, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3, 0.33, 0.5, 0.66, 0.75, 1.0, 2.0,
    )
        
bonusData = (
    ("(none)",                      1, (None, None)), # special
    ("adm_tech_cost_modifier",      -0.1, (-0.05, -0.25)), # unused
    ("advisor_cost",                -0.1, (-0.05, -0.25)),
    ("advisor_pool",                1, (1, 2)),
    ("army_tradition",              1.0, (0.25, 1.0)),
    ("army_tradition_decay",        -0.01, (-0.005, -0.01)),
    ("artillery_cost",              -0.1, (-0.05, -0.2)),
    ("artillery_power",             0.1, (0.05, 0.2)),
    ("auto_explore_adjacent_to_colony", 2.0, (True, True)), # bool), cost 1/2
    ("blockade_efficiency",         0.33, (0.33, 0.33)), #?
    ("build_cost",                  -0.2, (-0.1, -0.33)), #-0.1 to -0.2?
    ("cavalry_cost",                -0.1, (-0.05, -0.2)),
    ("cavalry_power",               0.1, (0.05, 0.25)),
    ("cb_on_government_enemies",    1.0, (True, True)), # bool
    ("cb_on_overseas",              1.0, (True, True)), # bool
    ("cb_on_primitives",            1.0, (True, True)), # bool
    ("cb_on_religious_enemies",     1.0, (True, True)), # bool
    ("colonists",                   1, (1, 1)),
    ("colonist_time",               -0.33, (-0.1, -0.33)), # Expansion only
    ("core_creation",               -0.15, (-0.1, -0.33)),
    ("defensiveness",               0.2, (0.1, 0.3)),
    ("dip_tech_cost_modifier",      -0.1, (-0.05, -0.25)), # unused
    ("diplomatic_reputation",       2, (1, 5)),
    ("diplomatic_upkeep",           2, (1, 3)),
    ("diplomats",                   1, (1, 1)),
    ("discipline",                  0.1, (0.05, 0.2)),
    ("discovered_relations_impact", -0.25, (-0.1, -0.25)),
    ("embargo_efficiency",          0.33, (0.1, 0.33)),
    ("enemy_core_creation",         1.0, (0.5, 2.0)),
    ("extra_manpower_at_religious_war", 1.0, (True, True)), # bool
    ("fabricate_claims_time",       -0.25, (-0.1, -0.25)),
    ("free_leader_pool",            1, (1, 1)),
    ("galley_cost",                 -0.2, (-0.1, -0.33)),
    ("galley_power",                0.2, (0.1, 0.5)), #?
    ("global_colonial_growth",      25, (15, 50)), #?
    ("global_foreign_trade_power",  0.2, (0.05, 0.25)), # adjusted downwards
    ("global_manpower_modifier",    0.33, (0.05, 1.0)), # 0.2 to 0.5?
    ("global_garrison_growth",      0.1, (0.05, 0.2)),
    ("global_missionary_strength",  0.02, (0.01, 0.03)),
    ("global_own_trade_power",      0.2, (0.05, 0.25)), 
    ("global_prov_trade_power_modifier", 0.2, (0.05, 0.25)),
    ("global_regiment_cost",        -0.1, (-0.05, -0.1)), #Poland only
    ("global_regiment_recruit_speed", -0.2, (-0.1, -0.25)), # Prussia only
    ("global_revolt_risk",          -1, (-1, -2)),
    ("global_ship_cost",            -0.1, (-0.05, -0.1)),
    ("global_ship_recruit_speed",   -0.1, (-0.05, -0.1)),
    ("global_spy_defence",          0.25, (0.05, 0.1)),
    ("global_tariffs",              0.1, (0.05, 0.1)), # Spain only
    ("global_tax_modifier",         0.1, (0.05, 0.2)),
    ("global_trade_income_modifier", 0.1, (0.05, 0.2)),
    ("global_trade_power",          0.1, (0.05, 0.2)),
    ("heavy_ship_power",            0.1, (0.05, 0.25)),
    ("heir_chance",                 0.5, (0.25, 1.0)),
    ("hostile_attrition",           1.0, (0.5, 1.0)),
    ("idea_claim_colonies",         1.0, (True, True)), # bool
    ("idea_cost",                   -0.1, (-0.05, -0.1)),
    ("imperial_authority",          0.1, (0.05, 0.1)), #split between 0.1 and 0.05
    ("infantry_cost",               -0.2, (-0.1, -0.33)), #OP?
    ("infantry_power",              0.1, (0.05, 0.25)),
    ("inflation_action_cost",       -0.15, (-0.1, -0.2)),
    ("inflation_reduction",         0.1, (0.05, 0.1)), #split between 0.1 and 0.05
    ("interest",                    -1.0, (-0.5, -1)),
    ("land_attrition",              -0.1, (-0.05, -0.2)),
    ("land_forcelimit_modifier",    0.25, (0.1, 0.5)), # few examples
    ("land_maintenance_modifier",   -0.15, (-0.1, -0.25)), # decrease cost?
    ("land_morale",                 0.15, (0.1, 0.5)), # 0.1 to 0.25? OP?
    ("leader_fire",                 2/3, (1, 1)), # adjusted upwards
    ("leader_land_manuever",        1, (1, 1)),
    ("leader_naval_manuever",       2, (1, 2)),
    ("leader_shock",                2/3, (1, 1)), # adjusted upwards
    ("leader_siege",                2/3, (1, 1)), # adjusted upwards
    ("legitimacy",                  1.0, (0.25, 1.0)),
    ("light_ship_cost",             -0.2, (-0.01, -0.33)),
    ("light_ship_power",            0.1, (0.05, 0.2)),
    ("manpower_recovery_speed",     0.2, (0.1, 0.33)),
    ("may_explore",                 1.0, (True, True)), # bool
    ("may_force_march",             1.0, (True, True)), # bool
    ("may_infiltrate_administration", 1.0, (True, True)), #bool
    ("may_sabotage_reputation",     1.0, (True, True)), #bool
    ("may_sow_discontent",          1.0, (True, True)), #bool
    ("merc_maintenance_modifier",   -0.25, (-0.1, -0.25)),
    ("mercenary_cost",              -0.25, (-0.1, -0.25)),
    ("merchants",                   1, (1, 1)),
    ("mil_tech_cost_modifier",      -0.1, (-0.05, -0.2)), # Aristocratic only
    ("missionaries",                1, (1, 1)),
    ("naval_attrition",             -0.25, (-0.1, -0.25)),
    ("naval_forcelimit_modifier",   0.25, (0.1, 0.5)), # 0.25 or 0.5?
    ("naval_maintenance_modifier",  -0.25, (-0.1, -0.33)), # -0.2), -0.25), or -0.33?
    ("naval_morale",                0.2, (0.1, 0.5)),
    ("navy_tradition",              1.0, (0.25, 1.0)),
    ("navy_tradition_decay",        -0.01, (-0.005, -0.01)),
    ("no_cost_for_reinforcing",     1.0, (True, True)), # bool
    ("no_religion_penalty",         1.0, (True, True)), # bool
    ("overseas_income",             0.2, (0.1, 0.3)), #0.1 or 0.2?
    ("papal_influence",             2, (1, 5)), # 2 or 3?
    ("possible_mercenaries",        0.5, (0.5, 1.0)),
    ("prestige",                    1.0, (0.5, 2.0)),
    ("prestige_decay",              -0.02, (-0.01, -0.02)),
    ("prestige_from_land",          1.0, (0.5, 1.0)), # Naval only
    ("prestige_from_naval",         1.0, (0.5, 1.0)), # Offensive only
    ("production_efficiency",       0.1, (0.05, 0.2)),
    ("range",                       0.25, (0.2, 0.33)), # 0.25 or 0.33?
    ("rebel_support_efficiency",    0.25, (0.1, 0.5)),
    ("recover_army_morale_speed",   0.05, (0.02, 0.1)),
    ("recover_navy_morale_speed",   0.05, (0.02, 0.1)),
    ("reduced_native_attacks",      1.0, (True, True)), # bool
    ("reduced_stab_impacts",        1.0, (True, True)), # bool
    ("reinforce_speed",             0.2, (0.1, 0.3)), # 0.15 to 0.30?
    ("relations_decay_of_me",       0.3, (0.1, 0.3)),
    ("religious_unity",             0.25, (0.2, 0.5)),
    ("republican_tradition",        0.005, (0.005, 0.01)), # adjusted upwards
    ("sea_repair",                  1.0, (True, True)), # bool
    ("spy_offence",                 0.2, (0.1, 0.25)), # 0.1 to 0.25?
    ("stability_cost_modifier",     -0.1, (-0.05, -0.2)),
    ("technology_cost",             -0.05, (-0.02, -0.1)),
    ("tolerance_heathen",           2, (1, 3)),
    ("tolerance_heretic",           2, (1, 4)),
    ("tolerance_own",               2, (1, 4)),
    ("trade_efficiency",            0.075, (0.05, 0.2)), 
    ("trade_range_modifier",        0.25, (0.05, 0.5)), #0.20 or 0.25?
    ("trade_steering",              0.2, (0.05, 0.5)), # 0.1 to 0.25 ?
    ("unjustified_demands",         -0.25, (-0.05, -0.25)), # Diplomatic only
    ("vassal_income",               0.2, (0.1, 0.5)), # 0.1 to 0.25 ?
    ("war_exhaustion",              -0.02, (-0.01, -0.05)), # Innovative only
    ("war_exhaustion_cost",         -0.2, (-0.1, -0.33)), # -0.1 to -0.2?
    )

bonusTypes, bonusNormalValue, bonusRange = zip(*bonusData)
