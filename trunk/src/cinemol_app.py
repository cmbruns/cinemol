from main_window import MainWindow
from scenes import FiveBallScene, TeapotActor
from cinemol_renderer import CinemolRenderer
from PySide.QtGui import QApplication
import sys

class CinemolApp(QApplication):
    def __init__(self):
        QApplication.__init__(self, sys.argv)
        mainWin = MainWindow()
        renderer = CinemolRenderer()
        renderer.actors.append(FiveBallScene())
        # renderer.actors.append(TeapotActor())
        mainWin.ui.glCanvas.set_gl_renderer(renderer)
        mainWin.show()
        sys.exit(self.exec_())
