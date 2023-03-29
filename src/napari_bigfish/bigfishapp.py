from pathlib import Path
import os
from enum import Enum
from datetime import datetime
from skimage import io
from collections import Counter
from qtpy.QtCore import Signal
from qtpy.QtCore import QObject
from bigfish import stack, detection
import numpy as np


class BigfishApp(QObject):
    """
    Application model for the napari FISH-spot detection widget, that runs
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
        """The constructor creates a bigfish app with default parameters.
        """
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
        """Run the processing in batch-mode on the input images.

        :param scale: A tupel with the scales (voxel-sizes) of the images in nm
                      for the z, y and x dimensions
        :type scale: 3-tupel of floats
        :param inputImages: A list of paths to the input images
        :param cellLabels: An optional list of paths to the cell label images
        :param nucleiMasks: An optional list of paths to the nuclei mask images
        :param subtractBackground: A boolean telling wether to subtract the background
                             before the analysis
        :param decomposeDenseRegion: A boolean telling wether to decompose dense
                                     regions for the spot detection
        """
        self.setProgressMax(len(inputImages))
        if len(inputImages)<1:
            return
        outputImagePath = self.createEmptySpotCountReport(inputImages[0])
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
            nucleiMasksData = None
            if nucleiMasks:
                nucleiMasksData = io.imread(nucleiMasks[index])
            self.countSpotsPerCellAndEnvironment(cellLabelData, nucleiMasksData)
            self.reportSpotCounts(inputImagePath, outputImagePath)
            self.setProgress(index+1)


    def setProgressMax(self, max):
        """Set the max. progress and send the progressSignal with the current
        and the max. progress.
        """
        self.progressMax = max
        self.progress = 0
        self.progressSignal.emit(self.progress, self.progressMax)


    def setProgress(self, progress):
        """Set the current progress and send the progressSignal with the current
        and the max. progress.
        """
        self.progress = progress
        self.progressSignal.emit(self.progress, self.progressMax)


    def reportSpots(self, inputPath):
        """Write a csv-file with the coordinates of the detected spots. The
        file can be opened by napari as a points-layer.

        :param inputPath: The past to the input images; the file will be written
        into a subdirectory "spots" of that directory.
        """
        path = Path(inputPath)
        inFolder, filename = os.path.split(path)
        outname, _ = os.path.splitext(filename)
        outname = outname + ".csv"
        inFolder = path.parent
        outFolder = os.path.join(inFolder, "spots")
        if not os.path.exists(outFolder):
            os.makedirs(outFolder)
        outPath = os.path.join(outFolder, outname)
        with open(outPath, 'w') as f:
            line = "index,axis-0,axis-1,axis-2"
            f.write(line)
            f.write('\n')
            for index, spot in enumerate(self.spots, start=1):
                line = str(index) + "," + ",".join([str(coord) for coord in spot])
                f.write(line)
                f.write('\n')


    def reportSpotCounts(self, inputPath, outputPath):
        """Write a csv-file with the spot-counts.

        :param inputPath: The path of the input image will be reported in the
                          csv-file
        :param outputPath: The directory into which the csv-file will be written
        """
        table = self.getSpotCountPerCellAndEnvironment()
        with open(outputPath, "a") as f:
            for line in table:
                csvLine = inputPath + "," + ",".join(str(value) for value in line)
                f.write(csvLine)
                f.write('\n')


    def createEmptySpotCountReport(self, inputPath):
        """Create a csv-file, containing only the column headings,
        for the spot-count-report and return the path to the file. The file
        is written into a subfolder ``results`` of the input folder.

        :param inputPath: The path to an input image
        """
        path = Path(inputPath)
        inFolder, filename = os.path.split(path)
        parent, folder = os.path.split(inFolder)
        ts = str(datetime.now())
        outname = ts + "_" + folder + "_count.csv"
        inFolder = path.parent
        outFolder = os.path.join(inFolder, "results")
        if not os.path.exists(outFolder):
            os.makedirs(outFolder)
        outPath = os.path.join(outFolder, outname)
        if not os.path.exists(outPath):
            with open(outPath, "a") as f:
                headings = "image,cell,spots in cytoplasm,spots in nucleus,spots in cell"
                f.write(headings)
                f.write('\n')
        return outPath


    def getSpotRadius(self):
        """Return the spot radius in the z, y and x-dimension
        :rtype: 2 or 3-tupel of float
        """
        spotRadius = (self.getRadiusXY(), self.getRadiusXY())
        if self.data.ndim > 2:
            spotRadius = (self.getRadiusZ(), self.getRadiusXY(),
                          self.getRadiusXY())
        return spotRadius


    def getScale(self, scale):
        """Answer the scale (voxel-size) in nm in the different dimensions
        :rtype: 2 or 3-tupel of float
        """
        if self.data.ndim == 3 or len(scale) == self.data.ndim:
            return scale
        return (scale[1], scale[2])


    def getDecomposeSpotRadius(self):
        """Answer the spot radius for the decomposition of dense regions.
        :rtype: 2 or 3-tupel of float
        """
        decomposeSpotRadius = (self.getDecomposeRadiusXY(),
                               self.getDecomposeRadiusXY())
        if self.data.ndim > 2:
            decomposeSpotRadius = (self.getDecomposeRadiusZ(),
                                   self.getDecomposeRadiusXY(),
                                   self.getDecomposeRadiusXY())
        return decomposeSpotRadius


    def subtractBackground(self):
        """Apply the gaussian background removal to the data of the application.
        The resulting image is stored in the result-attribute.
        """
        sigma = (self.getSigmaXY(), self.getSigmaXY())
        if self.data.ndim > 2:
            sigma = (self.getSigmaZ(), self.getSigmaXY(), self.getSigmaXY())
        self.result = stack.remove_background_gaussian(self.data, sigma)


    def detectSpots(self, scale):
        """Run the spot detection step with or without automatic threshold
        detection.

        :param scale: The scale (voxel size) of the image in the z, y and x
                      dimensions in nm.
        :type scale: 2 or 3-tupel of float
        """
        if self.findThreshold:
            self.spots, threshold = detection.detect_spots(
                self.data,
                remove_duplicate = self.shallRemoveDuplicates(),
                return_threshold = self.shallFindThreshold(),
                voxel_size = self.getScale(scale),
                spot_radius = self.getSpotRadius())
            self.setThreshold(threshold)
        else:
            self.spots = detection.detect_spots(
                self.data,
                threshold = self.getThreshold(),
                remove_duplicate = self.shallRemoveDuplicates(),
                return_threshold = self.shallFindThreshold(),
                voxel_size = self.getScale(scale),
                spot_radius = self.getSpotRadius())


    def decomposeDenseRegions(self, scale):
        """Run the decomposition of the dense regions.

        :param scale: The scale (voxel size) of the image in the z, y and x
                      dimensions in nm.
        :type scale: 2 or 3-tupel of float
        """
        self.spots, denseRegions, referenceSpot = detection.decompose_dense(
            self.data,
            self.spots,
            self.getScale(scale),
            self.getDecomposeSpotRadius(),
            alpha = self.alpha,
            beta = self.beta,
            gamma = self.gamma)


    def countSpotsPerCellAndEnvironment(self, cytoplasmLabels, nucleiLabels):
        """Counts the number of spots in the image and stores it in the
        attribute nrOfCells. Creates the cellLabelOfSpot list, that contains
        the cell-label for each spot and the nucleiLabelOfSpot list, that
        contains True for all spots that are within a nucleus.

        :param cytoplasmLabels: The cell-labels
        :type cytoplasmLabels: numpy.ndarray
        :param nucleiLabels: The nuclei-mask or labels
        :type nucleiLabels: numpy.ndarray
        """
        self.cellLabelOfSpot = []
        self.nucleiLabelOfSpot = []
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
        """Returns a table containing the spot-count for each cell, with the
        number of cells within the nucleus, outside of the nucleus and the total
        number.

        :rtype: list of lists
        """
        table = [0] * self.nrOfCells
        cellLabelAndNucleusFlag = zip(self.cellLabelOfSpot, self.nucleiLabelOfSpot)
        counter = Counter(cellLabelAndNucleusFlag)
        for cell in range(0, self.nrOfCells):
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


    def deactivateFindThreshold(self):
        self.findThreshold = False
        self.findThresholdSignal.emit(False)