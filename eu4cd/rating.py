from PyQt5.QtWidgets import (
    QWidget,
    )

class RatingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def handleCostChanged(self, cost):
        pass

    def handlePenaltiesChanged(self, yellow, red):
        pass
    
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
