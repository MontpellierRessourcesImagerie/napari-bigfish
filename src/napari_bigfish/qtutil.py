import pyperclip
import numpy as np
from qtpy.QtWidgets import QLabel, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem, QAction
from qtpy.QtCore import Qt, QVariant
from napari.utils import notifications
from napari_bigfish.array_util import ArrayUtil


class WidgetTool:
    """
    Utility methods for working with qt-widgets.
    """

    @staticmethod
    def getLineInput(parent, labelText, defaultValue, fieldWidth, callback):
        """Returns a label displaying the given text and an input field
        with the given default value.

        :param parent: The parent widget of the label and the input field
        :param labelText: The text of the label
        :param defaultValue: The value initailly displayed in the input field
        :param fieldWidth: The width of the input field
        :param callback: A callback function with a parameter text. The function
                         is called with the new text when the content of the
                         input field changes
        :return: A tupel of the label and the input field
        :rtype: (QLabel, QLineEdit)
        """
        label = QLabel(parent)
        label.setText(labelText)
        input = QLineEdit(parent)
        input.setText(str(defaultValue))
        input.textChanged.connect(callback)
        input.setMaximumWidth(fieldWidth)
        return label, input


    @staticmethod
    def getComboInput(parent, labelText, values):
        """Returns a label displaying the given text and a combo-box
        with the given values.

        :param parent: The parent widget of the label and the input field
        :param labelText: The text of the label
        :param values: The values in the list of the combo-box
        :return: A tupel of the label and the input field
        :rtype: (QLabel, QComboBox)
        """
        label = QLabel(parent)
        label.setText(labelText)
        input = QComboBox(parent)
        input.addItems(values)
        return label, input


    @staticmethod
    def replaceItemsInComboBox(comboBox, newItems):
        """Replace the items in the combo-box with newItems

        :param comboBox: The combo-box in which the items will be replaced
        :param newItems: The new items that will replace the current items
                         in the combo-box.
        """
        selectedText = comboBox.currentText()
        comboBox.clear()
        comboBox.addItems(newItems)
        index = -1
        try:
            index = newItems.index(selectedText)
        except ValueError:
            index = -1
        if index > -1:
            comboBox.setCurrentIndex(index)



class TableView(QTableWidget):
    """ A table that allows to copy the selected cells to the system-clipboard.
    """

    def __init__(self, data, *args):
        """Create a new table from data.

        :param data: A dictionary with the column names as keys and the data
        in the columns as lists.
        """
        rows = 0
        columns = 0
        if data:
            columns = len(data)
            rows = len(list(data.values())[0])
        QTableWidget.__init__(self, rows, columns, *args)
        self.data = data
        self.__setData()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        copyAction = QAction("Copy\tCtrl+C", self)
        copyAction.triggered.connect(self.copyDataToClipboard)
        self.addAction(copyAction)


    def __setData(self):
        horHeaders = []
        for n, key in enumerate(self.data.keys()):
            horHeaders.append(key)
            for m, item in enumerate(self.data[key]):
                newitem = QTableWidgetItem(str(item))
                newitem.setTextAlignment(Qt.AlignRight)
                self.setItem(m, n, newitem)
        self.setHorizontalHeaderLabels(horHeaders)


    def keyPressEvent(self, event):
        """Copy the selected table data to the system clipboard if the key-event
        is ctrl+C.

        :param event: The received key-pressed event.
        """
        super().keyPressEvent(event)
        if event.key() == Qt.Key_C and (event.modifiers() & Qt.ControlModifier):
            self.copyDataToClipboard()


    def copyDataToClipboard(self):
        """ Copy the data in the selected table-cells into the system clipboard.
        """
        notifications.show_info("copying data to clipboard")
        tableDataAsText = self.getSelectedDataAsString()
        pyperclip.copy(tableDataAsText)


    def getSelectedDataAsString(self):
        """ Get the data in the selected cells as a string. Columns are
        separated by tabs and lines by newlines".
        """
        copied_cells = self.selectedIndexes()
        if len(copied_cells) == 0:
            return ""
        labels = [self.horizontalHeaderItem(id).text() for id in range(0, self.columnCount())];
        data = [['' for i in range(self.columnCount())] for j in range(self.rowCount())]
        for cell in copied_cells:
            data[cell.row()][cell.column()] = cell.data()
        table =  np.array(data)
        table, columnIndices, _ = ArrayUtil.stripZeroRowsAndColumns(table, zero='')
        lines = ''
        for row in table:
            lines = lines + "\t".join([str(elem) for elem in row]) + "\n"
        lines = lines[:-1]
        remainingHeadings = [labels[index] for index in columnIndices]
        result = "\t".join(remainingHeadings) + "\n" + lines
        return result