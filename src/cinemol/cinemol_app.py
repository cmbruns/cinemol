import logging
logging.basicConfig()

from gui.main_window import MainWindow
import console_context
from scenes import FiveBallScene, Sphere2TestScene
from cinemol_renderer import CinemolRenderer
from PySide.QtGui import QApplication
import sys


class CinemolApp(object):
    def __init__(self):
        pass
    
    def launch(self):
        self.app = QApplication(sys.argv)
        self.app.setOrganizationName("rotatingpenguin.com")
        self.app.setApplicationName("Cinemol")
        self.mainWin = MainWindow()
        self.renderer = CinemolRenderer()
        # self.renderer.actors.append(Sphere2TestScene())
        self.renderer.actors.append(FiveBallScene())
        # self.renderer.actors.append(TeapotActor())
        self.mainWin.ui.glCanvas.set_gl_renderer(self.renderer)
        console_context.cm._set_app(self)
        self.mainWin.show()
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    CinemolApp().launch()
