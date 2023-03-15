from enum import Enum
from skimage import io
from collections import Counter
from qtpy.QtCore import Signal
from qtpy.QtCore import QObject
from bigfish import stack, detection
import numpy as np


class BigfishApp(QObject):
    """
    Application model for the napari FISH-spot detection widget that runs
    the bigfish gaussian background correction and spot detection.
    """

    sigmaSignal = Signal(float, float)
    thresholdSignal = Signal(float)
    radiusSignal = Signal(float, float)
    removeDuplicatesSignal = Signal(bool)
    findThresholdSignal = Signal(bool)
    decomposeRadiusSignal = Signal(float, float)
    alphaSignal = Signal(float)
    betaSignal = Signal(float)
    gammaSignal = Signal(float)
    progressSignal = Signal(int, int)

    def __init__(self):
        super(BigfishApp, self).__init__()
        self.sigmaXY = 2.3
        self.sigmaZ = 0.75
        self.threshold = 15
        self.radiusXY = 170
        self.radiusZ = 1250
        self.decomposeRadiusXY = 170
        self.decomposeRadiusZ = 1250
        self.alpha = 0.5
        self.beta = 1
        self.gamma = 5
        self.removeDuplicates = True
        self.findThreshold = True
        self.data = None
        self.spots = None
        self.result = None
        self.cellLabelOfSpot = None
        self.nucleiLabelOfSpot = None
        self.nrOfCells = 0
        self.progressMax = 0
        self.progress = 0


    def runBatch(self, scale, inputImages, cellLabels=None, nucleiMasks=None,
                       subtractBackground=False, decomposeDenseRegions=False):
        self.setProgressMax = len(inputImages)
        for index, inputImagePath in enumerate(inputImages):
            self.data = io.imread(inputImagePath)
            if subtractBackground:
                self.subtractBackground()
                self.data = self.getResult()
            self.detectSpots(scale)
            if decomposeDenseRegions:
                self.decomposeDenseRegions(scale)
            self.reportSpots(inputImagePath)
            cellLabelData = None
            if cellLabels:
                cellLabelData = io.imread(cellLabels[index])
            nucleiLabelData = None
            if nucleiMasks:
                nucleiMasksData = io.imread(nucleiMasks[index])
            self.countSpotsPerCellAndEnvironment(cellLabelData, nucleiMasksData)
            self.reportSpotCounts(inputImagePath)
            self.setProgress(index+1)


    def setProgressMax(self, max):
        self.progressMax = max
        self.progress = 0
        self.progressSignal.emit(self.progress, self.progressMax)


    def setProgress(self, progress):
        self.progress = progress
        self.progressSignal.emit(self.progress, self.progressMax)


    def reportSpots(self, inputPath):
        pass


    def reportSpotCounts(self, inputPath):
        pass


    def getSpotRadius(self):
        spotRadius = (self.getRadiusXY(), self.getRadiusXY())
        if self.data.ndim > 2:
            spotRadius = (self.getRadiusZ(), self.getRadiusXY(),
                          self.getRadiusXY())
        return spotRadius


    def getDecomposeSpotRadius(self):
        decomposeSpotRadius = (self.getDecomposeRadiusXY(),
                               self.getDecomposeRadiusXY())
        if self.data.ndim > 2:
            decomposeSpotRadius = (self.getDecomposeRadiusZ(),
                                   self.getDecomposeRadiusXY(),
                                   self.getDecomposeRadiusXY())
        return decomposeSpotRadius


    def subtractBackground(self):
        sigma = (self.getSigmaXY(), self.getSigmaXY())
        if self.data.ndim > 2:
            sigma = (self.getSigmaZ(), self.getSigmaXY(), self.getSigmaXY())
        self.result = stack.remove_background_gaussian(self.data, sigma)


    def detectSpots(self, scale):
        if self.findThreshold:
            self.spots, threshold = detection.detect_spots(
                self.data,
                remove_duplicate = self.shallRemoveDuplicates(),
                return_threshold = self.shallFindThreshold(),
                voxel_size = scale,
                spot_radius = self.getSpotRadius())
            self.setThreshold(threshold)
        else:
            self.spots = detection.detect_spots(
                self.data,
                threshold = self.getThreshold(),
                remove_duplicate = self.shallRemoveDuplicates(),
                return_threshold = self.shallFindThreshold(),
                voxel_size = scale,
                spot_radius = self.getSpotRadius())


    def decomposeDenseRegions(self, scale):
        self.spots, denseRegions, referenceSpot = detection.decompose_dense(
            self.data,
            self.spots,
            scale,
            self.getDecomposeSpotRadius(),
            alpha = self.alpha,
            beta = self.beta,
            gamma = self.gamma)


    def countSpotsPerCellAndEnvironment(self, cytoplasmLabels, nucleiLabels):
        if self.spots is None:
            return False
        self.nrOfCells = len(np.unique(cytoplasmLabels))
        self.cellLabelOfSpot = [0]*len(self.spots)
        self.nucleiLabelOfSpot = [0]*len(self.spots)
        for index, coords in enumerate(self.spots):
            if not cytoplasmLabels is None:
                self.cellLabelOfSpot[index] = cytoplasmLabels[tuple(coords)]
            if not nucleiLabels is None:
                self.nucleiLabelOfSpot[index] = (nucleiLabels[tuple(coords)]>0)
        return True


    def getSpotCountPerCellAndEnvironment(self):
        table = [0] * self.nrOfCells
        cellLabelAndNucleusFlag = zip(self.cellLabelOfSpot, self.nucleiLabelOfSpot)
        counter = Counter(cellLabelAndNucleusFlag)
        line0 = [0, 0, 0, counter[0, False]]
        table[0] = line0
        for cell in range(1, self.nrOfCells):
            notInNucleus = 0
            inNucleus = 0
            if (cell, False) in counter.keys():
                notInNucleus = counter[(cell, False)]
            if (cell, True) in counter.keys():
                inNucleus = counter[(cell, True)]
            line = [cell, notInNucleus, inNucleus, notInNucleus + inNucleus]
            table[cell] = line
        return table


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


    def getDecomposeRadiusXY(self):
        return self.decomposeRadiusXY


    def setDecomposeRadiusXY(self, radius):
        self.decomposeRadiusXY = radius
        self.decomposeRadiusSignal.emit(radius, self.decomposeRadiusZ)


    def getDecomposeRadiusZ(self):
        return self.decomposeRadiusZ


    def setDecomposeRadiusZ(self, radius):
        self.decomposeRadiusZ = radius
        self.decomposeRadiusSignal.emit(self.decomposeRadiusXY, radius)


    def getAlpha(self):
        return self.alpha


    def setAlpha(self, alpha):
        self.alpha = alpha
        self.alphaSignal.emit(alpha)


    def getBeta(self):
        return self.beta


    def setBeta(self, beta):
        self.beta = beta
        self.betaSignal.emit(beta)


    def getGamma(self):
        return self.gamma


    def setGamma(self, gamma):
        self.gamma = gamma
        self.gammaSignal.emit(gamma)


    def setData(self, data):
        self.data = data


    def getData(self):
        return self.data


    def getResult(self):
        return self.result


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