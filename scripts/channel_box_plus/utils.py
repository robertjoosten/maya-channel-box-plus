import shiboken2
from six import integer_types
from maya import mel
from maya import OpenMayaUI
from maya.api import OpenMaya
from PySide2 import QtWidgets, QtCore


CHANNEL_BOX = "mainChannelBox"


def get_object(node):
    """
    :param str node:
    :return: Maya object node
    :rtype: OpenMaya.MObject
    """
    sel = OpenMaya.MSelectionList()
    sel.add(node)
    return sel.getDependNode(0)


# ----------------------------------------------------------------------------


def maya_to_qt(name):
    """
    :param str name: Maya path of an ui object
    :return: QWidget of parsed Maya path
    :rtype: QWidget
    :raise RuntimeError: When no handle could be obtained
    """
    ptr = OpenMayaUI.MQtUtil.findControl(name)
    if ptr is None:
        ptr = OpenMayaUI.MQtUtil.findLayout(name)
    if ptr is None:
        ptr = OpenMayaUI.MQtUtil.findMenuItem(name)
    if ptr is not None:
        ptr = integer_types[-1](ptr)
        return shiboken2.wrapInstance(ptr, QtWidgets.QWidget)

    raise RuntimeError("Failed to obtain a handle to '{}'.".format(name))


def qt_to_maya(widget):
    """
    :param QWidget widget: QWidget of a maya ui object
    :return: Maya path of parsed QWidget
    :rtype: str
    """
    ptr = shiboken2.getCppPointer(widget)[0]
    ptr = integer_types[-1](ptr)
    return OpenMayaUI.MQtUtil.fullName(ptr)


# ----------------------------------------------------------------------------


def get_channel_box():
    """
    :return: Maya's main channel box
    :rtype: QtWidget.QWidget
    """
    channel_box = maya_to_qt(CHANNEL_BOX)
    return channel_box


def get_channel_box_menu():
    """
    :return: Maya's main channel box menu
    :rtype: QtWidgets.QMenu
    :raise RuntimeError: When menu cannot be found.
    """
    channel_box = get_channel_box()

    for child in channel_box.children():
        if isinstance(child, QtWidgets.QMenu):
            mel.eval("generateChannelMenu {} 1".format(qt_to_maya(child)))
            return child

    raise RuntimeError("No menu found in channel box widget.")


# ----------------------------------------------------------------------------


class ColourPicker(object):
    def __init__(self, data):
        self._data = data
        self._main = 0
        self._secondary = 0

    # ------------------------------------------------------------------------

    @property
    def colour(self):
        """
        :return: Colour
        :rtype: list[float]
        """
        return self._data[self._main][self._secondary]

    # ------------------------------------------------------------------------

    def next_main(self):
        self._main += 1
        if self._main == len(self._data):
            self._main = 0

    def next_secondary(self):
        self._secondary += 1
        if self._secondary == len(self._data[self._main]):
            self._secondary = 0

