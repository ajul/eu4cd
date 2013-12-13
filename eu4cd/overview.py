import eu4cd.gamedata
import pyradox.txt
import pyradox.yml

import os

from PyQt5.QtCore import (
    pyqtSignal,
    )
from PyQt5.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QWidget,
    )

class OverviewWidget(QWidget):
    countryLoaded = pyqtSignal()
    penaltiesChanged = pyqtSignal()
    adjectiveChanged = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QFormLayout()

        self.tagSelect = eu4cd.gamedata.TagSelect()
        layout.addRow(QLabel("Tag:"), self.tagSelect)

        self.name = QLineEdit()
        layout.addRow(QLabel("Name:"), self.name)

        self.adjective = QLineEdit()
        layout.addRow(QLabel("Adjective:"), self.adjective)


        technologyGroupToolTipText = "Upgrading starting technology group will give a penalty card."
        technologyGroupLabel = QLabel("Technology group:")
        technologyGroupLabel.setToolTip(technologyGroupToolTipText)
        self.technologyGroupSelect = eu4cd.gamedata.TechnologyGroupSelect()
        self.technologyGroupSelect.setToolTip(technologyGroupToolTipText)
        layout.addRow(technologyGroupLabel, self.technologyGroupSelect)
        
        self.religionSelect = eu4cd.gamedata.ReligionSelect()
        layout.addRow(QLabel("Religion:"), self.religionSelect)

        religionConvertToolTipText = "If checked, all provinces will be converted via event at game start."
        religionConvertLabel = QLabel("Convert religion:")
        religionConvertLabel.setToolTip(religionConvertToolTipText)
        self.religionConvert = QCheckBox()
        self.religionConvert.setToolTip(religionConvertToolTipText)
        layout.addRow(religionConvertLabel, self.religionConvert)

        self.governmentSelect = eu4cd.gamedata.GovernmentSelect()
        layout.addRow(QLabel("Government:"), self.governmentSelect)

        mercantilismToolTip = "Republics start with higher mercantilism."
        mercantilismLabel = QLabel("Mercantilism:")
        mercantilismLabel.setToolTip(mercantilismToolTip)
        self.mercantilism = QLineEdit()
        self.mercantilism.setToolTip(mercantilismToolTip)
        self.mercantilism.setReadOnly(True)
        layout.addRow(mercantilismLabel, self.mercantilism)
        
        self.setLayout(layout)

        # signals
        self.tagSelect.currentIndexChanged.connect(self.loadCountry)
        self.governmentSelect.currentIndexChanged.connect(self.handleGovernmentChanged)
        self.technologyGroupSelect.currentIndexChanged.connect(self.handleTechnologyGroupChanged)
        self.adjective.textChanged.connect(self.handleAdjectiveChanged)

    def reload(self):
        self.tagSelect.reload()
        self.technologyGroupSelect.reload()
        self.religionSelect.reload()
        self.governmentSelect.reload()

    def loadCountry(self, index):
        if index >= 0:
            self.tag = eu4cd.gamedata.tags[index]
            self.name.setText(eu4cd.gamedata.tagNames[index])
            adjective = eu4cd.gamedata.tagAdjectives[index]
            self.adjective.setText(adjective)
            
            self.countryData = pyradox.txt.parseFile(eu4cd.gamedata.tagFiles[index])
            self.defaultTechnologyGroup = eu4cd.gamedata.technologyGroups.index(self.countryData["technology_group"])
            self.technologyGroupSelect.setCurrentIndex(self.defaultTechnologyGroup)
            self.religionSelect.setCurrentIndex(eu4cd.gamedata.religions.index(self.countryData["religion"]))
            self.governmentSelect.setCurrentIndex(eu4cd.gamedata.governments.index(self.countryData["government"]))

        self.countryLoaded.emit()

    def getLocalization(self):
        return {
            self.tag : self.name.text(),
            self.tag + "_ADJ" : self.adjective.text(),
            }

    def getFileBasename(self):
        _, basename = os.path.split(eu4cd.gamedata.tagFiles[self.tagSelect.currentIndex()])
        return basename

    def getTree(self):
        result = self.countryData.deepCopy()

        result.deleteWalk("technology_group")
        result.deleteWalk("religion")
        result.deleteWalk("government")
        result.deleteWalk("mercantilism")

        result.insert(0, "technology_group", eu4cd.gamedata.technologyGroups[self.technologyGroupSelect.currentIndex()])
        result.insert(0, "religion", eu4cd.gamedata.religions[self.religionSelect.currentIndex()])
        result.insert(0, "government", eu4cd.gamedata.governments[self.governmentSelect.currentIndex()])
        
        result.insert(0, "mercantilism", eu4cd.gamedata.governmentMercantilisms[self.governmentSelect.currentIndex()])

        return result

    def handleTechnologyGroupChanged(self, index):
        self.penaltiesChanged.emit()

    def getPenalties(self):
        yellowCards = []
        redCards = []
        
        # tech group changed?
        technologyGroup = self.technologyGroupSelect.currentIndex()
        if technologyGroup < self.defaultTechnologyGroup:
            if technologyGroup != 0:
                yellowCards.append("Upgraded technology group to non-Western.")
            elif eu4cd.gamedata.technologyPowers[self.defaultTechnologyGroup] >= eu4cd.gamedata.technologyPowers[0]:
                yellowCards.append("Upgraded technology group to Western from same power.")
            else:
                redCards.append("Upgraded technology group to Western from lower power.")

        return yellowCards, redCards

    def handleGovernmentChanged(self, index):
        self.mercantilism.setText("%0.1f%%" % (eu4cd.gamedata.governmentMercantilisms[index] * 100.0))

    def handleAdjectiveChanged(self, adjective):
        self.adjectiveChanged.emit(adjective)
