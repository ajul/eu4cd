import eu4cd.gamedata
import eu4cd.idea
import eu4cd.mod
import eu4cd.overview
import eu4cd.rating

import pyradox.struct

from PyQt5.QtWidgets import (
    QAction,
    QLabel,
    QMainWindow,
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

        self.gamePath = r'D:\Steam\steamapps\common\Europa Universalis IV' # FIXME

        self.reload()

    def createMenus(self):
        self.menuFile = self.menuBar().addMenu("&File")
        self.menuFile.addAction(QAction("&Open", self, shortcut="Ctrl+O", statusTip="Open", triggered=lambda: None))
        self.menuFile.addAction(QAction("&Save", self, shortcut="Ctrl+S", statusTip="Save", triggered=self.save))
        self.menuFile.addAction(QAction("E&xit", self, shortcut="Ctrl+Q", statusTip="Exit the application", triggered=self.close))

    def createStatusBar(self):
        self.cost = QLabel()
        self.cost.setText("Cost: 0.00")
        self.penalties = QLabel()
        self.penalties.setText("%d yellow cards, %d red cards")
        self.statusBar().addPermanentWidget(self.cost)
        self.statusBar().addPermanentWidget(self.penalties)

    def reload(self):
        eu4cd.gamedata.readGameData(self.gamePath)
        self.overview.reload()
        self.ideas.reload()

    def save(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Save file", "", "Mod file (*.mod)")
        
        if not filepath: return

        ideas = pyradox.struct.Tree()

        ideas[self.ideas.getInternalName()] = self.ideas.getTree(self.overview.tag)
        
        events = None
        
        localization = {}
        localization.update(self.ideas.getLocalization(self.overview.tag))
        localization.update(self.overview.getLocalization())

        countries = {
                self.overview.getFileBasename() : self.overview.getTree(),
            }

        eu4cd.mod.writeMod(filepath, ideas=ideas, events=events, countries=countries, localization=localization)

    def handleCostChanged(self, cost):
        self.cost.setText("Cost: %0.2f (%s)" % (cost, eu4cd.rating.getIdeaRating(cost)))
        self.rating.handleCostChanged(cost)

    def handlePenaltiesChanged(self):
        yellowOverview, redOverview = self.overview.getPenalties()
        yellowIdeas, redIdeas = self.ideas.getPenalties()
        
        yellow = yellowOverview + yellowIdeas
        red = redOverview + redIdeas
        
        self.penalties.setText("%d yellow cards, %d red cards" % (len(yellow), len(red)))
        self.rating.handlePenaltiesChanged(yellow, red)

    def handleCountryLoaded(self):
        self.ideas.setInternalName(self.overview.tag + "_custom_ideas")
        self.ideas.setName(self.overview.adjective.text() + " Ideas")
