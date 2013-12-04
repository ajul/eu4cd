from PyQt5.QtCore import (
    QStringListModel,
    )

from PyQt5.QtWidgets import (
    QAbstractItemView,
    QColumnView,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QWidget,
    )

class RatingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # cost display
        self.cost = QGroupBox("National ideas")
        costLayout = QFormLayout()

        self.costDisplay = QLineEdit()
        self.costDisplay.setReadOnly(True)
        costLayout.addRow(QLabel("Cost"), self.costDisplay)

        self.costRating = QLineEdit()
        self.costRating.setReadOnly(True)
        costLayout.addRow(QLabel("Rating"), self.costRating)

        self.cost.setLayout(costLayout)

        # penalty display
        self.penalties = QGroupBox("Penalties")
        penaltiesLayout = QFormLayout()

        self.yellowCardCount = QLineEdit()
        self.yellowCardCount.setReadOnly(True)
        penaltiesLayout.addRow(QLabel("Yellow cards:"), self.yellowCardCount)

        self.yellowCardDisplay = QListView()
        self.yellowCardDisplay.setSelectionMode(QAbstractItemView.NoSelection)
        self.yellowCards = QStringListModel()
        self.yellowCardDisplay.setModel(self.yellowCards)
        penaltiesLayout.addRow(self.yellowCardDisplay)

        self.redCardCount = QLineEdit()
        self.redCardCount.setReadOnly(True)
        penaltiesLayout.addRow(QLabel("Red cards:"), self.redCardCount)

        self.redCardDisplay = QListView()
        self.redCardDisplay.setSelectionMode(QAbstractItemView.NoSelection)
        self.redCards = QStringListModel()
        self.redCardDisplay.setModel(self.redCards)
        penaltiesLayout.addRow(self.redCardDisplay)

        self.penalties.setLayout(penaltiesLayout)

        layout = QHBoxLayout()

        layout.addWidget(self.cost)
        layout.addWidget(self.penalties)

        self.setLayout(layout)

    def handleCostChanged(self, cost):
        self.costDisplay.setText("%0.2f" % (cost,))
        self.costRating.setText(getIdeaRating(cost))

    def handlePenaltiesChanged(self, yellow, red):
        self.yellowCardCount.setText("%d" % (len(yellow),))
        self.yellowCards.setStringList(yellow)
        self.redCardCount.setText("%d" % (len(red),))
        self.redCards.setStringList(red)
    
def getIdeaRating(cost):
    for maxCost, rating in ideaRatings[:-1]:
        if cost <= maxCost: return rating
    return ideaRatings[-1]

ideaRatings = (
    (7.0, "Cannot into relevant"),
    (9.0, "Cannot into stronk"),
    (11.0, "Normal"),
    (13.0, "Stronk"),
    (15.0, "Stronkest"),
    "Überstronk",
    )
