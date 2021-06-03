import logging
from PySide2 import QtWidgets

from channel_box_plus import widgets
from channel_box_plus import utils


log = logging.getLogger(__name__)


def execute():
    """
    Add the search interface and colouring functionality to Maya's main
    channel box. If channelBoxPlus is already installed a RuntimeError
    exception will be thrown. A threshold can be set, this threshold
    determines when the attributes should change colour. the higher the
    threshold the more the 2 attributes will have to match up to stay the
    same colour.

    :raises RuntimeError: When the channel box plus is already installed.
    """
    # get widgets
    channel_box = utils.get_channel_box()
    parent = channel_box.parent()
    parent_layout = parent.layout()
    parent_layout.setSpacing(0)

    # validate search widget
    for i in range(parent_layout.count()):
        item = parent_layout.itemAt(0)
        if isinstance(item.widget(), widgets.SearchWidget):
            raise RuntimeError("channel-box-plus has already been installed.")

    # initialize search widget
    search_widget = widgets.SearchWidget(parent)

    # add search widget to layout
    if isinstance(parent_layout, QtWidgets.QLayout):
        item = parent_layout.itemAt(0)
        widget = item.widget()
        parent_layout.removeWidget(widget)
        parent_layout.addWidget(search_widget)
        parent_layout.addWidget(widget)
    else:
        parent_layout.insertWidget(0, search_widget)

    log.info("channel-box-plus installed successfully.")