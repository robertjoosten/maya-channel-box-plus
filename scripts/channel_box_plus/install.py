import logging
from maya import cmds

from channel_box_plus import widgets
from channel_box_plus import utils


log = logging.getLogger(__name__)
MAYA_VERSION = int(cmds.about(version=True))


def execute():
    """
    Add the search interface and colouring functionality to Maya's main
    channel box. If channelBoxPlus is already installed a RuntimeError
    exception will be thrown. A threshold can be set, this threshold
    determines when the attributes should change colour. the higher the
    threshold the more the 2 attributes will have to match up to stay the
    same colour.

    In Maya 2022 and above the layout of the channel box is different which
    breaks the table views when adding the search widget. For this reason it
    is omitted for Maya 2022.

    :raises RuntimeError: When the channel box plus is already installed.
    """
    # get widgets
    channel_box = utils.get_channel_box()
    parent = channel_box.parent()
    parent_layout = parent.layout()
    parent_layout.setSpacing(0)
    parent_layout_count = parent_layout.count()

    # validate search widget
    for i in range(parent_layout.count()):
        item = parent_layout.itemAt(i)
        if isinstance(item.widget(), widgets.SearchWidget):
            raise RuntimeError("channel-box-plus has already been installed.")

    # initialize search widget
    search_widget = widgets.SearchWidget(parent)

    if parent_layout_count and MAYA_VERSION < 2022:
        item = parent_layout.takeAt(0)
        parent_layout.addWidget(search_widget)
        parent_layout.addItem(item)
    else:
        parent_layout.addWidget(search_widget)

    log.info("channel-box-plus installed successfully.")
