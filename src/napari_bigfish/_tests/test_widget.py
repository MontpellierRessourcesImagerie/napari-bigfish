import numpy as np

from napari_bigfish import DetectFISHSpotsWidget


# make_napari_viewer is a pytest fixture that returns a napari viewer object
# capsys is a pytest fixture that captures stdout and stderr output streams
def test_example_q_widget(make_napari_viewer, capsys):
    # make viewer and add an image layer using our fixture
    viewer = make_napari_viewer()
    viewer.add_image(np.random.random((100, 100)))

    # create our widget, passing in the viewer
    my_widget = DetectFISHSpotsWidget(viewer)

    # call our widget method
    my_widget.onClickSubtractBackground()

    # read captured output and check that it's as we expected
    captured = capsys.readouterr()
    assert captured.out == "INFO: Running background subtraction with sigma xy = 2.3, sigma z = 0.75 on Image.\n"



