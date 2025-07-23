import sys
import time
import logging
from decimal import InvalidOperation
from time import sleep

import numpy as np
from qtpy.QtCore import QItemSelectionModel
from qtpy.QtWidgets import QFileDialog
from napari_bigfish import DetectFISHSpotsWidget, DetectFISHSpotsBatchWidget
from napari_bigfish._widget import SubtractBackgroundThread, DetectSpotsThread
from napari_bigfish._widget import DecomposeDenseRegionsThread, CountSpotsThread
from napari_bigfish._widget import BatchCountSpotsThread, Progress
from napari_bigfish._widget import ImageListWidget
from unittest.mock import MagicMock
from unittest.mock import patch
import unittest.mock as mock


def test_DetectFISHSpotsWidget(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.add_image(np.random.random((100, 100)))
    spotsWidget.onClickSubtractBackground()
    captured = capsys.readouterr()
    assert captured.out == "INFO: Running background subtraction with sigma xy = 2.3, sigma z = 0.75 on Image.\n"
    viewer.layers.selection.active = None
    spotsWidget.onClickSubtractBackground()
    captured = capsys.readouterr()
    assert captured.out == "ERROR: Subtract background needs an image!\n"


def test_DetectFISHSpotsBatchWidget(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    viewer.add_image(np.random.random((100, 100)))
    spotsWidget = DetectFISHSpotsWidget(viewer)
    batchWidget = DetectFISHSpotsBatchWidget(viewer, spotsWidget.model)
    viewer.close()


def test_OnClickBatch(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    viewer.add_image(np.random.random((100, 100)))
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    spotsWidget.onClickBatch()


def test_onClickCountSpots(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    image = np.random.random((100, 100))
    labels = np.random.randint(0, 255, size=(100, 100))
    viewer.add_image(image)
    viewer.add_labels(labels)
    spotsWidget.onClickCountSpots()
    # viewer.close()


'''
def test_onClickDecomposeDenseRegions(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    image = np.random.randint(0, 255, size=(100, 100), dtype=np.uint16)
    image[10][10] = 65535
    image[20][20] = 65535
    image[30][10] = 65535
    viewer.add_image(image)
    points = np.array([[10, 10], [20, 20], [30, 10], [13, 15], [26, 28], [31, 17]], dtype=np.int64)
    viewer.add_points(points, size=5)
    viewer.layers.selection.clear()
    viewer.layers.selection.add(viewer.layers[0])
    viewer.layers.events.inserted.disconnect()
    viewer.layers.events.removed.disconnect()
    spotsWidget.onClickDecomposeDenseRegions()
'''


def test_onClickDecomposeDenseRegionsNoImage(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    spotsWidget.onClickDecomposeDenseRegions()
    # viewer.close()

'''
def test_onClickDetectSpots(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    image = np.random.randint(0, 255, size=(100, 100), dtype=np.uint16)
    viewer.add_image(image)
    viewer.layers.selection.clear()
    viewer.layers.selection.add(viewer.layers[0])
    viewer.layers.events.inserted.disconnect()
    viewer.layers.events.removed.disconnect()
    spotsWidget.onClickDetectSpots()
    # viewer.close()
'''


def test_onClickDetectSpotsNoImage(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    spotsWidget.onClickDetectSpots()

    # viewer.close()



def test_onRemoveDuplicatesChanged(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    spotsWidget.onRemoveDuplicatesChanged(0)
    assert (spotsWidget.model.removeDuplicates == False)
    spotsWidget.onRemoveDuplicatesChanged(2)
    assert (spotsWidget.model.removeDuplicates == True)


def test_onFindThresholdChanged(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    spotsWidget.onFindThresholdChanged(0)
    assert (spotsWidget.model.shallFindThreshold() == False)
    spotsWidget.onFindThresholdChanged(2)
    assert (spotsWidget.model.shallFindThreshold() == True)



def test_sigmaChanged(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    spotsWidget.sigmaChanged(13, 4)
    assert(spotsWidget.sigmaXYInput.text() == "13")
    assert(spotsWidget.sigmaZInput.text() == "4")


def test_thresholdChanged(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    spotsWidget.thresholdChanged(14.67)
    assert(spotsWidget.thresholdInput.text() == "14.67")


def test_radiusChanged(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    spotsWidget.radiusChanged(6, 2)
    assert(spotsWidget.radiusXYInput.text() == "6")
    assert(spotsWidget.radiusZInput.text() == "2")


def test_removeDuplicatesChanged(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    spotsWidget.removeDuplicatesChanged(False)
    assert(not spotsWidget.removeDuplicatesCheckbox.isChecked())
    spotsWidget.removeDuplicatesChanged(True)
    assert(spotsWidget.removeDuplicatesCheckbox.isChecked())


def test_findThresholdChanged(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    spotsWidget.findThresholdChanged(False)
    assert(not spotsWidget.findThresholdCheckbox.isChecked())
    spotsWidget.findThresholdChanged(True)
    assert(spotsWidget.findThresholdCheckbox.isChecked())


def test_updateSigmaXY(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    assert(spotsWidget.updateSigmaXY("3.2"))
    assert(spotsWidget.model.sigmaXY == 3.2)
    assert(not spotsWidget.updateSigmaXY("a.b"))
    assert(spotsWidget.model.sigmaXY == 3.2)


def test_updateSigmaZ(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    assert(spotsWidget.updateSigmaZ("1.1"))
    assert(spotsWidget.model.sigmaZ == 1.1)
    assert(not spotsWidget.updateSigmaZ("a.b"))
    assert(spotsWidget.model.sigmaZ == 1.1)


def test_updateThreshold(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    assert(spotsWidget.updateThreshold("15.54"))
    assert(spotsWidget.model.threshold == 15.54)
    assert(not spotsWidget.updateThreshold("a.b"))
    assert(spotsWidget.model.threshold == 15.54)


def test_updateRadiusXY(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    assert(spotsWidget.updateRadiusXY("9"))
    assert(spotsWidget.model.radiusXY == 9)
    assert(not spotsWidget.updateRadiusXY("a.b"))
    assert(spotsWidget.model.radiusXY == 9)


def test_updateRadiusZ(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    assert(spotsWidget.updateRadiusZ("3"))
    assert(spotsWidget.model.radiusZ == 3)
    assert(not spotsWidget.updateRadiusZ("a.b"))
    assert(spotsWidget.model.radiusZ == 3)


def test_updateDecomposeRadiusXY(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    assert(spotsWidget.updateDecomposeRadiusXY("9"))
    assert(spotsWidget.model.decomposeRadiusXY == 9)
    assert(not spotsWidget.updateDecomposeRadiusXY("a.b"))
    assert(spotsWidget.model.decomposeRadiusXY == 9)


def test_updateDecomposeRadiusZ(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    assert(spotsWidget.updateDecomposeRadiusZ("3"))
    assert(spotsWidget.model.decomposeRadiusZ == 3)
    assert(not spotsWidget.updateDecomposeRadiusZ("a.b"))
    assert(spotsWidget.model.decomposeRadiusZ == 3)


def test_updateAlpha(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    assert(spotsWidget.updateAlpha("0.67"))
    assert(spotsWidget.model.alpha == 0.67)
    assert(not spotsWidget.updateAlpha("a.b"))
    assert(spotsWidget.model.alpha == 0.67)


def test_updateBeta(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    assert(spotsWidget.updateBeta("6"))
    assert(spotsWidget.model.beta == 6)
    assert(not spotsWidget.updateBeta("a.b"))
    assert(spotsWidget.model.beta == 6)


def test_updateGamma(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    assert(spotsWidget.updateGamma("39"))
    assert(spotsWidget.model.gamma == 39)
    assert(not spotsWidget.updateGamma("a.b"))
    assert(spotsWidget.model.gamma == 39)


def test_addSpotCountingTable(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    spotsWidget.spotsName = "my spots"
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    aTable = {"name": ["Baecker", "Drewsen"], "first name": ["Volker", "Kenneth"]}
    spotsWidget.addSpotCountingTable(aTable)


def test_threadRemoveBackground(make_napari_viewer):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    image = np.random.random((100, 100))
    viewer.add_image(image)

    thread = SubtractBackgroundThread(spotsWidget.model, image, viewer, "/a/b/c/image1.tif", (340, 340, 1090), None, None)
    result = thread.removeBackground()
    assert(result.shape == image.shape)


def test_threadDetectSpots(make_napari_viewer):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    image = np.random.random((100, 100))
    viewer.add_image(image)
    thread = DetectSpotsThread(spotsWidget.model, image, viewer, "/a/b/c/image1.tif", (340, 340, 1090), 5)
    result = thread.detectSpots()
    assert(len(result)>0)


'''
def test_threadDecomposeDenseRegions(make_napari_viewer):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    image = np.random.randint(0, 255, size=(255, 255), dtype=np.uint16)
    viewer.add_image(image)
    spots = np.array([[10, 10], [20, 20], [30, 10], [13, 15], [26, 28], [31, 17]], dtype=np.int64)
    numberOfDetectedSpots = len(spots)
    spotsWidget.model.spots = spots
    thread = DecomposeDenseRegionsThread(spotsWidget.model, image, viewer, "/a/b/c/image1.tif", (340, 340, 1090), 5)
    result = thread.decompose()
    assert(len(result)>=numberOfDetectedSpots)
'''


def test_threadCountSpots(make_napari_viewer):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    image = np.random.randint(0, 255, size=(255, 255), dtype=np.uint16)
    cellLabels = np.zeros((255, 255), dtype=np.uint16)
    nucleiMask = np.zeros((255, 255), dtype=np.uint16)
    viewer.add_image(image)
    viewer.add_labels(cellLabels)
    spots = np.array([[10, 10], [20, 20], [30, 10], [13, 15], [26, 28], [31, 17]], dtype=np.int64)
    headings = ["image", "cell", "spots in cytoplasm", "spots in nucleus",
                "spots in cell"]
    thread = CountSpotsThread(spotsWidget.model, spotsWidget, spots, "my-spots", cellLabels, nucleiMask, headings)
    table = thread.countSpots()
    assert(table["spots in cell"][0] == len(spots))


@mock.patch('skimage.io.imread')
@mock.patch('os.makedirs')
def test_threadBatchCountSpots(mockMakedirs, mockImread, make_napari_viewer, capsys):
    mockImread.return_value = np.random.randint(0, 255, size=(255, 255, 2), dtype=np.uint16)
    scale = (300, 300, 1000)
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    inputImages = ["/a/b/i/i1.tif", "/a/b/i/i2.tif"]
    cellLabels = ["/a/b/l/l1.tif", "/a/b/l/l2.tif"]
    nucleiMasks = ["/a/b/l/m1.tif", "/a/b/l/m2.tif"]
    mock.patch('os.path.exists', return_value = True)
    mock_open = mock.mock_open()
    with mock.patch('builtins.open', mock_open):
        thread = BatchCountSpotsThread(scale, spotsWidget.model, inputImages, cellLabels, nucleiMasks,
                                       subtractBackground=True, decomposeDenseRegions=False)
        result = thread.batchCountSpots()
        assert(result is thread)


def test_Progress():
    progress = Progress(None, 100, "Testing progress")
    progress.progressChanged(50, 100)
    progress.progressChanged(100, 100)
    progress.processFinished()


def test_detectFISHSpotsBatchWidget3D(make_napari_viewer):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    image = np.random.randint(0, 255, size=(255, 255, 2), dtype=np.uint16)
    viewer.add_image(image)
    spotsWidget.onClickBatch()


def test_detectFISHSpotsBatchWidget_onLayerLoaded(make_napari_viewer):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    image = np.random.randint(0, 255, size=(255, 255, 2), dtype=np.uint16)
    viewer.add_image(image)
    spotsWidget.onClickBatch()
    spots = np.array([[10, 10, 10], [20, 20, 20]], dtype=np.int64)
    viewer.add_points(spots)


def test_detectFISHSpotsBatchWidget_updateScaleXY(make_napari_viewer):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    batchSpotsWidget = DetectFISHSpotsBatchWidget(viewer, spotsWidget.model)
    viewer.window.add_dock_widget(batchSpotsWidget, area='right',
                                       name="batch FISH-spot Detection",
                                       tabify = False)
    assert(batchSpotsWidget.updateScaleXY("330"))
    assert(batchSpotsWidget.scaleXY == 330)
    assert(not batchSpotsWidget.updateScaleXY("abc"))
    assert(batchSpotsWidget.scaleXY == 330)


def test_detectFISHSpotsBatchWidget_updateScaleZ(make_napari_viewer):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    batchSpotsWidget = DetectFISHSpotsBatchWidget(viewer, spotsWidget.model)
    viewer.window.add_dock_widget(batchSpotsWidget, area='right',
                                       name="batch FISH-spot Detection",
                                       tabify = False)
    assert(batchSpotsWidget.updateScaleZ("990"))
    assert(batchSpotsWidget.scaleZ == 990)
    assert(not batchSpotsWidget.updateScaleZ("abc"))
    assert(batchSpotsWidget.scaleZ == 990)


def test_detectFISHSpotsBatchWidget_onSubtractBackgroundChanged(make_napari_viewer):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    batchSpotsWidget = DetectFISHSpotsBatchWidget(viewer, spotsWidget.model)
    viewer.window.add_dock_widget(batchSpotsWidget, area='right',
                                       name="batch FISH-spot Detection",
                                       tabify = False)
    batchSpotsWidget.onSubtractBackgroundChanged(0)
    assert(not batchSpotsWidget.subtractBackground)
    batchSpotsWidget.onSubtractBackgroundChanged(2)
    assert(batchSpotsWidget.subtractBackground)


def test_detectFISHSpotsBatchWidget_onDecomposeChanged(make_napari_viewer):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    batchSpotsWidget = DetectFISHSpotsBatchWidget(viewer, spotsWidget.model)
    viewer.window.add_dock_widget(batchSpotsWidget, area='right',
                                       name="batch FISH-spot Detection",
                                       tabify = False)
    batchSpotsWidget.onDecomposeChanged(0)
    assert(not batchSpotsWidget.decomposeDenseRegions)
    batchSpotsWidget.onDecomposeChanged(2)
    assert(batchSpotsWidget.decomposeDenseRegions)


def test_detectFISHSpotsBatchWidget_runBatch(make_napari_viewer):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    batchSpotsWidget = DetectFISHSpotsBatchWidget(viewer, spotsWidget.model)
    viewer.window.add_dock_widget(batchSpotsWidget, area='right',
                                       name="batch FISH-spot Detection",
                                       tabify = False)
    batchSpotsWidget.runBatch()


@mock.patch.object(QFileDialog, 'getOpenFileNames')
def test_ImageListWidget(mock_filenames):
    mock_filenames.return_value = (["a/b/c/c_img.tif", "a/b/c/a_img.tif", "a/b/c/b_img.tif"], ".tif")
    imageList = ImageListWidget("images")
    assert('*.tif' in imageList.getFileExtensions())
    imageList.onClickAddFiles()
    assert(imageList.getValues()[0] == "a/b/c/a_img.tif")
    assert(len(imageList.getValues()) == 3)

    ix = imageList.model.index(0, 0)
    sm = imageList.listView.selectionModel()
    sm.select(ix, QItemSelectionModel.Select)
    imageList.deleteSelection()
    assert(imageList.getValues()[0] == "a/b/c/b_img.tif")
    assert(len(imageList.getValues()) == 2)

    imageList.onClickClearFiles()
    assert(len(imageList.getValues()) == 0)

