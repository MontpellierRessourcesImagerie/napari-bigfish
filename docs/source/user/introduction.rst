Introduction
============
.. image:: https://dev.mri.cnrs.fr/attachments/download/2941/napari_bigfish.png
    :alt: the napari-bigfish plugin

Napari-Bigfish is a `plugin <https://napari.org/stable/plugins/find_and_install_plugin.html>`_ for the multi-dimensional image viewer `napari <https://napari.org/stable/>`_. It provides an alternative graphical user interface to parts of the `Big-FISH <https://github.com/fish-quant/big-fish>`_ python package. `Big-FISH <https://github.com/fish-quant/big-fish>`_ is a python package for the analysis of smFISH images. 
The parts currently available via the plugin are:

 * `Gaussian Background Removal <https://big-fish.readthedocs.io/en/stable/stack/preprocessing.html#bigfish.stack.remove_background_gaussian>`_
 * `Automated Spot Detection <https://big-fish.readthedocs.io/en/stable/detection/spots.html#bigfish.detection.detect_spots>`_

   * minimum spot distance
   * removal of duplicates
   * auto-threshold detection
 * `Dense Region Decomposition <https://big-fish.readthedocs.io/en/stable/detection/dense.html#bigfish.detection.decompose_dense>`_
 * Counting of spots per cell and category cytoplasm/nucleus (not from bigfish)
 * Batch-Processing
