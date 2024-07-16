
from PICOSCOPE.PICOsdk.ps5000a import ps5000a as ps
from PICOSCOPE.PICOsdk.functions import  assert_pico_ok
import ctypes
import numpy as np
import time

class PicoStream: # klasa obsługująca Picoscop
    
    def print(self,strng):            
            try:
                self.q_err.put(strng,timeout=0)
            except:
                print(strng)

    def PICO_callback(self,handle, noOfSamples, startIndex, overflow, triggerAt, triggered, autoStop, param):        
        
        timeout=2
        self.SendedData += noOfSamples
        sourceEnd = startIndex + noOfSamples
        A = self.PS_bufferAMax[startIndex:sourceEnd]
        B = self.PS_bufferBMax[startIndex:sourceEnd]
        C = self.PS_bufferCMax[startIndex:sourceEnd]
        D = self.PS_bufferDMax[startIndex:sourceEnd]
        A_0 = self.PS_buffer_0Max[startIndex:sourceEnd]

        if  self.q_rawdata.full():
            qsz=self.q_rawdata.qsize()
            for i in range(qsz//2):
                if not self.q_rawdata.empty():
                    self.q_rawdata.get_nowait()   
            self.print('Losing streaming data (from Picoscope)')
            self.PS_new=True
        self.nextSample += noOfSamples
        self.q_rawdata.put({'A':np.array(A,dtype=float)*self.Ranges[0]/8192,
                            'B':np.array(B,dtype=float)*self.Ranges[1]/8192,
                            'C':np.array(C,dtype=float)*self.Ranges[2]/8192,
                            'D':np.array(D,dtype=float)*self.Ranges[3]/8192,
                            'Analog_0':np.array(A_0,dtype=np.int16), #Uwaga tak naprawdę jest tu 8 kanałów zapisanych na 16 bitach
                            't':time.time(),
                            'Ranges': [self.Ranges[0],self.Ranges[1],self.Ranges[2],self.Ranges[3]]}
                            ,timeout=timeout)
        #print(f'min{np.min(A)}, max{np.max(A)}')
    def __init__(self):        
      
            self.chandle=ctypes.c_int16()
            self.ps = ps
            self.assert_pico_ok = assert_pico_ok
            self.dt_ns = 16*8
            self.TIME = (60000000)*60
            self.SendedData = 0
            self.PICO_ranges={10,20,50,100,200,500,1000,2000,5000,10000,20000}
            self.PICO_res={8,12,14,15,16}
    
    def Stop(self):
        self.PS_status_stop = self.ps.ps5000aStop(self.chandle)
        self.Measure = False
    def setRangesAndCoupling(self,CH_RANGEs,COUPLINGs,D_CHANELS = True):
        self.Ranges = CH_RANGEs
        self.Couplings = COUPLINGs
        if len(CH_RANGEs) > 0:
            channel_A_range = self.ps.PS5000A_RANGE[f'PS5000A_{CH_RANGEs[0]}MV' if CH_RANGEs[0]<1000 else f'PS5000A_{CH_RANGEs[0]//1000}V']
        if len(CH_RANGEs) > 1:
            channel_B_range = self.ps.PS5000A_RANGE[f'PS5000A_{CH_RANGEs[1]}MV' if CH_RANGEs[1]<1000 else f'PS5000A_{CH_RANGEs[1]//1000}V']
        if len(CH_RANGEs) > 2:
            channel_C_range = self.ps.PS5000A_RANGE[f'PS5000A_{CH_RANGEs[2]}MV' if CH_RANGEs[2]<1000 else f'PS5000A_{CH_RANGEs[2]//1000}V']
        if len(CH_RANGEs) > 3:
            channel_D_range = self.ps.PS5000A_RANGE[f'PS5000A_{CH_RANGEs[3]}MV' if CH_RANGEs[3]<1000 else f'PS5000A_{CH_RANGEs[3]//1000}V']
        MissingCouplings = len(CH_RANGEs) - len(COUPLINGs)
        for i in range(MissingCouplings):
            COUPLINGs.append('AC')
        if len(CH_RANGEs) > 0:
            self.PS_status_setChA = self.ps.ps5000aSetChannel(self.chandle,
                                    self.ps.PS5000A_CHANNEL['PS5000A_CHANNEL_A'],
                                    1,#enabled
                                    self.ps.PS5000A_COUPLING['PS5000A_AC' if COUPLINGs[0] == "AC" else 'PS5000A_DC'],
                                    channel_A_range,
                                    0.0)#offset        
            self.assert_pico_ok(self.PS_status_setChA)  
        if len(CH_RANGEs) > 1:
            self.PS_status_setChB = self.ps.ps5000aSetChannel(self.chandle,
                                    self.ps.PS5000A_CHANNEL['PS5000A_CHANNEL_B'],
                                    1,
                                    self.ps.PS5000A_COUPLING['PS5000A_AC' if COUPLINGs[1] == "AC" else 'PS5000A_DC'],
                                    channel_B_range,
                                    0.0)
            self.assert_pico_ok(self.PS_status_setChB)
        if len(CH_RANGEs) > 2:
            self.PS_status_setChC = self.ps.ps5000aSetChannel(self.chandle,
                                    self.ps.PS5000A_CHANNEL['PS5000A_CHANNEL_C'],
                                    1,
                                    self.ps.PS5000A_COUPLING['PS5000A_AC' if COUPLINGs[2] == "AC" else 'PS5000A_DC'],
                                    channel_C_range,
                                    0.0)
            self.assert_pico_ok(self.PS_status_setChB)
        if len(CH_RANGEs) > 3:
            self.PS_status_setChD = self.ps.ps5000aSetChannel(self.chandle,
                                    self.ps.PS5000A_CHANNEL['PS5000A_CHANNEL_D'],
                                    1,
                                    self.ps.PS5000A_COUPLING['PS5000A_AC' if COUPLINGs[3] == "AC" else 'PS5000A_DC'],
                                    channel_D_range,
                                    0.0)
            self.assert_pico_ok(self.PS_status_setChB)
        if D_CHANELS[0]:
            self.PS_status_setDataBuffers0 = self.ps.ps5000aSetDigitalPort(self.chandle,
                                            self.ps.PS5000A_CHANNEL['PS5000A_DIGITAL_PORT0'],
                                            1,
                                            7000)

    def OpenUnit(self,PICO_BIT_RES = 14):
                    
        if PICO_BIT_RES not in {8,12,14,15,16}:
            PICO_BIT_RES=15
        resolution = self.ps.PS5000A_DEVICE_RESOLUTION[f'PS5000A_DR_{PICO_BIT_RES}BIT']
        self.PS_status_openunit = self.ps.ps5000aOpenUnit(ctypes.byref(self.chandle), None, resolution)
        
        try:
            self.assert_pico_ok(self.PS_status_openunit)
        
        except: # PicoNotOkError:        
            powerStatus = self.PS_status_openunit        
            if powerStatus == 286:
                self.PS_status_changePowerSource = self.ps.ps5000aChangePowerSource(self.chandle, powerStatus)
            elif powerStatus == 282:
                self.PS_status_changePowerSource = self.ps.ps5000aChangePowerSource(self.chandle, powerStatus)
            else:
                raise        

            self.assert_pico_ok(self.PS_status_changePowerSource)

        return
    def StartStreaming(self,DATA_QUEUE, A_CHANELS = [True, True, True, True],D_CHANELS = [True]):

        self.PS_sizeOfOneBuffer = int(5000000)
        self.PS_bufferAMax= np.zeros(shape=self.PS_sizeOfOneBuffer, dtype=np.int16)
        self.PS_bufferBMax = np.zeros(shape=self.PS_sizeOfOneBuffer, dtype=np.int16)
        self.PS_bufferCMax= np.zeros(shape=self.PS_sizeOfOneBuffer, dtype=np.int16)
        self.PS_bufferDMax = np.zeros(shape=self.PS_sizeOfOneBuffer, dtype=np.int16)
        self.PS_buffer_0Max = np.zeros(shape=self.PS_sizeOfOneBuffer, dtype=np.int16)


        if A_CHANELS[0]:
            self.PS_status_setDataBuffersA = self.ps.ps5000aSetDataBuffers(self.chandle,
                                            self.ps.PS5000A_CHANNEL['PS5000A_CHANNEL_A'],
                                            self.PS_bufferAMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                            None,
                                            self.PS_sizeOfOneBuffer,
                                            0,#memory_segment 
                                            self.ps.PS5000A_RATIO_MODE['PS5000A_RATIO_MODE_NONE'])
            self.assert_pico_ok(self.PS_status_setDataBuffersA)
            
        if A_CHANELS[1]:
            self.PS_status_setDataBuffersB = self.ps.ps5000aSetDataBuffers(self.chandle,
                                            self.ps.PS5000A_CHANNEL['PS5000A_CHANNEL_B'],
                                            self.PS_bufferBMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                            None,
                                            self.PS_sizeOfOneBuffer,
                                            0,
                                            self.ps.PS5000A_RATIO_MODE['PS5000A_RATIO_MODE_NONE'])
            self.assert_pico_ok(self.PS_status_setDataBuffersB)

        if A_CHANELS[2]:
            self.PS_status_setDataBuffersC = self.ps.ps5000aSetDataBuffers(self.chandle,
                                            self.ps.PS5000A_CHANNEL['PS5000A_CHANNEL_C'],
                                            self.PS_bufferCMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                            None,
                                            self.PS_sizeOfOneBuffer,
                                            0,
                                            self.ps.PS5000A_RATIO_MODE['PS5000A_RATIO_MODE_NONE'])
            self.assert_pico_ok(self.PS_status_setDataBuffersB)
        if A_CHANELS[3]:
            self.PS_status_setDataBuffersD = self.ps.ps5000aSetDataBuffers(self.chandle,
                                            self.ps.PS5000A_CHANNEL['PS5000A_CHANNEL_D'],
                                            self.PS_bufferDMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                            None,
                                            self.PS_sizeOfOneBuffer,
                                            0,
                                            self.ps.PS5000A_RATIO_MODE['PS5000A_RATIO_MODE_NONE'])
            self.assert_pico_ok(self.PS_status_setDataBuffersC)
        
        if D_CHANELS[0]:
            self.PS_status_setDataBuffers_0 = self.ps.ps5000aSetDataBuffers(self.chandle,
                                            self.ps.PS5000A_CHANNEL['PS5000A_DIGITAL_PORT0'],
                                            self.PS_buffer_0Max.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                            None,
                                            self.PS_sizeOfOneBuffer,
                                            0,
                                            self.ps.PS5000A_RATIO_MODE['PS5000A_RATIO_MODE_NONE'])
            self.assert_pico_ok(self.PS_status_setDataBuffersC)
        

        self.q_rawdata= DATA_QUEUE
        totalSamples =self.TIME
        
        sampleInterval = ctypes.c_int32(self.dt_ns)
        sampleUnits = self.ps.PS5000A_TIME_UNITS['PS5000A_NS']
        self.PS_status_runStreaming = self.ps.ps5000aRunStreaming(self.chandle,
                                                        ctypes.byref(sampleInterval),
                                                        sampleUnits,
                                                        0,#maxPreTriggerSamples
                                                        totalSamples,
                                                        0,#autoStopOn
                                                        1,#downsampleRatio
                                                        self.ps.PS5000A_RATIO_MODE['PS5000A_RATIO_MODE_NONE'],
                                                        self.PS_sizeOfOneBuffer )
        self.assert_pico_ok(self.PS_status_runStreaming)
        actualSampleInterval = sampleInterval.value
        actualSampleIntervalNs = actualSampleInterval         
        self.print("Capturing at sample interval %s ns" % actualSampleIntervalNs)        
        self.nextSample = 0
        self.autoStopOuter = False
        self.PS_new=True
        self.maxADC = ctypes.c_int16()
        self.PS_status_maximumValue = self.ps.ps5000aMaximumValue(self.chandle, ctypes.byref(self.maxADC))
        cFuncPtr = self.ps.StreamingReadyType(self.PICO_callback)

        self.Measure = True
        while self.Measure and( self.TIME > self.SendedData):       
            self.wasCalledBack = False
            self.PS_status_getStreamingLastestValues = self.ps.ps5000aGetStreamingLatestValues(self.chandle, cFuncPtr, None)
            time.sleep(0.05)
        self.SendedData = 0
