import sys
from napari_bigfish._tests.surrogate.surrogate import surrogate

from napari_bigfish.bigfishapp import BigfishApp
from unittest.mock import MagicMock
from unittest.mock import patch



def testRunBatchEmpty():
    app = BigfishApp()
    app.setProgressMax(10)
    app.runBatch((1, 1, 3), [])
    assert(app.progressMax == 0)

'''
@surrogate('os.path')
def testRunBatch():
    app = BigfishApp()
    app.setProgressMax(10)
    app.runBatch((1, 1, 3), ["a", "b"])
    assert(app.progressMax == 0)
'''