from napari.layers.labels.labels import Labels
from napari.layers.points.points import Points

class NapariUtil:
    """ Utility methods for the napari image viewer.
    """

    def __init__(self, viewer):
        """ Constructor.

        :param viewer: the napari viewer
        :type viewer: napari.viewer.Viewer
        """
        self.viewer = viewer


    def getLabelLayers(self):
        """ Return all label layers

        :return: A list of the label layers in the viewer
        :rtype: [napari.layers.labels.labels.Labels]
        """
        return self.getLayersOfType(Labels)


    def getPointsLayers(self):
        """ Return all point layers

        :return: A list of the point layers in the viewer
        :rtype: [napari.layers.points.points.Points]
        """
        return self.getLayersOfType(Points)


    def getLayersOfType(self, layerType):
        """ Return all layers of type layerType in the viewer

        :param layerType: A napari layer type like Labels or Points.
        :return: A list of the layers with the given type
        """
        layers = [layer.name for layer in self.viewer.layers if isinstance(layer, layerType)]
        return layers


    def getDataOfLayerWithName(self, name):
        """ Return the data of the layer with the given name.

        :param name: The name of the layer
        :type name: str
        :return: The layer with the given name if it exists and None otherwise
        """
        for layer in self.viewer.layers:
            if layer.name == name:
                return layer.data
        return None

