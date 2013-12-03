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
    
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QFormLayout()

        self.tagSelect = eu4cd.gamedata.TagSelect()
        layout.addRow(QLabel("Tag:"), self.tagSelect)

        self.name = QLineEdit()
        layout.addRow(QLabel("Name:"), self.name)

        self.adjective = QLineEdit()
        layout.addRow(QLabel("Adjective:"), self.adjective)
        
        self.technologyGroupSelect = eu4cd.gamedata.TechnologyGroupSelect()
        layout.addRow(QLabel("Technology group:"), self.technologyGroupSelect)
        
        self.religionSelect = eu4cd.gamedata.ReligionSelect()
        layout.addRow(QLabel("Religion:"), self.religionSelect)

        religionConvertLabel = QLabel("Convert religion:")
        religionConvertLabel.setToolTip("Convert all provinces via event at game start.")
        self.religionConvert = QCheckBox()
        self.religionConvert.setToolTip("Convert all provinces via event at game start.")
        layout.addRow(religionConvertLabel, self.religionConvert)

        self.governmentSelect = eu4cd.gamedata.GovernmentSelect()
        layout.addRow(QLabel("Government:"), self.governmentSelect)

        self.mercantilismSelect = eu4cd.gamedata.MercantilismSelect()
        layout.addRow(QLabel("Mercantilism:"), self.mercantilismSelect)
        
        self.setLayout(layout)

        # signals
        self.tagSelect.currentIndexChanged.connect(self.loadCountry)
        self.technologyGroupSelect.currentIndexChanged.connect(self.handleTechnologyGroupChanged)

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
            if "mercantilism" in self.countryData and self.countryData["mercantilism"] > 10.0:
                self.mercantilismSelect.setCurrentIndex(1)
            else:
                self.mercantilismSelect.setCurrentIndex(0)

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
        # TODO: recursive
        result["technology_group"] = eu4cd.gamedata.technologyGroups[self.technologyGroupSelect.currentIndex()]
        result["religion"] = eu4cd.gamedata.religions[self.religionSelect.currentIndex()]
        result["government"] = eu4cd.gamedata.governments[self.governmentSelect.currentIndex()]
        
        if self.mercantilismSelect.currentIndex() == 0:
            result["mercantilism"] = 10.0
        else:
            result["mercantilism"] = 25.0

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
            elif self.defaultTechnologyGroup <= 2:
                yellowCards.append("Upgraded technology group from near-Western to Western.")
            else:
                redCards.append("Upgraded technology group from non-near-Western to Western.")
        return yellowCards, redCards
