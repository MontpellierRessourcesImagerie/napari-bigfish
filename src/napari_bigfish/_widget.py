"""
A Widget to run the bigfish FISH-spot detection
"""
import time
import numpy as np
from typing import TYPE_CHECKING
from magicgui import magic_factory
from qtpy.QtWidgets import QVBoxLayout, QFormLayout
from qtpy.QtWidgets import QPushButton, QWidget, QLabel, QCheckBox, QGroupBox
from qtpy.QtCore import Slot
from napari.qt.threading import thread_worker
from napari.qt.threading import create_worker
from napari.utils import notifications
from napari.utils import progress
from napari.utils.events import Event
from napari_bigfish.bigfishapp import BigfishApp
from napari_bigfish.qtutil import WidgetTool, TableView
from napari_bigfish.napari_util import NapariUtil

if TYPE_CHECKING:
    import napari



class DetectFISHSpotsWidget(QWidget):


    def __init__(self, napari_viewer):
        super().__init__()
        self.setModel(BigfishApp())
        self.viewer = napari_viewer
        self.napariUtil = NapariUtil(self.viewer)
        self.fieldWidth = 50
        self.maxButtonWidth = 200
        self.spotDisplaySize = 5
        self.setLayout(QVBoxLayout())
        self.addSubtractBackgroundWidget()
        self.layout().addSpacing(20)
        self.addDetectSpotsWidget()
        self.layout().addSpacing(20)
        self.addDecomposeDenseRegionsWidget()
        self.layout().addSpacing(20)
        self.addCountSpotsWidget()
        self.viewer.layers.events.inserted.connect(self.onLayerAddedOrRemoved)
        self.viewer.layers.events.removed.connect(self.onLayerAddedOrRemoved)


    def addSubtractBackgroundWidget(self):
        groupBox = QGroupBox("Background Subtraction")
        formLayout = QFormLayout()
        sigmaXYLabel, self.sigmaXYInput = \
         WidgetTool.getLineInput(self, "sigma xy: ", self.model.getSigmaXY(),
                                 self.fieldWidth, self.updateSigmaXY)
        sigmaZLabel, self.sigmaZInput = \
         WidgetTool.getLineInput(self, "sigma z: ",self.model.getSigmaZ(),
                                 self.fieldWidth, self.updateSigmaZ)
        subtractBackgroundButton = QPushButton("Subtract Background")
        subtractBackgroundButton.setMaximumWidth(self.maxButtonWidth)
        subtractBackgroundButton.clicked.connect(self.onClickSubtractBackground)
        formLayout.addRow(sigmaXYLabel, self.sigmaXYInput)
        formLayout.addRow(sigmaZLabel, self.sigmaZInput)
        verticalLayout = QVBoxLayout()
        verticalLayout.addLayout(formLayout)
        verticalLayout.addWidget(subtractBackgroundButton)
        groupBox.setLayout(verticalLayout)
        self.layout().addWidget(groupBox)


    def addDetectSpotsWidget(self):
        groupBox = QGroupBox("Spot Detection")
        formLayout = QFormLayout()
        thresholdLabel, self.thresholdInput = \
         WidgetTool.getLineInput(self, "threshold: ",self.model.getThreshold(),
                                 self.fieldWidth, self.updateThreshold)
        radiusXYLabel, self.radiusXYInput = \
         WidgetTool.getLineInput(self, "spot radius xy: ",self.model.getRadiusXY(),
                                 self.fieldWidth, self.updateRadiusXY)
        radiusZLabel, self.radiusZInput = \
         WidgetTool.getLineInput(self, "spot radius z: ",self.model.getRadiusZ(),
                                 self.fieldWidth, self.updateRadiusZ)
        self.removeDuplicatesCheckbox = QCheckBox("remove duplicates")
        self.removeDuplicatesCheckbox.setChecked(self.model.shallRemoveDuplicates())
        self.removeDuplicatesCheckbox.stateChanged.connect(self.onRemoveDuplicatesChanged)
        self.findThresholdCheckbox = QCheckBox("find threshold")
        self.findThresholdCheckbox.setChecked(self.model.shallFindThreshold())
        self.findThresholdCheckbox.stateChanged.connect(self.onFindThresholdChanged)
        detectSpotsButton = QPushButton("Detect Spots")
        detectSpotsButton.setMaximumWidth(self.maxButtonWidth)
        detectSpotsButton.clicked.connect(self.onClickDetectSpots)
        formLayout.addRow(thresholdLabel, self.thresholdInput)
        formLayout.addRow(radiusXYLabel, self.radiusXYInput)
        formLayout.addRow(radiusZLabel, self.radiusZInput)
        verticalLayout = QVBoxLayout()
        verticalLayout.addLayout(formLayout)
        verticalLayout.addWidget(self.removeDuplicatesCheckbox)
        verticalLayout.addWidget(self.findThresholdCheckbox)
        verticalLayout.addWidget(detectSpotsButton)
        groupBox.setLayout(verticalLayout)
        self.layout().addWidget(groupBox)


    def addDecomposeDenseRegionsWidget(self):
        groupBox = QGroupBox("Decompose Dense Regions")
        formLayout = QFormLayout()
        spotLayers = self.napariUtil.getPointsLayers()
        spotsLabel, self.decomposeSpotsCombo = WidgetTool.getComboInput(self,
                                            "spots: ",
                                            spotLayers)
        radiusXYLabel, self.decomposeRadiusXYInput = \
         WidgetTool.getLineInput(self, "spot radius xy: ",self.model.getDecomposeRadiusXY(),
                                 self.fieldWidth, self.updateDecomposeRadiusXY)
        radiusZLabel, self.decomposeRadiusZInput = \
         WidgetTool.getLineInput(self, "spot radius z: ",self.model.getDecomposeRadiusZ(),
                                 self.fieldWidth, self.updateDecomposeRadiusZ)
        alphaLabel, self.alphaInput = \
         WidgetTool.getLineInput(self, "alpha: ",self.model.getAlpha(),
                                 self.fieldWidth, self.updateAlpha)
        betaLabel, self.betaInput = \
         WidgetTool.getLineInput(self, "beta: ",self.model.getBeta(),
                                 self.fieldWidth, self.updateBeta)
        gammaLabel, self.gammaInput = \
         WidgetTool.getLineInput(self, "gamma: ",self.model.getGamma(),
                                 self.fieldWidth, self.updateGamma)
        decomposeSpotsButton = QPushButton("Decompose Dense Regions")
        decomposeSpotsButton.setMaximumWidth(self.maxButtonWidth)
        decomposeSpotsButton.clicked.connect(self.onClickDecomposeDenseRegions)
        formLayout.addRow(spotsLabel, self.decomposeSpotsCombo)
        formLayout.addRow(radiusXYLabel, self.decomposeRadiusXYInput)
        formLayout.addRow(radiusZLabel, self.decomposeRadiusZInput)
        formLayout.addRow(alphaLabel, self.alphaInput)
        formLayout.addRow(betaLabel, self.betaInput)
        formLayout.addRow(gammaLabel, self.gammaInput)
        verticalLayout = QVBoxLayout()
        verticalLayout.addLayout(formLayout)
        verticalLayout.addWidget(decomposeSpotsButton)
        groupBox.setLayout(verticalLayout)
        self.layout().addWidget(groupBox)


    def addCountSpotsWidget(self):
        groupBox = QGroupBox("Spot Counting")
        formLayout = QVBoxLayout()
        spotLayers = self.napariUtil.getPointsLayers()
        spotsLabel, self.spotsCombo = WidgetTool.getComboInput(self,
                                            "spots: ",
                                            spotLayers)
        labelLayers = self.napariUtil.getLabelLayers()
        cytoLabel, self.cytoCombo = WidgetTool.getComboInput(self,
                                            "cytoplasm labels: ",
                                            labelLayers)
        nucleiLabel, self.nucleiCombo = WidgetTool.getComboInput(self,
                                            "nuclei labels or mask: ",
                                            labelLayers)
        countSpotsButton = QPushButton("Count Spots")
        countSpotsButton.setMaximumWidth(self.maxButtonWidth)
        countSpotsButton.clicked.connect(self.onClickCountSpots)
        formLayout.addWidget(spotsLabel)
        formLayout.addWidget(self.spotsCombo)
        formLayout.addWidget(cytoLabel)
        formLayout.addWidget(self.cytoCombo)
        formLayout.addWidget(nucleiLabel)
        formLayout.addWidget(self.nucleiCombo)
        verticalLayout = QVBoxLayout()
        verticalLayout.addLayout(formLayout)
        verticalLayout.addWidget(countSpotsButton)
        groupBox.setLayout(verticalLayout)
        self.layout().addWidget(groupBox)


    def setModel(self, aModel):
        self.model = aModel
        self.model.sigmaSignal.connect(self.sigmaChanged)
        self.model.thresholdSignal.connect(self.thresholdChanged)
        self.model.radiusSignal.connect(self.radiusChanged)
        self.model.removeDuplicatesSignal.connect(self.removeDuplicatesChanged)
        self.model.findThresholdSignal.connect(self.findThresholdChanged)


    def onClickCountSpots(self):
        headings = ["image", "cell", "spots in cytoplasm", "spots in nucleus",
                    "spots in cell"]
        cytoLabelsName = self.cytoCombo.currentText()
        nucleiMaskName = self.nucleiCombo.currentText()
        spotsName = self.spotsCombo.currentText()
        if cytoLabelsName and nucleiMaskName:
            cytoLabels = self.napariUtil.getDataOfLayerWithName(cytoLabelsName)
            nucleiMask = self.napariUtil.getDataOfLayerWithName(nucleiMaskName)
            spots = self.napariUtil.getDataOfLayerWithName(spotsName)
            self.model.spots = spots
            self.spotsName = spotsName
            countSpotsThread = CountSpotsThread(self.model, self, spots, spotsName,
                                                cytoLabels, nucleiMask,
                                                headings)
            progressThread = IndeterminedProgressThread("counting spots")
            countSpotsThread.connectFinished(progressThread.stop)
            countSpotsThread.start()
            progressThread.start()


    def onClickDecomposeDenseRegions(self):
        activeLayer = self.viewer.layers.selection.active
        if not activeLayer:
            notifications.show_error("Decompose dense regions needs an image!")
            return
        message = "decomposing dense regions on {} (radius xy={}, radius z={}, alpha={}, beta={}, gamma={})."
        notifications.show_info(
            message.format(
                activeLayer.name,
                self.model.decomposeRadiusXY,
                self.model.decomposeRadiusZ,
                self.model.alpha,
                self.model.beta,
                self.model.gamma))
        data = activeLayer.data
        scale = activeLayer.scale
        spotsName = self.decomposeSpotsCombo.currentText()
        spots = self.napariUtil.getDataOfLayerWithName(spotsName)
        self.model.spots = spots
        self.spotsName = spotsName
        decomposeSpotsThread = DecomposeDenseRegionsThread(self.model, data, self.viewer,
                                              spotsName, scale, self.spotDisplaySize)
        progressThread = IndeterminedProgressThread("decomposing dense regions")
        decomposeSpotsThread.connectFinished(progressThread.stop)
        decomposeSpotsThread.start()
        progressThread.start()


    def onClickDetectSpots(self):
        activeLayer = self.viewer.layers.selection.active
        if not activeLayer:
            notifications.show_error("Detect spots needs an image!")
            return
        message = "detecting spots on {} (threshold={}, radius xy={}, radius z={}, remove_duplicates is {} and find_threshold is {})."
        notifications.show_info(
            message.format(
                activeLayer.name,
                self.model.threshold,
                self.model.radiusXY,
                self.model.radiusZ,
                self.model.removeDuplicates,
                self.model.findThreshold))
        data = activeLayer.data
        scale = activeLayer.scale
        name = "spots in {image}".format(image=activeLayer.name)
        detectSpotsThread = DetectSpotsThread(self.model, data, self.viewer,
                                              name, scale, self.spotDisplaySize)
        progressThread = IndeterminedProgressThread("detecting spots")
        detectSpotsThread.connectFinished(progressThread.stop)
        detectSpotsThread.start()
        progressThread.start()


    def onClickSubtractBackground(self):
        activeLayer = self.viewer.layers.selection.active
        if not activeLayer:
            notifications.show_error("Subtract background needs an image!")
            return
        message = \
        "Running background subtraction with sigma xy = {}, sigma z = {} on {}."
        notifications.show_info(
            message.format(
            self.model.getSigmaXY(),
            self.model.getSigmaZ(),
            activeLayer.name))
        data = activeLayer.data
        scale = activeLayer.scale
        sigma = (self.model.getSigmaXY(), self.model.getSigmaXY())
        if data.ndim > 2:
            sigma = (self.model.getSigmaXY(),
                     self.model.getSigmaXY(),
                     self.model.getSigmaZ())
        self.model.setData(data)
        subtractBackgroundTread = SubtractBackgroundThread(self.model, data,
                                                           sigma, self.viewer,
                                                           activeLayer.name,
                                                           scale,
                                                           activeLayer.colormap,
                                                           activeLayer.blending)
        progressThread = IndeterminedProgressThread("subtracting background")
        subtractBackgroundTread.connectFinished(progressThread.stop)
        subtractBackgroundTread.start()
        progressThread.start()



    def onLayerAddedOrRemoved(self, event: Event):
        self.updateLayerSelectionComboBoxes()


    @Slot(int)
    def onRemoveDuplicatesChanged(self, state):
        self.model.removeBackground = (state > 0)


    @Slot(int)
    def onFindThresholdChanged(self, state):
        self.model.findThreshold = (state > 0)


    @Slot(float, float)
    def sigmaChanged(self, sigmaXY, sigmaZ):
        self.sigmaXYInput.setText(str(sigmaXY))
        self.sigmaZInput.setText(str(sigmaZ))


    @Slot(float)
    def thresholdChanged(self, threshold):
        self.thresholdInput.setText(str(threshold))


    @Slot(float, float)
    def radiusChanged(self, radiusXY, radiusZ):
        self.radiusXYInput.setText(str(radiusXY))
        self.radiusZInput.setText(str(radiusZ))


    @Slot(bool)
    def removeDuplicatesChanged(self, state):
        states = [False, True]
        self.removeDuplicatesCheckbox.setCheckState(states.index(state))


    @Slot(bool)
    def findThresholdChanged(self, state):
        states = [False, True]
        self.findThresholdCheckbox.setCheckState(states.index(state))


    @Slot(str)
    def updateSigmaXY(self, text):
        try:
            value = float(text)
        except:
            self.sigmaXYInput.setText(str(self.model.getSigmaXY()))
            return False
        self.model.sigmaXY = value
        return True


    @Slot(str)
    def updateSigmaZ(self, text):
        try:
            value = float(text)
        except:
            self.sigmaZInput.setText(str(self.model.getSigmaZ()))
            return False
        self.model.sigmaZ = value
        return True


    @Slot(str)
    def updateThreshold(self, text):
        try:
            value = float(text)
        except:
            self.thresholdInput.setText(str(self.model.getThreshold()))
            return False
        self.model.threshold = value
        return True


    @Slot(str)
    def updateRadiusXY(self, text):
        try:
            value = float(text)
        except:
            self.radiusXYInput.setText(str(self.model.getRadiusXY()))
            return False
        self.model.radiusXY = value
        return True


    @Slot(str)
    def updateRadiusZ(self, text):
        try:
            value = float(text)
        except:
            self.radiusZInput.setText(str(self.model.getRadiusZ()))
            return False
        self.model.radiusZ = value
        return True


    @Slot(str)
    def updateDecomposeRadiusXY(self, text):
        try:
            value = float(text)
        except:
            self.decomposeRadiusXYInput.setText(str(self.model.getDecomposeRadiusXY()))
            return False
        self.model.decomposeRadiusXY = value
        return True


    @Slot(str)
    def updateDecomposeRadiusZ(self, text):
        try:
            value = float(text)
        except:
            self.decomposeRadiusZInput.setText(str(self.model.getDecomposeRadiusZ()))
            return False
        self.model.decomposeRadiusZ = value
        return True


    @Slot(str)
    def updateAlpha(self, text):
        try:
            value = float(text)
        except:
            self.alphaInput.setText(str(self.model.getAlpha()))
            return False
        self.model.alpha = value
        return True


    @Slot(str)
    def updateBeta(self, text):
        try:
            value = float(text)
        except:
            self.betaInput.setText(str(self.model.getBeta()))
            return False
        self.model.beta = value
        return True


    @Slot(str)
    def updateGamma(self, text):
        try:
            value = float(text)
        except:
            self.gammaInput.setText(str(self.model.getGamma()))
            return False
        self.model.gamma = value
        return True


    def updateLayerSelectionComboBoxes(self):
        labelComboBoxes = [self.cytoCombo, self.nucleiCombo]
        labelLayers = self.napariUtil.getLabelLayers()
        for comboBox in labelComboBoxes:
            WidgetTool.replaceItemsInComboBox(comboBox, labelLayers)
        spotComboBoxes = [self.spotsCombo, self.decomposeSpotsCombo]
        spotLayers = self.napariUtil.getPointsLayers()
        for comboBox in spotComboBoxes:
            WidgetTool.replaceItemsInComboBox(comboBox, spotLayers)


    def addSpotCountingTable(self, table):
        tableView = TableView(table)
        self.viewer.window.add_dock_widget(
                                    tableView, area='right',
                                    name="Nr. Of Spots: " + self.spotsName,
                                    tabify = False)



class WorkerThread:


    def start(self):
        self.worker.start()


    def connectFinished(self, method):
        self.worker.finished.connect(method)





class SubtractBackgroundThread(WorkerThread):


    def __init__(self, model, data, sigma, viewer, name, scale, colormap, blending):
        self.model = model
        self.data = data
        self.name = name
        self.scale = scale
        self.viewer = viewer
        self.colormap = colormap
        self.blending = blending
        self.sigma = sigma
        self.worker = create_worker(self.removeBackground)
        self.worker.returned.connect(self.addImage)


    def addImage(self, data):
        self.viewer.add_image(data, scale=self.scale, name=self.name,
                              colormap=self.colormap,
                              blending=self.blending)


    def removeBackground(self):
        self.model.setData(self.data)
        self.model.subtractBackground(self.sigma)
        return self.model.getResult()



class DetectSpotsThread(WorkerThread):


    def __init__(self, model, data, viewer, name, scale, spotDisplaySize):
        self.model = model
        self.data = data
        self.name = name
        self.scale = scale
        self.viewer = viewer
        self.spotDisplaySize = spotDisplaySize
        self.worker = create_worker(self.detectSpots)
        self.worker.returned.connect(self.addDetectedSpots)



    def addDetectedSpots(self, data):
        '''
        Add the detected spots to the viewer.

        Note that this method needs to bee here and not in the widget, because
        otherwise different threads would potentially read the same data
        (name, scale, ...), which might have been modified in the meantime, for
        example by selecting another input image.
        '''
        self.viewer.add_points(data,
                               name=self.name,
                               size=self.spotDisplaySize,
                               scale=self.scale)


    def detectSpots(self):
        self.model.setData(self.data)
        self.model.detectSpots(tuple(self.scale))
        return self.model.getSpots()


class DecomposeDenseRegionsThread(WorkerThread):


    def __init__(self, model, data, viewer, name, scale, spotDisplaySize):
        self.model = model
        self.data = data
        self.name = name
        self.scale = scale
        self.viewer = viewer
        self.spotDisplaySize = spotDisplaySize
        self.worker = create_worker(self.decompose)
        self.worker.returned.connect(self.addSpots)


    def addSpots(self, data):
        self.viewer.add_points(data,
                               name=self.name,
                               size=self.spotDisplaySize,
                               scale=self.scale)


    def decompose(self):
         self.model.setData(self.data)
         self.model.decomposeDenseRegions(tuple(self.scale))
         return self.model.spots


class CountSpotsThread(WorkerThread):


    def __init__(self, model, parent, spots, spotsName,
                       cytoLabels, nucleiMask, headings):
        self.model = model
        self.spots = spots
        self.spotsName = spotsName
        self.model.spots = self.spots
        self.cytoLabels = cytoLabels
        self.nucleiMask = nucleiMask
        self.headings = headings
        self.worker = create_worker(self.countSpots)
        self.worker.returned.connect(parent.addSpotCountingTable)


    def countSpots(self):
        self.model.countSpotsPerCellAndEnvironment(self.cytoLabels,
                                                   self.nucleiMask)
        data = self.model.getSpotCountPerCellAndEnvironment()
        for row in data:
            row.insert(0, self.spotsName)
        columns = list(zip(*data))
        table = {}
        for index, column in enumerate(columns):
            table[self.headings[index]] = column
        return table



class IndeterminedProgressThread:


    def __init__(self, description):
        self.worker = create_worker(self.yieldUndeterminedProgress)
        self.progress = progress(total=0)
        self.progress.set_description(description)


    def yieldUndeterminedProgress(self):
        while True:
            time.sleep(0.05)


    def start(self):
        self.worker.start()


    def stop(self):
        self.progress.close()
        self.worker.quit()
