from qtpy.QtCore import Signal
from qtpy.QtCore import QObject
from bigfish import stack, detection

class BigfishApp(QObject):

    sigmaSignal = Signal(float, float)
    thresholdSignal = Signal(float)
    radiusSignal = Signal(float, float)
    removeDuplicatesSignal = Signal(bool)
    findThresholdSignal = Signal(bool)


    def __init__(self):
        super(BigfishApp, self).__init__()
        self.sigmaXY = 2.3
        self.sigmaZ = 0.75
        self.threshold = 15
        self.radiusXY = 340
        self.radiusZ = 2500
        self.removeDuplicates = True
        self.findThreshold = True
        self.data = None
        self.spots = None
        self.result = None


    def getSigmaXY(self):
        return self.sigmaXY


    def setSigmaXY(self, sigmaXY):
        self.sigmaXY = sigmaXY
        self.sigmaSignal.emit(sigmaXY, self.getSigmaZ())


    def getSigmaZ(self):
        return self.sigmaZ


    def setSigmaZ(self, sigmaZ):
        self.sigmaZ = sigmaZ
        self.sigmaSignal.emit(self.getSigmaXY(), sigmaZ)


    def getRadiusXY(self):
        return self.radiusXY


    def setRadiusXY(self, radius):
        self.radiusXY = radius
        self.radiusSignal.emit(radius, self.getRadiusZ())


    def getRadiusZ(self):
        return self.radiusZ


    def setRadiusZ(self, radius):
        self.radiusZ = radius
        self.radiusSignal.emit(self.getRadiusXY(), radius)


    def setData(self, data):
        self.data = data


    def getData(self):
        return self.data


    def getResult(self):
        return self.result


    def subtractBackground(self, sigma):
        self.result = stack.remove_background_gaussian(self.data, sigma)


    def detectSpots(self, scale):
        radiusXY = self.getRadiusXY()
        if self.findThreshold:
            self.spots, threshold = detection.detect_spots(
                self.data,
                remove_duplicate = self.shallRemoveDuplicates(),
                return_threshold = self.shallFindThreshold(),
                voxel_size = scale,
                spot_radius = (self.getRadiusZ(), radiusXY , radiusXY))
            self.setThreshold(threshold)
        else:
            self.spots = detection.detect_spots(
                self.data,
                remove_duplicate = self.shallRemoveDuplicates(),
                return_threshold = self.shallFindThreshold(),
                voxel_size = scale,
                spot_radius = (self.getRadiusZ(), radiusXY , radiusXY))


    def getSpots(self):
        return self.spots


    def getThreshold(self):
        return self.threshold


    def setThreshold(self, threshold):
        self.threshold = threshold
        self.thresholdSignal.emit(threshold)


    def shallRemoveDuplicates(self):
        return self.removeDuplicates


    def activateRemoveDuplicates(self):
        self.removeDuplicates = True
        self.removeDuplicatesSignal.emit(True)


    def deactivateRemoveDuplicates(self):
        self.removeDuplicates = False
        self.removeDuplicatesSignal.emit(False)


    def shallFindThreshold(self):
        return self.findThreshold


    def activateFindThreshold(self):
        self.findThreshold = True
        self.findThresholdSignal.emit(True)


    def deactivateRemoveDuplicates(self):
        self.findThreshold = False
        self.findThresholdSignal.emit(False)