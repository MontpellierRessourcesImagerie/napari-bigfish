"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/stable/plugins/guides.html?#widgets

Replace code below according to your needs.
"""
from typing import TYPE_CHECKING

from magicgui import magic_factory
from qtpy.QtWidgets import QHBoxLayout, QPushButton, QWidget, QLabel, QLineEdit
from qtpy.QtCore import Slot
from napari_bigfish.bigfishapp import BigfishApp
from napari.utils import notifications
import numpy as np

if TYPE_CHECKING:
    import napari


class ExampleQWidget(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # in one of two ways:
    # 1. use a parameter called `napari_viewer`, as done here
    # 2. use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, napari_viewer):
        super().__init__()
        self.setModel(BigfishApp())
        self.viewer = napari_viewer

        sigmaXYLabel = QLabel(self)
        sigmaXYLabel.setText("sigma xy: ")
        self.sigmaXYInput = QLineEdit(self)
        self.sigmaXYInput.setText(str(self.model.getSigmaXY()))
        self.sigmaXYInput.textChanged.connect(self.updateSigmaXY)
        self.sigmaXYInput.setMaximumWidth(50)

        sigmaZLabel = QLabel(self)
        sigmaZLabel.setText("sigma z: ")
        self.sigmaZInput = QLineEdit(self)
        self.sigmaZInput.setText(str(self.model.getSigmaZ()))
        self.sigmaZInput.textChanged.connect(self.updateSigmaZ)
        self.sigmaZInput.setMaximumWidth(50)

        btn = QPushButton("Subtract Background")
        btn.clicked.connect(self.onClickSubtractBackground)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(sigmaXYLabel)
        self.layout().addWidget(self.sigmaXYInput)
        self.layout().addWidget(sigmaZLabel)
        self.layout().addWidget(self.sigmaZInput)
        self.layout().addWidget(btn)


    def setModel(self, aModel):
        self.model = aModel
        self.model.sigma.connect(self.sigmaChanged)


    def onClickSubtractBackground(self):
        activeLayer = self.viewer.layers.selection.active
        if not activeLayer:
            notifications.show_error("Subtract background needs an image!")
            return
        notifications.show_info("Running background subtraction with sigma xy = {}, sigma z = {} on {}.".format(self.model.getSigmaXY(), self.model.getSigmaZ(), activeLayer.name))
        data = activeLayer.data
        scale = activeLayer.scale
        if data.shape[0] == 1:
            data = np.squeeze(data, axis=0)
            scale = scale[1:]
        sigma = (self.model.getSigmaXY(), self.model.getSigmaXY())
        if data.ndim > 2:
            sigma = (self.model.getSigmaXY(), self.model.getSigmaXY(), self.model.getSigmaZ())
        self.model.setData(data)
        self.model.subtractBackground(sigma)
        cleaned = self.model.getResult()
        self.viewer.add_image(cleaned, scale=scale, name=activeLayer.name, colormap=activeLayer.colormap, blending=activeLayer.blending)



    @Slot(float, float)
    def sigmaChanged(self, sigmaXY, sigmaZ):
        self.sigmaXYInput.setText(str(sigmaXY))
        self.sigmaZInput.setText(str(sigmaZ))


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



@magic_factory
def example_magic_widget(img_layer: "napari.layers.Image"):
    print(f"you have selected {img_layer}")


# Uses the `autogenerate: true` flag in the plugin manifest
# to indicate it should be wrapped as a magicgui to autogenerate
# a widget.
def example_function_widget(img_layer: "napari.layers.Image"):
    print(f"you have selected {img_layer}")
