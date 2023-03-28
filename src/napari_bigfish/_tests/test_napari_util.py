import numpy as np
from napari_bigfish.napari_util import NapariUtil


def testGetDataOfLayerWithName(make_napari_viewer):
    viewer = make_napari_viewer()
    data1 = np.random.random((100, 100))
    data2 = np.random.random((10, 10))
    viewer.add_image(data1, name="first")
    viewer.add_image(data2, name="second")
    util = NapariUtil(viewer)
    firstData = util.getDataOfLayerWithName("first")
    assert(firstData is data1)
    secondData = util.getDataOfLayerWithName("second")
    assert(secondData is data2)
    thirdData = util.getDataOfLayerWithName("third")
    assert(thirdData is None)