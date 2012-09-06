# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './converter_dialog.ui'
#
# Created: Fri Feb 24 01:02:56 2012
#      by: PyQt4 UI code generator 4.8.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ConverterDialog(object):
    def setupUi(self, ConverterDialog):
        ConverterDialog.setObjectName(_fromUtf8("ConverterDialog"))
        ConverterDialog.resize(393, 94)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ConverterDialog.sizePolicy().hasHeightForWidth())
        ConverterDialog.setSizePolicy(sizePolicy)
        ConverterDialog.setMinimumSize(QtCore.QSize(393, 94))
        ConverterDialog.setMaximumSize(QtCore.QSize(393, 94))
        ConverterDialog.setWindowTitle(QtGui.QApplication.translate("ConverterDialog", "Converter", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout = QtGui.QGridLayout(ConverterDialog)
        self.gridLayout.setContentsMargins(-1, -1, -1, 0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lblCSV = QtGui.QLabel(ConverterDialog)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lblCSV.setFont(font)
        self.lblCSV.setFrameShape(QtGui.QFrame.NoFrame)
        self.lblCSV.setText(QtGui.QApplication.translate("ConverterDialog", "Input CSV file:", None, QtGui.QApplication.UnicodeUTF8))
        self.lblCSV.setObjectName(_fromUtf8("lblCSV"))
        self.gridLayout.addWidget(self.lblCSV, 0, 0, 1, 1)
        self.txtCsvPath = QtGui.QLineEdit(ConverterDialog)
        self.txtCsvPath.setObjectName(_fromUtf8("txtCsvPath"))
        self.gridLayout.addWidget(self.txtCsvPath, 0, 1, 1, 1)
        self.btnSelectCsv = QtGui.QToolButton(ConverterDialog)
        self.btnSelectCsv.setText(QtGui.QApplication.translate("ConverterDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectCsv.setObjectName(_fromUtf8("btnSelectCsv"))
        self.gridLayout.addWidget(self.btnSelectCsv, 0, 2, 1, 1)
        self.lblSHP = QtGui.QLabel(ConverterDialog)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lblSHP.setFont(font)
        self.lblSHP.setText(QtGui.QApplication.translate("ConverterDialog", "Output SHP file:", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSHP.setObjectName(_fromUtf8("lblSHP"))
        self.gridLayout.addWidget(self.lblSHP, 1, 0, 1, 1)
        self.txtShpPath = QtGui.QLineEdit(ConverterDialog)
        self.txtShpPath.setObjectName(_fromUtf8("txtShpPath"))
        self.gridLayout.addWidget(self.txtShpPath, 1, 1, 1, 1)
        self.btnSelectShp = QtGui.QToolButton(ConverterDialog)
        self.btnSelectShp.setText(QtGui.QApplication.translate("ConverterDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectShp.setObjectName(_fromUtf8("btnSelectShp"))
        self.gridLayout.addWidget(self.btnSelectShp, 1, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ConverterDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 3)

        self.retranslateUi(ConverterDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ConverterDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ConverterDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ConverterDialog)

    def retranslateUi(self, ConverterDialog):
        pass

