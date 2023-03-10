"""
A Widget to run the bigfish FISH-spot detection
"""
import numpy as np
from typing import TYPE_CHECKING
from magicgui import magic_factory
from qtpy.QtWidgets import QVBoxLayout, QFormLayout
from qtpy.QtWidgets import QPushButton, QWidget, QLabel, QCheckBox, QGroupBox
from qtpy.QtCore import Slot
from napari.qt.threading import thread_worker
from napari.utils import notifications
from napari.utils import progress
from napari.utils.events import Event
from napari_bigfish.bigfishapp import BigfishApp
from napari_bigfish.qtutil import WidgetTool, TableView
from napari_bigfish.napari_util import NapariUtil

if TYPE_CHECKING:
    import napari

@Slot(object)
def addDetectedSpots(obj):
    obj.viewer.add_points(obj.model.getSpots(),
                            name=obj.name,
                            size=obj.spotDisplaySize,
                            scale=obj.scale)


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
            self.model.countSpotsPerCellAndEnvironment(cytoLabels, nucleiMask)
            data = self.model.getSpotCountPerCellAndEnvironment()
            for row in data:
                row.insert(0, spotsName)
            columns = list(zip(*data))
            table = {}
            for index, column in enumerate(columns):
                table[headings[index]] = column
            tableView = TableView(table)
            self.viewer.window.add_dock_widget(tableView, area='right', name="Nr. Of Spots: " + spotsName, tabify = False)



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
        squeezed = False
        if data.shape[0] == 1:
            data = np.squeeze(data, axis=0)
            scale = scale[1:]
            squeezed = True
        name = "spots in {image}".format(image=activeLayer.name)
        self.detectSpots(data, name, scale)


    @thread_worker(connect={"returned": addDetectedSpots})
    def detectSpots(self, data, name, scale):
        self.model.setData(data)
        self.model.detectSpots(tuple(scale))
        self.name = name
        self.scale = scale
        return self


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
        squeezed = False
        if data.shape[0] == 1:
            data = np.squeeze(data, axis=0)
            scale = scale[1:]
            squeezed = True
        sigma = (self.model.getSigmaXY(), self.model.getSigmaXY())
        if data.ndim > 2:
            sigma = (self.model.getSigmaXY(),
                    self.model.getSigmaXY(),
                    self.model.getSigmaZ())
        self.model.setData(data)
        self.model.subtractBackground(sigma)
        cleaned = self.model.getResult()
        if squeezed:
            cleaned = np.expand_dims(cleaned, axis=0)
        self.viewer.add_image(cleaned, scale=scale, name=activeLayer.name,
                              colormap=activeLayer.colormap,
                              blending=activeLayer.blending)


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


    def updateLayerSelectionComboBoxes(self):
        labelComboBoxes = [self.cytoCombo, self.nucleiCombo]
        labelLayers = self.napariUtil.getLabelLayers()
        for comboBox in labelComboBoxes:
            WidgetTool.replaceItemsInComboBox(comboBox, labelLayers)
        spotComboBoxes = [self.spotsCombo]
        spotLayers = self.napariUtil.getPointsLayers()
        for comboBox in spotComboBoxes:
            WidgetTool.replaceItemsInComboBox(comboBox, spotLayers)
