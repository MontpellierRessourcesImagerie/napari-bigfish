import sys
import time
import numpy as np
from napari_bigfish import DetectFISHSpotsWidget, DetectFISHSpotsBatchWidget
from napari_bigfish._widget import SubtractBackgroundThread, DetectSpotsThread
import logging

def test_DetectFISHSpotsWidget(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    viewer.add_image(np.random.random((100, 100)))
    spotsWidget = DetectFISHSpotsWidget(viewer)
    spotsWidget.onClickSubtractBackground()
    captured = capsys.readouterr()
    assert captured.out == "INFO: Running background subtraction with sigma xy = 2.3, sigma z = 0.75 on Image.\n"
    viewer.layers.selection.active = None
    spotsWidget.onClickSubtractBackground()
    viewer.close()


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
    viewer.close()


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
    viewer.close()


def test_onClickDecomposeDenseRegions(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    image = np.random.randint(0, 255, size=(100, 100), dtype=np.uint16)
    viewer.add_image(image)
    points = np.array([[10, 10], [20, 20], [30, 10], [13, 15], [26, 28], [31, 17]], dtype=np.int64)
    viewer.add_points(points, size=5)
    viewer.layers.selection.clear()
    viewer.layers.selection.add(viewer.layers[0])
    viewer.layers.events.inserted.disconnect()
    viewer.layers.events.removed.disconnect()
    spotsWidget.onClickDecomposeDenseRegions()
    viewer.close()


def test_onClickDecomposeDenseRegionsNoImage(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    spotsWidget.onClickDecomposeDenseRegions()
    viewer.close()


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
    viewer.close()



def test_onClickDetectSpotsNoImage(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    spotsWidget.onClickDetectSpots()
    viewer.close()


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