from qtpy.QtWidgets import QPushButton, QSizePolicy
from qtpy.QtCore import QSize


class MainWindowButton(QPushButton):

    def __init__(self, parent):
        super(MainWindowButton, self).__init__(parent)
        sizepolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizepolicy.setHorizontalStretch(0)
        sizepolicy.setVerticalStretch(0)

        self.setMinimumSize(QSize(100, 100))
        self.setIconSize(QSize(50, 50))



