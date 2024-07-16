from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from PICOSCOPE.PICOsdk import PICO
import multiprocessing.dummy as mp

class QPICO5000(QWidget):
        def __init__(self,RawDataQ):

            super().__init__()
            self.layout=QGridLayout()
            self.PICOdevice = PICO.PicoStream()
            self.RawDataQ = RawDataQ

            Description1 =      "Ten panel umożliwia zmianę domyslnych ustawień karty akwizycji danych picoscope\n"
            Description1 +=     "Domyślne watość to: \n"
            Description1 +=     "Wszystki kanały włączone, coupling DC oraz maksymalna wartość napięcia 1000mV \n"
            Description1 +=     "Pasek mocy po prawej wskazuje aktualne użycie zakresu pomiarowego. \n"
            Description1 +=     "Zaleca się, aby wskaźnik mocy zawierał się między 50 a 95% \n"
            Description1 +=     "Zaleca się użycie couplingu DC. Inne ustawienia mogą spowodować artefakty w uzyskanym obrazie. \n"
            DescriptionLabel = QLabel(Description1)
            DescriptionLabel.setMaximumHeight(200)
            DescriptionLabel.setWordWrap(True)

            self.RunPanel = QHBoxLayout()
            self.ConnectButton = QPushButton("Connect")
            self.ConnectButton.clicked.connect(self.ConnectClicked)

            self.StartButton = QPushButton("Start")
            self.StartButton.clicked.connect(self.StreamingClicked)

            self.StopButton = QPushButton("Stop")
            self.StopButton.clicked.connect(self.StopStreamingClicked)

            self.RunPanel.addWidget(self.ConnectButton)
            self.RunPanel.addWidget(self.StartButton)
            self.RunPanel.addWidget(self.StopButton)

            CH_A_SettingsPanel = QHBoxLayout()
            CH_B_SettingsPanel = QHBoxLayout()
            CH_C_SettingsPanel = QHBoxLayout()
            CH_D_SettingsPanel = QHBoxLayout()
            self.UpdateButton = QPushButton('Load settings to device')
            self.UpdateButton.clicked.connect(self.UpdatePicoSettings)

            self.Panels = [CH_A_SettingsPanel,CH_B_SettingsPanel,CH_C_SettingsPanel,CH_D_SettingsPanel]
            self.IsActive = [True,True,True,True]
            self.HM_Channels = 4
            self.IsActive_CB = [QCheckBox("CH_A"),QCheckBox("CH_B"),QCheckBox("CH_C"),QCheckBox("CH_D")]

            
            self.Couplings = ['DC','DC','DC','DC']
            self.PossibleCouplings = ['AC','DC']
            self.Couplings_CB = [QComboBox(),QComboBox(),QComboBox(),QComboBox()]
            
            self.Ranges = [2000,10000,200,200]
            self.PossibleRanges = [20,50,100,200,500,1000,2000,5000,10000]
            self.Ranges_CB = [QComboBox(),QComboBox(),QComboBox(),QComboBox()]
            
            self.BitResolution = 14
            self.PowerMeter = [QProgressBar(),QProgressBar(),QProgressBar(),QProgressBar()]

            for i in range(4):
                self.IsActive_CB[i].setChecked(self.IsActive[i])
                self.Panels[i].addWidget(self.IsActive_CB[i])

                for k in range(len(self.PossibleRanges)):
                    self.Ranges_CB[i].addItem(str(self.PossibleRanges[k]) + ' mV')
                
                self.Ranges_CB[i].setCurrentIndex(self.Ranges_CB[i].findText(str(self.Ranges[i]) + ' mV'))
                self.Panels[i].addWidget(self.Ranges_CB[i])

                for k in range(len(self.PossibleCouplings)):
                    self.Couplings_CB[i].addItem(str(self.PossibleCouplings[k]))
                self.Couplings_CB[i].setCurrentIndex(self.Couplings_CB[i].findText(str(self.Couplings[i])))
                self.Panels[i].addWidget(self.Couplings_CB[i])

                self.PowerMeter[i].setGeometry(30,40,100,20)
                self.Panels[i].addWidget(self.PowerMeter[i])

            self.PolarisationCB = QCheckBox("Reverse Polarisation")
            self.PolarisationCB.setChecked(False)
            
            self.layout.addLayout(self.RunPanel,0,0)
            self.layout.addLayout(CH_A_SettingsPanel,1,0)
            self.layout.addLayout(CH_B_SettingsPanel,2,0)
            self.layout.addLayout(CH_C_SettingsPanel,3,0)
            self.layout.addLayout(CH_D_SettingsPanel,4,0)
            self.layout.addWidget(self.UpdateButton,5,0)
            self.layout.addWidget(self.PolarisationCB,6,0)
            
            self.layout.addWidget(DescriptionLabel,7,0)
        
            self.setLayout(self.layout) 
        def ConnectClicked(self):
            self.PICOdevice.OpenUnit(PICO_BIT_RES = 14)
        def StreamingClicked(self):
            """ Starts streaming proces in a new thread. \n
                Create Queue that will be populated with raw data from Picoscope. \n
                Data from queue can be taken by Queue.get() \n
                Returns tuple with both: Queue and thread """
            self.StreamingThread = mp.Process(target=self.PICOdevice.StartStreaming,args=([self.RawDataQ,[True,True,True,True],[True]]))
            self.StreamingThread.start()

            return self.StreamingThread
        def StopStreamingClicked(self):

            self.PICOdevice.Stop()
            while not self.RawDataQ.empty():
                self.RawDataQ.get_nowait()
            
            self.StreamingThread.join()
        def UpdatePicoSettings(self):

            for i in range(4):
                self.IsActive[i] = self.IsActive_CB[i].isChecked()
                self.Couplings[i] = self.Couplings_CB[i].currentText()
                self.Ranges[i] = int(self.Ranges_CB[i].currentText().split(' ')[0])
            print(self.IsActive)
            print(self.Couplings)
            print(self.Ranges)

            if self.IsActive[0]:
                self.HM_Channels = 1
            if self.IsActive[1]:
                self.HM_Channels = 2
            if self.IsActive[2]:
                self.HM_Channels = 3
            if self.IsActive[3]:
                self.HM_Channels = 4

            self.PICOdevice.setRangesAndCoupling( self.Ranges[0:self.HM_Channels],
                                            self.Couplings[0:self.HM_Channels],
                                            [True])
