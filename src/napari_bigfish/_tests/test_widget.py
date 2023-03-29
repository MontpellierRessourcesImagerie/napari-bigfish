import numpy as np

from napari_bigfish import DetectFISHSpotsWidget, DetectFISHSpotsBatchWidget


def test_DetectFISHSpotsWidget(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    viewer.add_image(np.random.random((100, 100)))
    spotsWidget = DetectFISHSpotsWidget(viewer)
    spotsWidget.onClickSubtractBackground()
    captured = capsys.readouterr()
    assert captured.out == "INFO: Running background subtraction with sigma xy = 2.3, sigma z = 0.75 on Image.\n"


def test_DetectFISHSpotsBatchWidget(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    viewer.add_image(np.random.random((100, 100)))
    spotsWidget = DetectFISHSpotsWidget(viewer)
    batchWidget = DetectFISHSpotsBatchWidget(viewer, spotsWidget.model)


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


def test_onClickDecomposeDenseRegions(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    spotsWidget = DetectFISHSpotsWidget(viewer)
    viewer.window.add_dock_widget(spotsWidget, area='right',
                                       name="FISH-spot Detection",
                                       tabify = False)
    image = np.random.random((100, 100))
    labels = np.random.randint(0, 255, size=(100, 100), dtype=np.uint8)
    viewer.add_image(image)
    viewer.add_labels(labels)
    # add spots layer
    spotsWidget.onClickCountSpots()
    # spotsWidget.onClickDecomposeDenseRegions()
