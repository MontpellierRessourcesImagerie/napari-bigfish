import sys
import numpy as np
from napari_bigfish.bigfishapp import BigfishApp
from unittest.mock import MagicMock
from unittest.mock import patch
import unittest.mock as mock



def testRunBatchEmpty():
    app = BigfishApp()
    app.setProgressMax(10)
    app.runBatch((1, 1, 3), [])
    assert(app.progressMax == 0)


@mock.patch('skimage.io.imread')
def testRunBatch(mockImRead):
    read_data = "1, 2, 3"
    mock_open = mock.mock_open(read_data=read_data)
    imageData = np.random.random((256, 256))
    mockImRead.return_value = imageData
    with mock.patch('builtins.open', mock_open):
        app = BigfishApp()
        app.findThreshold = False
        app.setProgressMax(10)
        app.runBatch((1, 1, 3), ["a", "b"])
    assert(app.progressMax == 2)


@mock.patch('skimage.io.imread')
def testRunBatchWithSubtractBackground(mockImRead):
    read_data = "1, 2, 3"
    mock_open = mock.mock_open(read_data=read_data)
    imageData = np.random.random((256, 256))
    mockImRead.return_value = imageData
    with mock.patch('builtins.open', mock_open):
        app = BigfishApp()
        app.findThreshold = False
        app.setProgressMax(10)
        app.runBatch((1, 1, 3), ["a", "b"], subtractBackground = True)
    assert(app.progressMax == 2)


@mock.patch('skimage.io.imread')
def testRunBatchWithDecomposeDenseRegions(mockImRead):
    read_data = "1, 2, 3"
    mock_open = mock.mock_open(read_data=read_data)
    imageData = np.random.random((256, 256))
    mockImRead.return_value = imageData
    with mock.patch('builtins.open', mock_open):
        app = BigfishApp()
        app.findThreshold = False
        app.setProgressMax(10)
        app.runBatch((1, 1, 3), ["a", "b"], decomposeDenseRegions = True)
    assert(app.progressMax == 2)


@mock.patch('skimage.io.imread')
def testRunBatchWithLabelsAndMask(mockImRead):
    read_data = "1, 2, 3"
    mock_open = mock.mock_open(read_data=read_data)
    imageData = np.random.random((256, 256))
    labels = np.random.randint((256, 256))
    mask = np.random.random((256, 256))
    mask[ mask > 0.5] = 255
    mask[ mask <= 0.5] = 0
    mockImRead.return_value = imageData
    with mock.patch('builtins.open', mock_open):
        app = BigfishApp()
        app.findThreshold = False
        app.setProgressMax(10)
        app.runBatch((1, 1, 3), ["a", "b"], cellLabels=[labels, labels], nucleiMasks=[mask, mask])
    assert(app.progressMax == 2)

