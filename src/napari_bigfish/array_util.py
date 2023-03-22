import numpy as np



class ArrayUtil:
    '''A class to provide utils that do common operations on arrays.'''


    @staticmethod
    def stripZeroRowsAndColumns(data, zero=0):
        '''Return an array with all-zero rows and columns removed.

        Returns a stripped array, with all rows and columns, in which each
        element is zero, removed. Instead of rows and comumns with all zero
        elements rows and columns containing another number, string or
        object at each position can be removed from the array.

        Parameters
        ----------
            data: numpy.ndarray
                A table from which empty rows and columns will be stripped
            zero: The element for which rows and columns will be removed

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