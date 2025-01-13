# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QSizePolicy,
    QSpinBox,
    QWidget,
)


class Ui_SETTINGS(object):
    def setupUi(self, SETTINGS):
        if not SETTINGS.objectName():
            SETTINGS.setObjectName("SETTINGS")
        SETTINGS.resize(440, 220)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SETTINGS.sizePolicy().hasHeightForWidth())
        SETTINGS.setSizePolicy(sizePolicy)
        SETTINGS.setMinimumSize(QSize(440, 220))
        SETTINGS.setMaximumSize(QSize(440, 220))
        self.SETTINGS_DIAG = QDialogButtonBox(SETTINGS)
        self.SETTINGS_DIAG.setObjectName("SETTINGS_DIAG")
        self.SETTINGS_DIAG.setGeometry(QRect(260, 180, 161, 32))
        self.SETTINGS_DIAG.setOrientation(Qt.Orientation.Horizontal)
        self.SETTINGS_DIAG.setStandardButtons(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok
        )
        self.PORT_IN = QComboBox(SETTINGS)
        self.PORT_IN.setObjectName("PORT_IN")
        self.PORT_IN.setGeometry(QRect(110, 13, 321, 32))
        self.PORT_IN.setMouseTracking(True)
        self.PORT_IN.setTabletTracking(True)
        self.PORT_IN.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.PORT_IN.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.PORT_IN_T = QLabel(SETTINGS)
        self.PORT_IN_T.setObjectName("PORT_IN_T")
        self.PORT_IN_T.setGeometry(QRect(20, 20, 91, 16))
        self.PORT_IN_T.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.PORT_IN_T.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.PORT_OUT = QComboBox(SETTINGS)
        self.PORT_OUT.setObjectName("PORT_OUT")
        self.PORT_OUT.setGeometry(QRect(110, 43, 321, 32))
        self.PORT_OUT.setMouseTracking(True)
        self.PORT_OUT.setTabletTracking(True)
        self.PORT_OUT.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.PORT_OUT.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.PORT_OUT_T = QLabel(SETTINGS)
        self.PORT_OUT_T.setObjectName("PORT_OUT_T")
        self.PORT_OUT_T.setGeometry(QRect(20, 50, 91, 16))
        self.PORT_OUT_T.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.PORT_OUT_T.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.CHANNEL = QSpinBox(SETTINGS)
        self.CHANNEL.setObjectName("CHANNEL")
        self.CHANNEL.setGeometry(QRect(117, 77, 51, 22))
        self.CHANNEL.setMouseTracking(True)
        self.CHANNEL.setTabletTracking(True)
        self.CHANNEL.setMinimum(1)
        self.CHANNEL.setMaximum(16)
        self.CHANNEL_T = QLabel(SETTINGS)
        self.CHANNEL_T.setObjectName("CHANNEL_T")
        self.CHANNEL_T.setGeometry(QRect(20, 80, 91, 16))
        self.CHANNEL_T.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.CHANNEL_T.setLocale(QLocale(QLocale.English, QLocale.UnitedKingdom))
        self.OPT_SEND_BUFFER = QCheckBox(SETTINGS)
        self.OPT_SEND_BUFFER.setObjectName("OPT_SEND_BUFFER")
        self.OPT_SEND_BUFFER.setGeometry(QRect(20, 120, 251, 20))
        self.OPT_DUMP_SAVE = QCheckBox(SETTINGS)
        self.OPT_DUMP_SAVE.setObjectName("OPT_DUMP_SAVE")
        self.OPT_DUMP_SAVE.setGeometry(QRect(20, 150, 251, 20))

        self.retranslateUi(SETTINGS)
        self.SETTINGS_DIAG.accepted.connect(SETTINGS.accept)
        self.SETTINGS_DIAG.rejected.connect(SETTINGS.reject)

        QMetaObject.connectSlotsByName(SETTINGS)

    # setupUi

    def retranslateUi(self, SETTINGS):
        SETTINGS.setWindowTitle(
            QCoreApplication.translate("SETTINGS", "Settings", None)
        )
        self.PORT_IN_T.setText(QCoreApplication.translate("SETTINGS", "IN", None))
        self.PORT_OUT_T.setText(QCoreApplication.translate("SETTINGS", "OUT", None))
        self.CHANNEL_T.setText(QCoreApplication.translate("SETTINGS", "CHANNEL", None))
        self.OPT_SEND_BUFFER.setText(
            QCoreApplication.translate(
                "SETTINGS", "Send buffer to device on prog change", None
            )
        )
        self.OPT_DUMP_SAVE.setText(
            QCoreApplication.translate(
                "SETTINGS", "Dump program to device on save", None
            )
        )

    # retranslateUi
