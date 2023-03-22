import numpy as np
from napari_bigfish.array_util import ArrayUtil

def testArrayUtil():
    matrix = np.array([[1, 0, 3], [0, 0, 0], [2, 0, 4]])
    result, colIndices, rowIndices = ArrayUtil.stripZeroRowsAndColumns(matrix)
    assert(result.shape == (2, 2))
    assert(colIndices[0] == 0)
    assert(colIndices[1] == 2)
    assert(rowIndices[0] == 0)
    assert(rowIndices[1] == 2)