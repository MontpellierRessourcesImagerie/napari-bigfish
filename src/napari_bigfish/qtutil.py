from qtpy.QtWidgets import QLabel, QLineEdit, QComboBox

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