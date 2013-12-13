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

        self.costRating = QLineEdit()
        self.costRating.setReadOnly(True)
        costLayout.addRow(QLabel("Rating:"), self.costRating)

        self.costDisplay = QLineEdit()
        self.costDisplay.setReadOnly(True)
        costLayout.addRow(QLabel("Cost:"), self.costDisplay)

        possibleRatings = QGroupBox("Possible ratings")
        possibleRatingsLayout = QFormLayout()
        for cost, rating in ideaRatings:
            if cost is not None:
                possibleRatingsLayout.addRow(QLabel("Up to %0.1f:" % (cost),), QLabel(rating))
            else:
                possibleRatingsLayout.addRow(QLabel("Above:"), QLabel(rating))
        possibleRatings.setLayout(possibleRatingsLayout)
        costLayout.addRow(possibleRatings)

        self.cost.setLayout(costLayout)

        # penalty display
        self.penalties = QGroupBox("Penalties")
        penaltiesLayout = QFormLayout()

        # self.penaltiesRating = QLineEdit()
        # self.penaltiesRating.setReadOnly(True)
        # penaltiesLayout.addRow(QLabel("Rating:"), self.penaltiesRating)
        
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
        # self.penaltiesRating.setText(getPenaltiesRating(len(yellow), len(red)))
    
def getIdeaRating(cost):
    for maxCost, rating in ideaRatings[:-1]:
        if cost <= maxCost: return rating
    return ideaRatings[-1][1]

def getPenaltiesRating(yellowCount, redCount):
    if redCount > 0 or yellowCount > 1:
        return "Red"
    elif yellowCount > 0:
        return "Yellow"
    else:
        return "Green"

ideaRatings = (
    (7.0, "Cannot into relevant"),
    (9.0, "Cannot into stronk"),
    (11.0, "Normal"),
    (13.0, "Stronk"),
    (15.0, "Stronkest"),
    (None, "Überstronk"),
    )
