import pyperclip
import numpy as np
from qtpy.QtWidgets import QLabel, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem
from qtpy.QtCore import Qt
from napari_bigfish.array_util import ArrayUtil

class WidgetTool:


    @staticmethod
    def getLineInput(parent, labelText, defaultValue, fieldWidth, callback):
        label = QLabel(parent)
        label.setText(labelText)
        input = QLineEdit(parent)
        input.setText(str(defaultValue))
        input.textChanged.connect(callback)
        input.setMaximumWidth(fieldWidth)
        return label, input


    @staticmethod
    def getComboInput(parent, labelText, values):
        label = QLabel(parent)
        label.setText(labelText)
        input = QComboBox(parent)
        input.addItems(values)
        return label, input


    @staticmethod
    def replaceItemsInComboBox(comboBox, newItems):
        selectedText = comboBox.currentText()
        comboBox.clear()
        comboBox.addItems(newItems)
        index = comboBox.findData(selectedText)
        if index > -1:
            comboBox.setCurrentIndex(index)



class TableView(QTableWidget):


    def __init__(self, data, *args):
        QTableWidget.__init__(self, len(list(data.values())[0]),
                                    len(data), *args)
        self.data = data
        self.setData()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()


    def setData(self):
        horHeaders = []
        for n, key in enumerate(self.data.keys()):
            horHeaders.append(key)
            for m, item in enumerate(self.data[key]):
                newitem = QTableWidgetItem(str(item))
                newitem.setTextAlignment(Qt.AlignRight)
                self.setItem(m, n, newitem)
        self.setHorizontalHeaderLabels(horHeaders)


    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == Qt.Key_C and (event.modifiers() & Qt.ControlModifier):
            print("copying data to clipboard")
            tableDataAsText = self.getSelectedDataAsString()
            pyperclip.copy(tableDataAsText)


    def getSelectedDataAsString(self):
        copied_cells = self.selectedIndexes()
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