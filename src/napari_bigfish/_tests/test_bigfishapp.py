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


@mock.patch('os.path.exists')
def testReportSpots(mockPathExists):
    mockPathExists.return_value = True
    with patch('builtins.open', mock.mock_open()) as m:
        app = BigfishApp()
        app.spots = [(1,2,3), (4,5,6)]
        app.reportSpots("./a")
    handle = m()
    handle.write.assert_any_call('index,axis-0,axis-1,axis-2')
    handle.write.assert_any_call("\n")
    handle.write.assert_any_call('1,1,2,3')
    handle.write.assert_any_call("\n")
    handle.write.assert_any_call('2,4,5,6')
    handle.write.assert_any_call("\n")


def testGettersAndSetters():
    app = BigfishApp()

    app.setSigmaXY(2.3)
    sigma = app.getSigmaXY()
    assert(sigma == 2.3)

    app.setSigmaZ(0.7)
    sigma = app.getSigmaZ()
    assert(sigma == 0.7)

    app.setRadiusXY(350)
    radius = app.getRadiusXY()
    assert(radius == 350)

    app.setRadiusZ(1050)
    radius = app.getRadiusZ()
    assert(radius == 1050)

    app.setDecomposeRadiusXY(351)
    radius = app.getDecomposeRadiusXY()
    assert(radius == 351)

    app.setDecomposeRadiusZ(1051)
    radius = app.getDecomposeRadiusZ()
    assert(radius == 1051)

    app.setAlpha(0.6)
    alpha = app.getAlpha()
    assert(alpha == 0.6)

    app.setBeta(0.9)
    beta = app.getBeta()
    assert(beta == 0.9)

    app.setGamma(10)
    gamma = app.getGamma()
    assert(gamma == 10)

    data = np.array([[1, 2, 3], [4, 5, 6], [7, 8 ,9]])
    app.setData(data)
    assert(app.getData() is data)

    spots = [(1, 2, 3), (4, 5, 6)]
    app.spots = spots
    assert(app.getSpots() is spots)

    app.setThreshold(5.7)
    assert(app.getThreshold() == 5.7)

    app.activateRemoveDuplicates()
    assert(app.shallRemoveDuplicates() == True)
    app.deactivateRemoveDuplicates()
    assert(app.shallRemoveDuplicates() == False)

    app.activateFindThreshold()
    assert(app.shallFindThreshold() == True)
    app.deactivateFindThreshold()
    assert(app.shallFindThreshold() == False)


