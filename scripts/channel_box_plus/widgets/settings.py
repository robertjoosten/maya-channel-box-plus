from PySide2 import QtWidgets, QtGui, QtCore


__all__ = [
    "SettingsDialog"
]

SPLIT_COLOUR_DEFAULT = [0.150, 0.150, 0.150]
USER_COLOURS_DEFAULT = [
    [
        [0.764, 0.266, 0.266],
        [0.662, 0.168, 0.168],
        [0.564, 0.086, 0.086],
        [0.466, 0.007, 0.007],
    ],
    [
        [0.301, 0.662, 0.168],
        [0.211, 0.564, 0.086],
        [0.129, 0.466, 0.007],
        [0.054, 0.364, 0.000],
    ],
    [
        [0.266, 0.301, 0.764],
        [0.168, 0.203, 0.662],
        [0.086, 0.117, 0.564],
        [0.007, 0.039, 0.466],
    ],
    [
        [0.764, 0.266, 0.701],
        [0.662, 0.168, 0.600],
        [0.564, 0.086, 0.501],
        [0.466, 0.007, 0.403],
    ],
]


class SettingsDialog(QtWidgets.QDialog):
    """
    Creates a settings widget that will allow for the changes of settings that
    will update the appearance of the colour information.
    """
    def __init__(self, parent):
        super(SettingsDialog, self).__init__(parent)

        scale_factor = self.logicalDpiX() / 96.0
        self.setMinimumWidth(int(400 * scale_factor))
        self.setWindowTitle("CB+ Colour settings")
        self.setWindowIcon(QtGui.QIcon(":/channelBox.png"))

        # create settings
        self.settings = QtCore.QSettings("channel_box_plus.ini", QtCore.QSettings.IniFormat)
        self.settings.setFallbacksEnabled(False)

        # create layout
        layout = QtWidgets.QGridLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)

        # create threshold
        threshold_label = QtWidgets.QLabel(self)
        threshold_label.setText("Threshold:")
        layout.addWidget(threshold_label, 0, 0)

        self._threshold = QtWidgets.QDoubleSpinBox(self)
        self._threshold.setRange(0, 1)
        self._threshold.setDecimals(2)
        self._threshold.setSingleStep(0.05)
        layout.addWidget(self._threshold, 0, 1)

        # create keyable split
        split_label = QtWidgets.QLabel(self)
        split_label.setText("Split non-keyable:")
        layout.addWidget(split_label, 1, 0)

        self._split_non_keyable = QtWidgets.QCheckBox(self)
        layout.addWidget(self._split_non_keyable, 1, 1)

        # set stretch
        layout.setRowStretch(2, 100)

        # create apply
        apply = QtWidgets.QPushButton(self)
        apply.setText("Apply")
        apply.released.connect(self.apply)
        layout.addWidget(apply, 3, 0, 1, 2)

    # ------------------------------------------------------------------------

    @property
    def threshold(self):
        """
        :return: Threshold
        :rtype: float
        """
        try:
            return self.settings.value("threshold", 0.75, type=float)
        except TypeError:
            return float(self.settings.value("threshold", 0.75))

    @property
    def split_non_keyable(self):
        """
        :return: Split non-keyable attributes
        :rtype: bool
        """
        try:
            # for some reason using type=bool errors in py2
            return bool(self.settings.value("split_non_keyable", False, type=int))
        except TypeError:
            return bool(self.settings.value("split_non_keyable", False))

    @property
    def split_colour(self):
        """
        :return: Split non-keyable attributes
        :rtype: list
        """
        return SPLIT_COLOUR_DEFAULT

    @property
    def user_colours(self):
        """
        :return: User colours
        :rtype: list
        """
        return USER_COLOURS_DEFAULT

    # ------------------------------------------------------------------------

    def apply(self):
        self.settings.setValue("threshold", self._threshold.value())
        self.settings.setValue("split_non_keyable", self._split_non_keyable.isChecked())
        self.settings.sync()
        self.accept()

    def exec_(self):
        self._threshold.setValue(self.threshold)
        self._split_non_keyable.setChecked(self.split_non_keyable)
        return super(SettingsDialog, self).exec_()
