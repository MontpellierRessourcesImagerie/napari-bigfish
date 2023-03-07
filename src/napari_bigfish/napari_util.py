from napari.layers.labels.labels import Labels
from napari.layers.points.points import Points

class NapariUtil:

    def __init__(self, viewer):
        self.viewer = viewer


    def getLabelLayers(self):
        return self.getLayersOfType(Labels)


    def getPointsLayers(self):
        return self.getLayersOfType(Points)


    def getLayersOfType(self, layerType):
        layers = [layer.name for layer in self.viewer.layers if isinstance(layer, layerType)]
        return layers


    def getDataOfLayerWithName(self, name):
        for layer in self.viewer.layers:
            if layer.name == name:
                return layer.data
        return None

