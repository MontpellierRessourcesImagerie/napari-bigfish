import pyperclip
from qtpy.QtCore import Qt, QEvent
from qtpy.QtGui import QKeyEvent
from qtpy.QtWidgets import QWidget
from napari_bigfish.qtutil import WidgetTool, TableView


def doNothing():
    pass

def testGetLineInput():
    parent = QWidget()
    doNothing()
    label, input = WidgetTool.getLineInput(parent,
                                           "enter a number: ",
                                           5,
                                           50,
                                           doNothing
                                           )
    assert(str(label.text()) == "enter a number: ")
    assert(input.text() == "5")


def testGetComboInput():
    parent = QWidget()

    label, combo = WidgetTool.getComboInput(parent,
                                           "select a flavour: ",
                                           ["strawberry", "vanille", "chocolate"]
                                           )
    assert(str(label.text()) == "select a flavour: ")
    assert(combo.count()==3)


def testReplaceItemsInCombo():
    parent = QWidget()

    label, combo = WidgetTool.getComboInput(parent,
                                           "select a flavour: ",
                                           ["strawberry", "vanille", "chocolate"]
                                           )
    combo.setCurrentIndex(0)
    WidgetTool.replaceItemsInComboBox(combo, ["strawberry", "peach", "stracciatella"])
    assert(combo.itemText(1) == "peach")
    assert(combo.count()==3)


def testCopyDataToClipboard():
    pyperclip.copy("")
    data = {"name": ["smith", "drew"], "firstname": ["john", "kenneth"]}
    tableWidget = TableView(data)
    tableWidget.selectAll()
    tableWidget.copyDataToClipboard()
    s = pyperclip.paste()
    lines = s.split("\n")
    assert(lines[0].startswith("name\tfirstname"))
    assert(lines[1].startswith("smith\tjohn"))
    assert(lines[2].startswith("drew\tkenneth"))


def testKeyPressEvent():
    pyperclip.copy("")
    data = {"name": ["smith", "drew"], "firstname": ["john", "kenneth"]}
    tableWidget = TableView(data)
    tableWidget.selectAll()
    event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key_C, Qt.ControlModifier)
    tableWidget.keyPressEvent(event)
    s = pyperclip.paste()
    lines = s.split("\n")
    assert(lines[0].startswith("name\tfirstname"))
    assert(lines[1].startswith("smith\tjohn"))
    assert(lines[2].startswith("drew\tkenneth"))

def testKeyPressEventNoSelection():
    pyperclip.copy("")
    data = {"name": ["smith", "drew"], "firstname": ["john", "kenneth"]}
    tableWidget = TableView(data)
    event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key_C, Qt.ControlModifier)
    tableWidget.keyPressEvent(event)
    s = pyperclip.paste()
    assert(s == "")