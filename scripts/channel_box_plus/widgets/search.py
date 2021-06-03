import difflib
from maya import cmds
from maya.api import OpenMaya
from PySide2 import QtWidgets, QtCore

from channel_box_plus import utils
from channel_box_plus.widgets import settings
from channel_box_plus.utils import CHANNEL_BOX


__all__ = [
    "SearchWidget"
]


class SearchWidget(QtWidgets.QWidget):
    """
    Create a search widget that will allow for filtering of the attributes.
    This can come in handy when working with lots of attributes and only
    wanted to work with a hand full at a time.
    """
    def __init__(self, parent):
        super(SearchWidget, self).__init__(parent)

        scale_factor = self.logicalDpiX() / 96.0
        self.setMaximumHeight(int(30 * scale_factor))

        # create settings
        self.settings = settings.SettingsDialog(self)
        self.callback = self.register_callback()

        # create layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(3, 5, 3, 5)
        layout.setSpacing(3)
        
        # create search widget
        self.edit = QtWidgets.QLineEdit(self)
        self.edit.textChanged.connect(self.reset)
        self.edit.setPlaceholderText("Search...")
        layout.addWidget(self.edit)

        # create clear widget
        button = QtWidgets.QPushButton(self)
        button.setText("x")
        button.setFlat(True)
        button.setMinimumHeight(int(20 * scale_factor))
        button.setMinimumWidth(int(20 * scale_factor))
        button.released.connect(self.edit.clear)
        layout.addWidget(button)

        # extend menu
        self.menu = utils.get_channel_box_menu()
        self.menu.addSeparator()
        action = self.menu.addAction("Colour settings")
        action.triggered.connect(self.display_dialog)

        # reset widget
        self.reset()

    # ------------------------------------------------------------------------

    def display_dialog(self):
        if self.settings.exec_():
            self.reset()

    # ------------------------------------------------------------------------

    def update_search(self, search, node):
        """
        Loop over all visible attributes and match them with the search
        string. The search string is split using and empty space and all
        elements need to match.
        
        :param str search:
        :param str node:
        """
        # reset of search string is empty
        if not search:
            cmds.channelBox(CHANNEL_BOX, edit=True, fixedAttrList=[])
            return
    
        # split match string
        matches = []
        matches_components = search.lower().split()
        
        # get matching attributes
        obj = utils.get_object(node)
        dependency = OpenMaya.MFnDependencyNode(obj)

        # get keyable and channel box attributes to match when looping over
        # all attributes. It is not possible to get this list in order and
        # the MFnAttribute.channelBox doesn't return the right result ...
        attributes = cmds.listAttr(node, keyable=True) or []
        attributes.extend(cmds.listAttr(node, channelBox=True) or [])
        attributes = set(attributes)

        for i in range(dependency.attributeCount()):
            attribute_fn = OpenMaya.MFnAttribute(dependency.attribute(i))
            attribute = attribute_fn.name
            if attribute not in attributes:
                continue

            if all([match in attribute.lower() for match in matches_components]):
                matches.append(attribute)

        # append null if not matches are found, if an empty list is provided
        # all attributes will be displayed.
        if not matches:
            matches.append("null")

        # filter channel box
        cmds.channelBox(CHANNEL_BOX, edit=True, fixedAttrList=matches)

    def update_colour(self, node):
        """
        Loop over the selected objects user defined attributes, and generate 
        a colour for them, nodeRegex is not used because it slows down the 
        displaying of the the Channel Box in scenes with many user defined 
        attributes. 
        
        :param str node:
        """
        colour_picker = utils.ColourPicker(self.settings.user_colours)
        attribute_previous = None
        attributes = cmds.listAttr(node, userDefined=True) or []

        for attribute in attributes:
            attribute_path = "{}.{}".format(node, attribute)
            is_locked = cmds.getAttr(attribute_path, lock=True)
            is_keyable = cmds.getAttr(attribute_path, keyable=True)

            if is_locked or (not is_keyable and self.settings.split_non_keyable):
                attribute_previous = None
                colour_picker.next_main()
                colour = self.settings.split_colour
            else:
                if attribute_previous is not None:
                    ratio = difflib.SequenceMatcher(None, attribute, attribute_previous).ratio()
                    if ratio < self.settings.threshold:
                        colour_picker.next_secondary()

                attribute_previous = attribute
                colour = colour_picker.colour

            cmds.channelBox(
                CHANNEL_BOX,
                edit=True,
                attrRegex=attribute,
                attrBgColor=colour
            )

    # ------------------------------------------------------------------------

    def register_callback(self):
        """
        Register a callback to run the reset function every time the
        selection list is modified.

        :return: Callback id
        :rtype: int
        """
        return OpenMaya.MModelMessage.addCallback(
            OpenMaya.MModelMessage.kActiveListModified,
            self.reset
        )

    def remove_callback(self):
        """
        Remove the callback that updates the ui every time the selection
        list is modified.
        """
        if self.callback is not None:
            OpenMaya.MMessage.remove_callback(self.callback)
            self.callback = None

    # ------------------------------------------------------------------------

    def reset(self, *args):
        """
        Update the main channel box with the input data, filter attributes
        based on the search term and colour user attributes.
        """
        search = self.edit.text()
        nodes = cmds.ls(selection=True, long=True) or []

        if nodes:
            self.update_colour(nodes[-1])
            self.update_search(search, nodes[-1])

    def deleteLater(self):
        """
        Subclass the deleteLater function to first remove the callback,
        this callback shouldn't be floating around and should be deleted
        with the widget.
        """
        self.remove_callback()
        super(SearchWidget, self).deleteLater()
