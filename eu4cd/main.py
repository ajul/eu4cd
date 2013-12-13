import os

import webbrowser
import traceback

import eu4cd.gamedata
import eu4cd.idea
import eu4cd.mod
import eu4cd.overview
import eu4cd.rating

import pyradox.struct
import pyradox.txt

from PyQt5.QtWidgets import (
    QAction,
    QDialog,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSizePolicy,
    QTabWidget,
    )

version = '0.5'

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
        self.ideas.ideaNamesChanged.connect(self.handleIdeaNamesChanged)
        self.overview.countryLoaded.connect(self.handleCountryLoaded)
        self.overview.penaltiesChanged.connect(self.handlePenaltiesChanged)
        self.overview.adjectiveChanged.connect(self.handleAdjectiveChanged)

        self.setCentralWidget(self.main)
        self.setWindowTitle("Unofficial Europa Universalis IV Country Designer")

        self.loadConfig()

    def loadConfig(self, automatic=True, optional=False):
        try:
            config = pyradox.txt.parseFile('config.txt')
        except:
            config = pyradox.struct.Tree()

        if optional:
            gamePath = QFileDialog.getExistingDirectory(caption = "Select Europa Universalis IV directory", directory = self.gamePath)
            if gamePath == "":
                return # canceled
            else:
                self.gamePath = gamePath
        else:
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

            if self.gamePath == "" or not automatic:
                self.gamePath = QFileDialog.getExistingDirectory(caption = "Select Europa Universalis IV directory", directory = self.gamePath)

            if 'modpath' in config and os.path.exists(config['modpath']):
                self.modPath = config['modpath']
            else:
                homeDir = os.path.expanduser("~")
                self.modPath = os.path.join(homeDir, "Documents", "Paradox Interactive", "Europa Universalis IV", "mod")
                if not os.path.exists(self.modPath):
                    self.modPath = ""
        try:
            self.reload()
        except IOError as e:
            print(traceback.format_exc())
            QMessageBox.critical(None, "Load failed!", "Could not read game data from %s: %s" % (self.gamePath, e))
            self.loadConfig(automatic=False)
        except pyradox.txt.ParseError as e:
            print(traceback.format_exc())
            QMessageBox.critical(None, "Load failed!", "Syntax error when reading game data from %s:\n%s" % (self.gamePath, e))
            self.loadConfig(automatic=False)
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
        def openParadoxplaza():
            webbrowser.open("about:blank") # fill in
            
        def openSourceforge():
            webbrowser.open("https://sourceforge.net/projects/eu4cd/")
        
        self.menuFile = self.menuBar().addMenu("&File")
        self.menuFile.addAction(QAction("L&oad game data", self, shortcut="Ctrl+O", statusTip="Load game data", triggered=lambda: self.loadConfig(optional=True)))
        self.menuFile.addAction(QAction("&Save mod", self, shortcut="Ctrl+S", statusTip="Save mod", triggered=self.save))
        self.menuFile.addSeparator()
        self.menuFile.addAction(QAction("E&xit", self, shortcut="Ctrl+Q", statusTip="Exit the application", triggered=self.close))

        self.menuHelp = self.menuBar().addMenu("&Help")
        self.menuHelp.addAction(QAction("&Paradoxplaza forum topic", self, statusTip="Visit the forum topic", triggered=openParadoxplaza))
        self.menuHelp.addAction(QAction("&Sourceforge project page", self, statusTip="Visit the project page", triggered=openSourceforge))
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(QAction("&About", self, statusTip="View version and license information", triggered=self.about))

    def about(self):
        dialog = AboutBox()
        dialog.exec()
        

    def createStatusBar(self):
        self.cost = QLabel()
        self.penalties = QLabel()
        self.cost.setToolTip(eu4cd.rating.costToolTipText)
        self.penalties.setToolTip(eu4cd.rating.penaltiesToolTipText)
        self.statusBar().addPermanentWidget(self.cost)
        self.statusBar().addPermanentWidget(self.penalties)

    def reload(self):
        eu4cd.gamedata.readGameData(self.gamePath)
        self.overview.reload()
        self.ideas.reload()
        self.handleCostChanged([0.0] * 9)
        self.handlePenaltiesChanged()

    def save(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Save mod", self.modPath, "Mod file (*.mod)")
        
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
            "eu4cd_convert_provinces_event_title" : "The One True Faith",
            "eu4cd_convert_provinces_event_desc" : "Our glorious nation of $COUNTRY$ follows the One True Faith of $COUNTRY_RELIGION$.",
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
        except IOError as e:
            print(traceback.format_exc())
            QMessageBox.critical(None, "Save failed!", "Could not save mod to %s:\n%s" % (filepath, e))
        else:
            self.writeConfig() # successful save, write mod path to config
            self.statusBar().showMessage("Saved mod to %s." % (filepath,), 5000)

    def handleCostChanged(self, costs):
        totalCost = sum(costs)
        self.cost.setText("National ideas cost: %0.2f points (%s)" % (totalCost, eu4cd.rating.getIdeaRating(totalCost)))
        self.rating.handleCostChanged(costs)

    def handleIdeaNamesChanged(self, names):
        self.rating.handleIdeaNamesChanged(names)

    def handlePenaltiesChanged(self):
        yellowOverview, redOverview = self.overview.getPenalties()
        yellowIdeas, redIdeas = self.ideas.getPenalties()
        
        yellow = yellowOverview + yellowIdeas
        red = redOverview + redIdeas
        
        self.penalties.setText("%d yellow card(s), %d red card(s)" % (len(yellow), len(red)))
        self.rating.handlePenaltiesChanged(yellow, red)

    def handleCountryLoaded(self):
        self.ideas.setInternalName(self.overview.tag + "_custom_ideas")

    def handleAdjectiveChanged(self, adjective):
        self.ideas.setName(adjective + " Ideas")
        self.ideas.tabs.traditions.setName(adjective + " Traditions")
        self.ideas.tabs.ambitions.setName(adjective + " Ambitions")

class AboutBox(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        self.setText("Unofficial Europa Universalis IV Country Designer")
        self.setInformativeText("Version %s" % version)
        
        f = open("license.txt")
        licenseText = f.read()
        f.close()
        self.setDetailedText(licenseText)
