import numpy as np

from PICOSCOPE.PICOsdk.API import QPICO5000
from Qplt.Qwidgets import Qplt

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import multiprocessing.dummy as mp
import time
import os
import sys

class App(QWidget):
    def __init__(self,parent=None):

        super(App, self).__init__(parent)
        self.CreateGUI()
      
    def CreateGUI(self):
        self.MainGrid = QGridLayout()
        self.Tab = QTabWidget()

        self.PlotingPanel1 = Qplt(Name="1st plot")
        self.PlotingPanel2 = Qplt(Name = "2nd plot")
        self.Queue = mp.Queue(10)
        self.PICOTab = QPICO5000(self.Queue)

        self.Tab.addTab(self.PlotingPanel1,"Chart A")
        self.Tab.addTab(self.PlotingPanel2,"Chart B")

        self.Tab.addTab(self.PICOTab,"PICOSCOPE")
        self.MainGrid.addWidget(self.Tab)

        self.setLayout(self.MainGrid)

if __name__ == '__main__':# creating apyqt5 application
    
    app = QApplication(sys.argv)
  
    # creating a window object
    main = App()
      
    # showing the window
    main.show()
  
    # loop
    sys.exit(app.exec_())