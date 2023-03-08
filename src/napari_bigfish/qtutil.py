import pyperclip
from qtpy.QtWidgets import QLabel, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem
from qtpy.QtCore import Qt


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
        QTableWidget.__init__(self, len(list(data.values())[0]), len(data), *args)
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
            copied_cells = self.selectedIndexes()
            lines = ''
            lastRow = copied_cells[0].row()
            for cell in copied_cells:
                currentRow = cell.row()
                if lastRow != currentRow:
                    lines = lines[:-1]
                    lines = lines + "\n"
                lastRow = currentRow
                lines = lines + cell.data() + "\t"
            if len(lines) > 0:
                lines = lines[:-1]
                lines = lines + "\n"
            pyperclip.copy(lines)

