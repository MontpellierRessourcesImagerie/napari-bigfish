import numpy as np



class ArrayUtil:

    @staticmethod
    def stripZeroRowsAndColumns(data, zero="0"):
        '''Return an array with all-zero rows and columns removed.

        Returns a stripped array, with all rows and columns, in which each
        element is zero, removed.

        Parameters
        ----------
            data: numpy.ndarray
                A table from which empty rows and columns will be stripped
        Return
        ----------
            stripped: numpy.ndarray
                The input array data with all-zero rows and columns removed
            columnIndices: numpy.ndarray
                A 1D array of the indices of the columns that are not all zero
                in the input array
            rowIndices: numpy.ndarray
                A 1D array of the indices of the rows that are not all zero
                in the input array

        '''
        rowIndices = np.where(~np.all(data == zero, axis=1))[0]
        stripped = data[~np.all(data == zero, axis=1)]
        stripped = np.array(list(zip(*stripped)))
        columnIndices = np.where(~np.all(stripped == zero, axis=1))[0]
        stripped = stripped[~np.all(stripped == zero, axis=1)]
        stripped = np.array(list(zip(*stripped)))
        return stripped, columnIndices, rowIndices