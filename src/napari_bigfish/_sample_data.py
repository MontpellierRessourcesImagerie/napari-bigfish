"""
This module is an example of a barebones sample data provider for napari.

It implements the "sample data" specification.
see: https://napari.org/stable/plugins/guides.html?#sample-data

Replace code below according to your needs.
"""
from __future__ import annotations

import numpy
from skimage import io

def make_sample_data():
    """Download and return a sample image for the napari-bigfish plugin. The
    dataset has three layers, one image layer with the FISH-spots, one
    artificially constructed labels-layer, representing cells and one also
    artificially constructed labels layer, representing the nuclei.
    """
    scale = (1000, 108.3424, 108.3424)
    image = io.imread('https://dev.mri.cnrs.fr/attachments/download/2909/3C-02_decon_ch01-1.tif')
    data = numpy.array(image)
    cellLabelsImage = io.imread('https://dev.mri.cnrs.fr/attachments/download/2911/3C-01_decon_ch00-lbl-1.tif')
    cellLabels = numpy.array(cellLabelsImage)
    nucleiLabelsImage = io.imread('https://dev.mri.cnrs.fr/attachments/download/2910/3C-01_decon_ch02-lbl-nuclei.tif')
    nucleiLabels = numpy.array(nucleiLabelsImage)

    return [(data,
             {'scale': scale,
              'name': 'spots (bigfish example image)'}),
            (cellLabels,
             {'scale': scale,
              'name': 'cell labels (bigfish example image)'},
              "labels"),
            (nucleiLabels,
             {'scale': scale,
              'name': 'nuclei labels (bigfish example image)'},
              "labels")
           ]
