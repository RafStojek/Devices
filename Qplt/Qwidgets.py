from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

class Qplt(QWidget):
    # constructor
    def __init__(self,Name = "New plot" , parent=None):
        super(Qplt, self).__init__(parent)
        # a figure instance to plot on
        self.figure = plt.figure()
  
        # this is the Canvas Widget that
        # displays the 'figure'it takes the
        # 'figure' instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
  
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)
  
        # creating a Vertical Box layout
        layout = QVBoxLayout()
        
        if Name:
            layout.addWidget(QLabel(Name))

        # adding tool bar to the layout
        layout.addWidget(self.toolbar)
          
        # adding canvas to the layout
    
        layout.addWidget(self.canvas)
          
        # setting layout to the main window
        self.setLayout(layout)
    # action called by the push button
    def NewAx(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        return ax
    
    def Plot(self):
        self.canvas.draw()
