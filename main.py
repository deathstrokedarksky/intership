# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'InternProject.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1314, 771)
        font = QtGui.QFont()
        font.setPointSize(10)
        MainWindow.setFont(font)
        MainWindow.setFocusPolicy(QtCore.Qt.NoFocus)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.plotter = QtWidgets.QPushButton(self.centralwidget)
        self.plotter.setGeometry(QtCore.QRect(900, 640, 161, 50))
        self.plotter.setStyleSheet("QPushButton{\n"
"    background-color:rgb(0,200,96);\n"
"    border: none;\n"
"    padding: 5px;\n"
"    color:rgb(205,230,255);\n"
"    border-radius: 5px;\n"
"    font:75 14pt \"Candara\";\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"    background-color:rgb(0,220,65);    \n"
"}\n"
"QPushButton:pressed{\n"
"    background-color:rgb(0,200,96);    \n"
"}")
        self.plotter.setObjectName("plotter")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(50, 20, 1191, 601))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.datetimefrom = QtWidgets.QDateTimeEdit(self.centralwidget)
        self.datetimefrom.setGeometry(QtCore.QRect(250, 650, 161, 32))
        self.datetimefrom.setMaximumDate(QtCore.QDate(2100, 12, 31))
        self.datetimefrom.setMinimumDate(QtCore.QDate(1970, 1, 1))
        self.datetimefrom.setMaximumTime(QtCore.QTime(23, 59, 59))
        self.datetimefrom.setCalendarPopup(True)
        self.datetimefrom.setTimeSpec(QtCore.Qt.LocalTime)
        self.datetimefrom.setObjectName("datetimefrom")
        self.labelfrom = QtWidgets.QLabel(self.centralwidget)
        self.labelfrom.setGeometry(QtCore.QRect(170, 650, 70, 32))
        self.labelfrom.setStyleSheet("QLabel{\n"
"    background-color:rgb(0,200,96);\n"
"    border: none;\n"
"    padding: 5px;\n"
"    color:rgb(205,230,255);\n"
"    border-radius: 5px;\n"
"    font:75 14pt \"Candara\";\n"
"}")
        self.labelfrom.setObjectName("labelfrom")
        self.labelto = QtWidgets.QLabel(self.centralwidget)
        self.labelto.setGeometry(QtCore.QRect(430, 650, 70, 32))
        self.labelto.setStyleSheet("QLabel{\n"
"    background-color:rgb(0,200,96);\n"
"    border: none;\n"
"    padding: 5px;\n"
"    color:rgb(205,230,255);\n"
"    border-radius: 5px;\n"
"    font:75 14pt \"Candara\";\n"
"}")
        self.labelto.setObjectName("labelto")
        self.datetimeto = QtWidgets.QDateTimeEdit(self.centralwidget)
        self.datetimeto.setGeometry(QtCore.QRect(510, 650, 161, 32))
        self.datetimeto.setMaximumDate(QtCore.QDate(2100, 12, 31))
        self.datetimeto.setMinimumDate(QtCore.QDate(1970, 1, 1))
        self.datetimeto.setMaximumTime(QtCore.QTime(23, 59, 59))
        self.datetimeto.setCalendarPopup(True)
        self.datetimeto.setTimeSpec(QtCore.Qt.LocalTime)
        self.datetimeto.setObjectName("datetimeto")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1314, 29))
        self.menubar.setObjectName("menubar")
        self.menuOpen_files = QtWidgets.QMenu(self.menubar)
        self.menuOpen_files.setObjectName("menuOpen_files")
        self.menuExport = QtWidgets.QMenu(self.menubar)
        self.menuExport.setObjectName("menuExport")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menuOpen_files.addSeparator()
        self.menubar.addAction(self.menuOpen_files.menuAction())
        self.menubar.addAction(self.menuExport.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.plotter.setText(_translate("MainWindow", "Plot graphs"))
        self.datetimefrom.setDisplayFormat(_translate("MainWindow", "M/d/yyyy h:mm:ss"))
        self.labelfrom.setText(_translate("MainWindow", "From:"))
        self.labelto.setText(_translate("MainWindow", "To:"))
        self.datetimeto.setDisplayFormat(_translate("MainWindow", "M/d/yyyy h:mm:ss"))
        self.menuOpen_files.setTitle(_translate("MainWindow", "Import"))
        self.menuExport.setTitle(_translate("MainWindow", "Export"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
