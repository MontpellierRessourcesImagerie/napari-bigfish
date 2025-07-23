"""
A Widget to run the bigfish FISH-spot detection
"""
import time
import numpy as np
import napari
from pathlib import Path
from magicgui import magic_factory
from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout, QListView, QAbstractItemView
from qtpy.QtWidgets import QPushButton, QWidget, QLabel, QCheckBox, QGroupBox
from qtpy.QtWidgets import QFileDialog, QAction
from qtpy.QtCore import Qt
from qtpy.QtGui import QStandardItemModel, QStandardItem, QKeySequence
from qtpy.QtCore import Slot, QObject
from napari.qt.threading import thread_worker
from napari.qt.threading import create_worker
from napari.utils import notifications
from napari.utils import progress
from napari.utils.events import Event
from napari_bigfish.bigfishapp import BigfishApp
from napari_bigfish.qtutil import WidgetTool, TableView
from napari_bigfish.napari_util import NapariUtil



FIELD_WIDTH = 50
COMBO_BOX_MAX_WIDTH = 150
MAX_BUTTON_WIDTH = 200
MIN_LIST_WIDTH = 200
MIN_LIST_HEIGHT = 100
SPOT_DISPLAY_SIZE = 5
SPACING = 20
FILE_EXTENSIONS = ['*.tif', '*.tiff', '*.jpg']



class DetectFISHSpotsWidget(QWidget):
    """ The widget allows to parametrize and run background subtraction
    and spot detection on the active image.

    The widget regroups the operations ``subtract background``,
    ``detect spots``, ``decompose dense regions`` and ``count spots``. It also
    has a button to change to the ``Batch Processing``-widget, which will use
    the parameters entered here.
    """


    def __init__(self, napari_viewer):
        """The constructor creates and connects the widget.
        """
        super().__init__()
        self.setModel(BigfishApp())
        self.viewer = napari_viewer
        self.napariUtil = NapariUtil(self.viewer)
        self.fieldWidth = FIELD_WIDTH
        self.maxButtonWidth = MAX_BUTTON_WIDTH
        self.spotDisplaySize = SPOT_DISPLAY_SIZE
        self.setLayout(QVBoxLayout())
        self.addSubtractBackgroundWidget()
        self.layout().addSpacing(SPACING)
        self.addDetectSpotsWidget()
        self.layout().addSpacing(SPACING)
        self.addDecomposeDenseRegionsWidget()
        self.layout().addSpacing(SPACING)
        self.addCountSpotsWidget()
        self.layout().addSpacing(SPACING)
        self.addBatchButton()
        self.viewer.layers.events.inserted.connect(self.onLayerAddedOrRemoved)
        self.viewer.layers.events.removed.connect(self.onLayerAddedOrRemoved)


    def addSubtractBackgroundWidget(self):
        """Adds the widget for the background subtration to the layout. The
        widget has two input fields for the sigma of the Gaussian in xy and z
        and an action button to run the operation.
        """
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
        """Adds the widget for the spot detection to the layout. The widget has
        an input field for the threshold, input fields for the spot radius,
        checkboxes for the ``remove duplicates``and ``find threshold`` options
        and an action button to run the operation.
        """
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
        """
        Add the widget for the Dense Region Decomposition to the layout. The
        widget has a combo-box for the selection of the points-layer containing
        the previously detected spots. It has input fields for the spot radius
        and for the alpha, beta and gamma parameters. It has an action button to
        run the operation on the active image layer.
        """
        groupBox = QGroupBox("Decompose Dense Regions")
        formLayout = QFormLayout()
        spotLayers = self.napariUtil.getPointsLayers()
        spotsLabel, self.decomposeSpotsCombo = WidgetTool.getComboInput(self,
                                            "spots: ",
                                            spotLayers)
        self.decomposeSpotsCombo.setMaximumWidth(COMBO_BOX_MAX_WIDTH)
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
        """Add the widget for the Spot Counting operation to the layout. The
        widget has combo-boxes for the selection of the points-layer containing
        the spots, the labels layer containing the cells and the labels-layer
        containing the nuclei. It has an action button to run the operation.
        """
        groupBox = QGroupBox("Spot Counting")
        formLayout = QVBoxLayout()
        spotLayers = self.napariUtil.getPointsLayers()
        spotsLabel, self.spotsCombo = WidgetTool.getComboInput(self,
                                            "spots: ",
                                            spotLayers)
        self.spotsCombo.setMaximumWidth(COMBO_BOX_MAX_WIDTH)
        labelLayers = self.napariUtil.getLabelLayers()
        cytoLabel, self.cytoCombo = WidgetTool.getComboInput(self,
                                            "cytoplasm labels: ",
                                            labelLayers)
        nucleiLabel, self.nucleiCombo = WidgetTool.getComboInput(self,
                                            "nuclei labels or mask: ",
                                            labelLayers)
        self.nucleiCombo.setMaximumWidth(COMBO_BOX_MAX_WIDTH)
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


    def addBatchButton(self):
        """Adds an action button that closes this widget and opens the batch-
        processing widget. The model, containg the parameters are transferred
        to the new widget.
        """
        layout = QHBoxLayout()
        batchButton = QPushButton("Run Batch")
        batchButton.setMaximumWidth(self.maxButtonWidth)
        batchButton.clicked.connect(self.onClickBatch)
        layout.addWidget(batchButton)
        self.layout().addLayout(layout)


    def setModel(self, aModel):
        self.model = aModel
        self.model.sigmaSignal.connect(self.sigmaChanged)
        self.model.thresholdSignal.connect(self.thresholdChanged)
        self.model.radiusSignal.connect(self.radiusChanged)
        self.model.removeDuplicatesSignal.connect(self.removeDuplicatesChanged)
        self.model.findThresholdSignal.connect(self.findThresholdChanged)


    def onClickBatch(self):
        self.viewer.window.remove_dock_widget(self)
        batchWidget = DetectFISHSpotsBatchWidget(self.viewer, self.model)
        self.viewer.window.add_dock_widget(
                                    batchWidget, area='right',
                                    name="Bigfish Batch Processing",
                                    tabify = False)


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
        self.model.setData(data)
        subtractBackgroundTread = SubtractBackgroundThread(self.model, data,
                                                           self.viewer,
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
        self.model.removeDuplicates = (state > 0)


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
    """Superclass for the different classes of long running operations, that are
    meant to be executed in a parallel thread.
    """

    def start(self):
        """Start the operation in a different thread.
        """
        self.worker.start()


    def connectFinished(self, method):
        """Connect the finished signal of the operation to the given method.

        :param method: The function that will be executed when the operation
                       finished
        """
        self.worker.finished.connect(method)



class SubtractBackgroundThread(WorkerThread):
    """Run the subtract background operation in a separate thread. When the
    thread finished, add the result image to the viewer.
    """


    def __init__(self, model, data, viewer, name, scale, colormap, blending):
        self.model = model
        self.data = data
        self.name = name
        self.scale = scale
        self.viewer = viewer
        self.colormap = colormap
        self.blending = blending
        self.worker = create_worker(self.removeBackground)
        self.worker.returned.connect(self.addImage)


    def addImage(self, data):
        self.viewer.add_image(data, scale=self.scale, name=self.name,
                              colormap=self.colormap,
                              blending=self.blending)


    def removeBackground(self):
        self.model.setData(self.data)
        self.model.subtractBackground()
        return self.model.getResult()



class DetectSpotsThread(WorkerThread):
    """Run the spot detection in a separate thread. After the spot detection
    finished, add the detected spots in the form of a points layer to the
    viewer.
    """


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

        Note that this method needs to be here and not in the widget, because
        otherwise different threads would potentially read the same data
        (name, scale, ...), which might have been modified in the meantime, for
        example by selecting another input image.
        '''
        self.viewer.add_points(data,
                               name=self.name,
                               size=self.spotDisplaySize,
                               scale=self.scale)


    def detectSpots(self):
        data = self.data
        originalNumberOfDims = len(data.shape)
        if originalNumberOfDims > 3:
            data = np.squeeze(data)
        if np.amax(data) > 1:
            data = data / np.amax(data)
        scale = self.scale
        if len(scale) > 3:
            scale = scale[1:len(scale)]
        self.model.setData(data)
        self.model.detectSpots(tuple(scale))
        result = self.model.getSpots()
        if len(result[0]) < originalNumberOfDims:
            return np.hstack((np.zeros((len(result), 1), dtype=result.dtype), result))
        return result


class DecomposeDenseRegionsThread(WorkerThread):
    """Run the Dense Region Decomposition in a separate thread. When finished,
    add the resulting spots in the form of a points-layer to the viewer.
    """


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
    """Run the spot counting in a separate thread. Once the operation
    finished, ``addSpotCountingTable`` of the parent widget is called.
    """

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



class BatchCountSpotsThread(WorkerThread):
    """Run the batch-processing in a separate thread.
    """


    def __init__(self, scale, model, inputImages, cellLabels, nucleiMasks,
                 subtractBackground=False, decomposeDenseRegions=False):
        self.scale = scale
        self.model = model
        self.inputImages = inputImages
        self.cellLabels = cellLabels
        self.nucleiMasks = nucleiMasks
        self.subtractBackground = subtractBackground
        self.decomposeDenseRegions = decomposeDenseRegions
        self.worker = create_worker(self.batchCountSpots)


    def batchCountSpots(self):
            self.model.runBatch(
                            self.scale,
                            self.inputImages,
                            self.cellLabels,
                            self.nucleiMasks,
                            subtractBackground = self.subtractBackground,
                            decomposeDenseRegions= self.decomposeDenseRegions)
            return self



class Progress(QObject):
    """A progress indicator for operations running in a parallel thread. The
    operation needs to connect a signal to the progressChanged method, with the
    current progress and the maximum progress value.
    """

    def __init__(self, parent, maxProgress, description):
        """Create a new progress-indicator with the given parent-widget, maximum
        progress value and description.
        """
        super().__init__(parent)
        self.progress = progress(total=maxProgress)
        self.progress.set_description(description)


    @Slot(int, int)
    def progressChanged(self, value, maxProgress):
        """Update the progress value and the max. progress value.
        """
        self.progress.update(value)
        self.progress.set_description("Processing image {} of {}".format(
                                                                value,
                                                                maxProgress))
        return True


    def processFinished(self):
        self.progress.close()



class IndeterminedProgressThread:
    """An indetermined progress indicator that moves while an operation is
    still working.
    """

    def __init__(self, description):
        """Create a new indetermined progress indicator with the given
        description.
        """
        self.worker = create_worker(self.yieldUndeterminedProgress)
        self.progress = progress(total=0)
        self.progress.set_description(description)


    def yieldUndeterminedProgress(self):
        """The progress indicator has nothing to do by himself, so just
        sleep and yield, while still running.
        """
        while True:
            time.sleep(0.05)
            yield


    def start(self):
        """Start the operation in a parallel thread"""
        self.worker.start()


    def stop(self):
        """Close the progress indicator and quite the parallel thread.
        """
        self.progress.close()
        self.worker.quit()



class DetectFISHSpotsBatchWidget(QWidget):
    """The widget that lets the user select images and start the
    batch-processing. The widget has input fields for the scale in xy and z,
    checkboxes for the options ``subtract background`` and ``decompose dense
    regions``, image-lists for the input images, the cell labels and the nuclei
    masks and an action button to start the batch-processing.
    """

    def __init__(self, napari_viewer, model):
        super().__init__()

        self.scaleXY = 300
        self.scaleZ = 900
        self.subtractBackground = False
        self.decomposeDenseRegions = False
        self.setModel(model)
        self.viewer = napari_viewer
        activeLayer = self.viewer.layers.selection.active
        if activeLayer:
            self.scaleXY = activeLayer.scale[-1]
            if activeLayer.data.ndim > 2:
                self.scaleZ = activeLayer.scale[-3]
        self.viewer.layers.events.inserted.connect(self.onLayerLoaded)
        self.fieldWidth = FIELD_WIDTH
        self.maxButtonWidth = MAX_BUTTON_WIDTH
        self.spotDisplaySize = SPOT_DISPLAY_SIZE
        self.setLayout(QVBoxLayout())
        self.addBatchParameterWidget()
        self.layout().addSpacing(SPACING)
        self.addInputImagesWidget()
        self.layout().addSpacing(SPACING)
        self.addRunButton()


    def onLayerLoaded(self, event):
        layers = event.source
        for layer in layers:
            if isinstance(layer, napari.layers.points.points.Points):
                scale = (self.scaleXY, self.scaleXY)
                if layer.ndim > 2:
                    scale = (self.scaleZ, self.scaleXY, self.scaleXY)
                layer.scale = scale


    def setModel(self, aModel):
        self.model = aModel


    def addBatchParameterWidget(self):
        groupBox = QGroupBox("Parameters")
        formLayout = QFormLayout()
        scaleXYLabel, self.scaleXYInput = \
         WidgetTool.getLineInput(self, "scale xy [nm]: ",
                                       self.scaleXY,
                                       self.fieldWidth,
                                       self.updateScaleXY)
        scaleZLabel, self.scaleZInput = \
         WidgetTool.getLineInput(self, "scale z [nm]: ",
                                       self.scaleZ,
                                       self.fieldWidth,
                                       self.updateScaleZ)
        self.subtractBackgroundCheckbox = QCheckBox("subtract background")
        self.subtractBackgroundCheckbox.setChecked(self.subtractBackground)
        self.subtractBackgroundCheckbox.stateChanged.connect(self.onSubtractBackgroundChanged)

        self.decomposeDenseRegionsCheckbox = QCheckBox("decompose dense regions")
        self.decomposeDenseRegionsCheckbox.setChecked(self.decomposeDenseRegions)
        self.decomposeDenseRegionsCheckbox.stateChanged.connect(self.onDecomposeChanged)

        formLayout.addRow(scaleXYLabel, self.scaleXYInput)
        formLayout.addRow(scaleZLabel, self.scaleZInput)
        verticalLayout = QVBoxLayout()
        verticalLayout.addLayout(formLayout)
        verticalLayout.addWidget(self.subtractBackgroundCheckbox)
        verticalLayout.addWidget(self.decomposeDenseRegionsCheckbox)

        groupBox.setLayout(verticalLayout)
        self.layout().addWidget(groupBox)


    def addInputImagesWidget(self):
        groupBox = QGroupBox("Images And Labels")
        self.inputImageListWidget = ImageListWidget("Input Images")
        self.cellLabelsListWidget = ImageListWidget("Cell Label Images")
        self.nucleiMasksListWidget = ImageListWidget("Nuclei Mask Images")
        verticalLayout = QVBoxLayout()
        verticalLayout.addWidget(self.inputImageListWidget)
        verticalLayout.addWidget(self.cellLabelsListWidget)
        verticalLayout.addWidget(self.nucleiMasksListWidget)
        groupBox.setLayout(verticalLayout)
        self.layout().addWidget(groupBox)


    def addRunButton(self):
        runBatchButton = QPushButton("Run")
        runBatchButton.setMaximumWidth(self.maxButtonWidth)
        runBatchButton.clicked.connect(self.runBatch)
        horizontalLayout = QHBoxLayout()
        horizontalLayout.addWidget(runBatchButton)
        self.layout().addLayout(horizontalLayout)


    @Slot(str)
    def updateScaleXY(self, text):
        try:
            value = float(text)
        except:
            self.scaleXYInput.setText(str(self.scaleXY))
            return False
        self.scaleXY = value
        return True


    @Slot(str)
    def updateScaleZ(self, text):
        try:
            value = float(text)
        except:
            self.scaleZInput.setText(str(self.scaleZ))
            return False
        self.scaleZ = value
        return True


    @Slot(int)
    def onSubtractBackgroundChanged(self, state):
        self.subtractBackground = (state > 0)


    @Slot(int)
    def onDecomposeChanged(self, state):
        self.decomposeDenseRegions = (state > 0)


    def runBatch(self):
        scale = (self.scaleZ, self.scaleXY, self.scaleXY)
        inputImages = self.inputImageListWidget.getValues()
        cellLabels = self.cellLabelsListWidget.getValues()
        nucleiMasks = self.nucleiMasksListWidget.getValues()
        if not cellLabels:
            cellLabels = None
        if not nucleiMasks:
            nucleiMasks = None
        self.batchThread = BatchCountSpotsThread(
                            scale,
                            self.model,
                            inputImages,
                            cellLabels = cellLabels,
                            nucleiMasks = nucleiMasks,
                            subtractBackground = self.subtractBackground,
                            decomposeDenseRegions = self.decomposeDenseRegions)
        progress = Progress(self, len(inputImages), "Big Fish Batch Processing Started")
        self.model.progressSignal.connect(progress.progressChanged)
        self.batchThread.worker.returned.connect(progress.processFinished)
        self.batchThread.start()



class ImageListWidget(QWidget):
    """An image-list widget that has a list of images, a button that opens
    a file-dialog to add images, a button to clear the list and a context-menu
    that allows to remove the selected images from the list.
    """

    def __init__(self, name):
        super().__init__()
        self.minWidth = MIN_LIST_WIDTH
        self.minHeight = MIN_LIST_HEIGHT
        self.name = name
        self.setLayout(QVBoxLayout())
        self.fieldWidth = FIELD_WIDTH
        self.maxButtonWidth = MAX_BUTTON_WIDTH
        self.addImageListWidget()
        self.currentFolder = str(Path.home())


    def getFileExtensions(self):
        return " ".join(FILE_EXTENSIONS)


    def addImageListWidget(self):
        groupBox = QGroupBox(self.name)
        self.listView = QListView()
        self.listView.setMinimumSize(self.minWidth, self.minHeight)

        self.listView.setContextMenuPolicy(Qt.ActionsContextMenu)
        copyAction = QAction("Remove\tDel", self)
        copyAction.setShortcut(QKeySequence(QKeySequence.Delete))
        copyAction.triggered.connect(self.deleteSelection)
        self.listView.addAction(copyAction)
        self.listView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.model = QStandardItemModel(self.listView)
        self.listView.setModel(self.model)
        self.addFilesButton = QPushButton("Add Files")
        self.addFilesButton.setMaximumWidth(self.maxButtonWidth)
        self.addFilesButton.clicked.connect(self.onClickAddFiles)
        self.clearFilesButton = QPushButton("Clear")
        self.clearFilesButton.setMaximumWidth(self.maxButtonWidth)
        self.clearFilesButton.clicked.connect(self.onClickClearFiles)
        verticalLayout = QVBoxLayout()
        horizontalLayout = QHBoxLayout()
        horizontalLayout.addWidget(self.listView)
        verticalLayout.addLayout(horizontalLayout)
        horizontalLayoutButtons = QHBoxLayout()
        horizontalLayoutButtons.addWidget(self.addFilesButton)
        horizontalLayoutButtons.addWidget(self.clearFilesButton)
        verticalLayout.addLayout(horizontalLayoutButtons)
        groupBox.setLayout(verticalLayout)
        self.layout().addWidget(groupBox)


    def onClickAddFiles(self):
        files, _ = QFileDialog.getOpenFileNames(
                        self,
                        "Select one or more files to open",
                        self.currentFolder,
                        "Images ("+self.getFileExtensions()+")")
        if files:
            self.currentFolder = str(Path(files[0]).parent)
        files.sort()
        for file in files:
           self.model.appendRow(QStandardItem(file))


    def onClickClearFiles(self):
        self.model.clear()


    def deleteSelection(self):
        ranges = self.listView.selectionModel().selection()
        for range in ranges:
            self.listView.model().removeRows(range.top(), range.height())


    def getValues(self):
        model = self.listView.model()
        values = []
        for row in range(0, model.rowCount()):
            item = model.item(row, 0)
            if item:
                values.append(item.text())
        return values