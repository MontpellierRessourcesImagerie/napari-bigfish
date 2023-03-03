"""
A Widget to run the bigfish FISH-spot detection
"""
import numpy as np
from typing import TYPE_CHECKING
from magicgui import magic_factory
from qtpy.QtWidgets import QVBoxLayout, QFormLayout
from qtpy.QtWidgets import QPushButton, QWidget, QLabel, QCheckBox
from qtpy.QtCore import Slot
from napari.utils import notifications
from napari_bigfish.bigfishapp import BigfishApp
from napari_bigfish.qtutil import WidgetTool


if TYPE_CHECKING:
    import napari


class DetectFISHSpotsWidget(QWidget):


    def __init__(self, napari_viewer):
        super().__init__()
        self.setModel(BigfishApp())
        self.viewer = napari_viewer
        self.fieldWidth = 50
        self.maxButtonWidth = 200
        self.spotDisplaySize = 5
        self.setLayout(QVBoxLayout())
        self.addSubtractBackgroundWidget(1)
        self.addDetectSpotsWidget(2)


    def addSubtractBackgroundWidget(self, line):
        formLayout = QFormLayout()
        sigmaXYLabel, self.sigmaXYInput = \
         WidgetTool.getLineInput(self, "sigma xy: ",self.model.getSigmaXY(),
                                 self.fieldWidth, self.updateSigmaXY)
        sigmaZLabel, self.sigmaZInput = \
         WidgetTool.getLineInput(self, "sigma z: ",self.model.getSigmaZ(),
                                 self.fieldWidth, self.updateSigmaZ)
        subtractBackgroundButton = QPushButton("Subtract Background")
        subtractBackgroundButton.setMaximumWidth(self.maxButtonWidth)
        subtractBackgroundButton.clicked.connect(self.onClickSubtractBackground)
        formLayout.addRow(sigmaXYLabel, self.sigmaXYInput)
        formLayout.addRow(sigmaZLabel, self.sigmaZInput)
        self.layout().addLayout(formLayout)
        self.layout().addWidget(subtractBackgroundButton)


    def addDetectSpotsWidget(self, line):
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
        self.layout().addLayout(formLayout)
        self.layout().addWidget(self.removeDuplicatesCheckbox)
        self.layout().addWidget(self.findThresholdCheckbox)
        self.layout().addWidget(detectSpotsButton)


    def setModel(self, aModel):
        self.model = aModel
        self.model.sigmaSignal.connect(self.sigmaChanged)
        self.model.thresholdSignal.connect(self.thresholdChanged)
        self.model.radiusSignal.connect(self.radiusChanged)
        self.model.removeDuplicatesSignal.connect(self.removeDuplicatesChanged)
        self.model.findThresholdSignal.connect(self.findThresholdChanged)


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
        self.model.setData(data)
        self.model.detectSpots(tuple(scale))
        name = "spots in {image}".format(image=activeLayer.name)
        self.viewer.add_points(self.model.getSpots(),
                               name=name,
                               size=self.spotDisplaySize,
                               scale=scale)


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


    @Slot(int)
    def onRemoveDuplicatesChanged(self, state):
        self.model.removeBackground = (state==1)


    @Slot(int)
    def onFindThresholdChanged(self, state):
        self.model.findThreshold = (state==1)


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


