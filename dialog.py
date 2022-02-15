# -*- coding: utf-8 -*-

################################################################################
## Configurator generated from reading UI file 'dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(628, 662)
        self.horizontalLayout = QHBoxLayout(Dialog)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(8)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.lbl_username = QLabel(Dialog)
        self.lbl_username.setObjectName(u"lbl_username")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.lbl_username)

        self.line_username = QLineEdit(Dialog)
        self.line_username.setObjectName(u"line_username")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.line_username)

        self.lbl_password = QLabel(Dialog)
        self.lbl_password.setObjectName(u"lbl_password")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.lbl_password)

        self.line_password = QLineEdit(Dialog)
        self.line_password.setObjectName(u"line_password")
        self.line_password.setEchoMode(QLineEdit.Password)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.line_password)


        self.verticalLayout.addLayout(self.formLayout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.btn_login = QPushButton(Dialog)
        self.btn_login.setObjectName(u"btn_login")

        self.horizontalLayout_3.addWidget(self.btn_login)

        self.btn_save = QPushButton(Dialog)
        self.btn_save.setObjectName(u"btn_save")
        self.btn_save.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.btn_save)

        self.btn_load = QPushButton(Dialog)
        self.btn_load.setObjectName(u"btn_load")
        self.btn_load.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.btn_load)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.text_browser = QTextBrowser(Dialog)
        self.text_browser.setObjectName(u"text_browser")
        self.text_browser.setMinimumSize(QSize(600, 0))

        self.verticalLayout.addWidget(self.text_browser)

        self.btn_doit = QPushButton(Dialog)
        self.btn_doit.setObjectName(u"btn_doit")
        self.btn_doit.setEnabled(False)

        self.verticalLayout.addWidget(self.btn_doit)


        self.horizontalLayout.addLayout(self.verticalLayout)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
#if QT_CONFIG(tooltip)
        self.lbl_username.setToolTip(QCoreApplication.translate("Dialog", u"Username for FRD", None))
#endif // QT_CONFIG(tooltip)
        self.lbl_username.setText(QCoreApplication.translate("Dialog", u"Username", None))
#if QT_CONFIG(tooltip)
        self.lbl_password.setToolTip(QCoreApplication.translate("Dialog", u"WebDAV password for FRD", None))
#endif // QT_CONFIG(tooltip)
        self.lbl_password.setText(QCoreApplication.translate("Dialog", u"Password", None))
#if QT_CONFIG(tooltip)
        self.btn_login.setToolTip(QCoreApplication.translate("Dialog", u"Log in to Fontys Research Drive", None))
#endif // QT_CONFIG(tooltip)
        self.btn_login.setText(QCoreApplication.translate("Dialog", u"Login", None))
#if QT_CONFIG(tooltip)
        self.btn_save.setToolTip(QCoreApplication.translate("Dialog", u"Save username and password to a .env file", None))
#endif // QT_CONFIG(tooltip)
        self.btn_save.setText(QCoreApplication.translate("Dialog", u"Save", None))
#if QT_CONFIG(tooltip)
        self.btn_load.setToolTip(QCoreApplication.translate("Dialog", u"Load folder structure from spreadsheet file", None))
#endif // QT_CONFIG(tooltip)
        self.btn_load.setText(QCoreApplication.translate("Dialog", u"Load", None))
#if QT_CONFIG(tooltip)
        self.btn_doit.setToolTip(QCoreApplication.translate("Dialog", u"Try to make folders on FRD", None))
#endif // QT_CONFIG(tooltip)
        self.btn_doit.setText(QCoreApplication.translate("Dialog", u"Do it!", None))
    # retranslateUi

