import os

import eu4cd.gamedata
import eu4cd.idea
import eu4cd.mod
import eu4cd.overview
import eu4cd.rating

import pyradox.struct
import pyradox.txt

from PyQt5.QtWidgets import (
    QAction,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QTabWidget,
    )

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.createMenus()
        self.createStatusBar()
        
        # main widget
        self.main = QTabWidget()
        self.overview = eu4cd.overview.OverviewWidget()
        self.ideas = eu4cd.idea.IdeasWidget()
        self.rating = eu4cd.rating.RatingWidget()
        
        self.main.addTab(self.overview, "Overview")
        self.main.addTab(self.ideas, "Ideas")
        self.main.addTab(self.rating, "Rating")

        self.ideas.costChanged.connect(self.handleCostChanged)
        self.ideas.costChanged.connect(self.handlePenaltiesChanged)
        self.overview.countryLoaded.connect(self.handleCountryLoaded)
        self.overview.penaltiesChanged.connect(self.handlePenaltiesChanged)

        self.setCentralWidget(self.main)
        self.setWindowTitle("Europa Universalis 4 Country Designer")

        self.loadConfig()

    def loadConfig(self, forceManualGamePath=False):
        try:
            config = pyradox.txt.parseFile('config.txt')
        except:
            config = pyradox.struct.Tree()

        gamePathSearch = (
            r'C:\Steam\steamapps\common\Europa Universalis IV',
            r'D:\Steam\steamapps\common\Europa Universalis IV',
            )

        self.gamePath = ""
        if 'gamepath' in config and os.path.exists(config['gamepath']):
            self.gamePath = config['gamepath']
        else:
            for location in gamePathSearch:
                if os.path.exists(location):
                    self.gamePath = location

        if self.gamePath == "" or forceManualGamePath:
            self.gamePath = QFileDialog.getExistingDirectory(caption = "Select Europa Universalis IV directory", dir = self.gamePath)

        if 'modpath' in config and os.path.exists(config['modpath']):
            self.modPath = config['modpath']
        else:
            self.modPath = ""
        try:
            self.reload()
        except Exception as e:
            print(e)
            QMessageBox.critical(None, "Load failed!", "Failed to load game data from %s." % (self.gamePath,))
            self.loadConfig(forceManualGamePath = True)
        else:
            self.writeConfig()

    def writeConfig(self):
        config = pyradox.struct.Tree()
        config['gamepath'] = self.gamePath
        config['modpath'] = self.modPath
        
        f = open('config.txt', 'w')
        f.write(str(config))
        f.close()

    def createMenus(self):
        self.menuFile = self.menuBar().addMenu("&File")
        self.menuFile.addAction(QAction("&Open", self, shortcut="Ctrl+O", statusTip="Open", triggered=lambda: None))
        self.menuFile.addAction(QAction("&Save", self, shortcut="Ctrl+S", statusTip="Save", triggered=self.save))
        self.menuFile.addAction(QAction("E&xit", self, shortcut="Ctrl+Q", statusTip="Exit the application", triggered=self.close))

    def createStatusBar(self):
        self.cost = QLabel()
        self.penalties = QLabel()
        self.statusBar().addPermanentWidget(self.cost)
        self.statusBar().addPermanentWidget(self.penalties)

    def reload(self):
        eu4cd.gamedata.readGameData(self.gamePath)
        self.overview.reload()
        self.ideas.reload()
        self.handleCostChanged(0.0)
        self.handlePenaltiesChanged()

    def save(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Save file", self.modPath, "Mod file (*.mod)")
        
        if not filepath: return

        self.modPath, _ = os.path.split(filepath)

        ideas = pyradox.struct.Tree()

        ideas[self.ideas.getInternalName()] = self.ideas.getTree(self.overview.tag)
        
        events = pyradox.txt.parseFile(os.path.join('eu4cd', 'txt', 'convert_provinces.txt'))
        events["namespace"] = "eu4cd_%s_events" % (self.overview.tag,)
        events["country_event"]["id"] = "eu4cd_%s_events.1" % (self.overview.tag,)
        events["country_event"]["trigger"]["tag"] = self.overview.tag
        if self.overview.religionConvert.isChecked():
            events["country_event"]["trigger"]["always"] = True
        else:
            events["country_event"]["trigger"]["always"] = False
        
        localization = {
            "eu4cd_convert_provinces_event_title" : "The True Faith",
            "eu4cd_convert_provinces_event_desc" : "$COUNTRYNAME$ follows the one true faith of $COUNTRY_RELIGION$.",
            "eu4cd_convert_provinces_event_option" : "Excellent",
            }
        localization.update(self.ideas.getLocalization(self.overview.tag))
        localization.update(self.overview.getLocalization())

        try:
            eu4cd.mod.writeMod(filepath,
                               tag = self.overview.tag,
                               countryBasename = self.overview.getFileBasename(),
                               countryData = self.overview.getTree(),
                               ideas=ideas,
                               events=events,
                               localization=localization)
        except Exception as e:
            print(e)
            QMessageBox.critical(None, "Save failed!", "Failed to save mod to %s." % (filepath,))
        else:
            self.writeConfig()

    def handleCostChanged(self, cost):
        self.cost.setText("National ideas cost: %0.2f (%s)" % (cost, eu4cd.rating.getIdeaRating(cost)))
        self.rating.handleCostChanged(cost)

    def handlePenaltiesChanged(self):
        yellowOverview, redOverview = self.overview.getPenalties()
        yellowIdeas, redIdeas = self.ideas.getPenalties()
        
        yellow = yellowOverview + yellowIdeas
        red = redOverview + redIdeas
        
        self.penalties.setText("%d yellow card(s), %d red card(s)" % (len(yellow), len(red)))
        self.rating.handlePenaltiesChanged(yellow, red)

    def handleCountryLoaded(self):
        self.ideas.setInternalName(self.overview.tag + "_custom_ideas")
        self.ideas.setName(self.overview.adjective.text() + " Ideas")
