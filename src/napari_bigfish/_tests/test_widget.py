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


