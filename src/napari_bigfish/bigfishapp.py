from qtpy.QtCore import Signal, QObject
from bigfish import stack

class BigfishApp(QObject):

    sigmaSignal = Signal(float, float)
    thresholdSignal = Signal(float)

    def __init__(self):
        QObject.__init__(self)
        self.sigmaXY = 2.3
        self.sigmaZ = 0.75
        self.threshold = 15
        self.data = None
        self.result = None


    def getSigmaXY(self):
        return self.sigmaXY


    def setSigmaXY(self, sigmaXY):
        self.sigmaXY = sigmaXY
        sigmaSignal.emit(sigmaXY, self.getSigmaZ())


    def getSigmaZ(self):
        return self.sigmaZ


    def setSigmaZ(self, sigmaZ):
        self.sigmaZ = sigmaZ
        sigma.emit(self.getSigmaXY(), sigmaZ)


    def setData(self, data):
        self.data = data


    def getData(self):
        return self.data


    def getResult(self):
        return self.result


    def subtractBackground(self, sigma):
        self.result = stack.remove_background_gaussian(self.data, sigma)

    def getThreshold(self):
        return self.threshold

    def setThreshold(self, threshold):
        self.threshold = threshold
        thresholdSignal.emit(threshold)