from qtpy.QtWidgets import QMenu, QPlainTextEdit, QAction
from qtpy.QtCore import Slot, Qt
from qtpy.QtGui import QSyntaxHighlighter, QTextCharFormat


from qrainbowstyle.windows import FramelessWindow


class Highlighter(QSyntaxHighlighter):

    def __init__(self, parent):
        super(Highlighter, self).__init__(parent)
        self.generator_format = QTextCharFormat()
        self.generator_format.setForeground(Qt.yellow)

    def highlightBlock(self, text):
        if text.startswith('<GENERATOR>'):
            self.setFormat(0, len(text), self.generator_format)


class ProgressWindow(FramelessWindow):

    def __init__(self, parent, generator):
        super(ProgressWindow, self).__init__(parent)
        self.__generator = generator

        self.__progress_view = QPlainTextEdit(self)
        self.__highlighter = Highlighter(self.__progress_view.document())
        self.__progress_view.textChanged.connect(self.__on_progress_text)
        self.addContentWidget(self.__progress_view)

        self.menu = QMenu(self.__generator, self)
        close_action = QAction("Close", self.menu)
        close_action.triggered.connect(self.close)
        self.menu.addAction(close_action)
        self.addMenu(self.menu)

    def generator(self):
        return self.__generator

    @Slot(str)
    def appendProgress(self, text):
        self.__progress_view.appendPlainText(text)

    @Slot()
    def setFinished(self):
        pass

    @Slot()
    def setstarted(self):
        pass

    @Slot()
    def __on_progress_text(self):
        self.__progress_view.verticalScrollBar().setValue(self.__progress_view.verticalScrollBar().maximum())
