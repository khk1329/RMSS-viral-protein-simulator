# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Mutation_simulator_GUIUHSSGo.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QProgressBar, QPushButton,
    QSizePolicy, QSpinBox, QTextEdit, QVBoxLayout,
    QWidget)

class Ui_CovSimulatorGUI(object):
    def setupUi(self, CovSimulatorGUI):
        if not CovSimulatorGUI.objectName():
            CovSimulatorGUI.setObjectName(u"CovSimulatorGUI")
        CovSimulatorGUI.resize(1148, 744)
        CovSimulatorGUI.setStyleSheet(u"QWidget{background-color: #E9F0F4; color: black;}\n"
"     QPushButton {\n"
"                background-color: #1D83D5;\n"
"                color: white;\n"
"                font-weight: bold;\n"
"                border: 1px solid #4183BC;\n"
"                border-radius: 6px;\n"
"            }\n"
"            QPushButton:hover {\n"
"                background-color: #306999;\n"
"            }")
        self.loadInputBtn = QPushButton(CovSimulatorGUI)
        self.loadInputBtn.setObjectName(u"loadInputBtn")
        self.loadInputBtn.setGeometry(QRect(9, 9, 571, 31))
        self.loadInputBtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.loadTargetBtn = QPushButton(CovSimulatorGUI)
        self.loadTargetBtn.setObjectName(u"loadTargetBtn")
        self.loadTargetBtn.setGeometry(QRect(10, 80, 571, 31))
        self.loadTargetBtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.chooseOutputFolderBtn = QPushButton(CovSimulatorGUI)
        self.chooseOutputFolderBtn.setObjectName(u"chooseOutputFolderBtn")
        self.chooseOutputFolderBtn.setGeometry(QRect(10, 570, 571, 31))
        self.chooseOutputFolderBtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.startBtn = QPushButton(CovSimulatorGUI)
        self.startBtn.setObjectName(u"startBtn")
        self.startBtn.setGeometry(QRect(10, 650, 571, 71))
        self.startBtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.startBtn.setStyleSheet(u" QPushButton {\n"
"                background-color: #0D47A1;\n"
"                color: white;\n"
"                font-weight: bold;\n"
"                border: 1px solid #4183BC;\n"
"                border-radius: 6px;\n"
"            }")
        self.progressBar = QProgressBar(CovSimulatorGUI)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(610, 20, 511, 16))
        self.progressBar.setStyleSheet(u"QProgressBar {\n"
"    border: 1px solid #00CC66;\n"
"    border-radius: 0px;\n"
"    background-color: #E9F0F4;\n"
"    text-align: center;\n"
"    font: bold 12px;\n"
"    color: #006400; /* \ud14d\uc2a4\ud2b8: \uc9c4\ud55c \ucd08\ub85d (DarkGreen) */\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background: qlineargradient(\n"
"        x1: 0, y1: 0, x2: 1, y2: 0,\n"
"        stop: 0 #00FF7F,\n"
"        stop: 1 #00CC66\n"
"    );\n"
"    border-radius: 0px;\n"
"    margin: 0px;\n"
"}\n"
"")
        self.progressBar.setValue(0)
        self.logOutput = QTextEdit(CovSimulatorGUI)
        self.logOutput.setObjectName(u"logOutput")
        self.logOutput.setGeometry(QRect(610, 50, 511, 631))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.logOutput.sizePolicy().hasHeightForWidth())
        self.logOutput.setSizePolicy(sizePolicy)
        self.logOutput.setStyleSheet(u"QWidget{background-color: white; color: black;}\n"
"QScrollBar:vertical {\n"
"        background: transparent;\n"
"        width: 6px;\n"
"        margin: 2px 0 2px 0;\n"
"    }\n"
"\n"
"QScrollBar::handle:vertical {\n"
"        background: #1D83D5;\n"
"        border-radius: 3px;\n"
"        min-height: 20px;\n"
"    }\n"
"\n"
"QScrollBar::add-line:vertical,\n"
"QScrollBar::sub-line:vertical {\n"
"        height: 0px;\n"
"        background: none;\n"
"    }\n"
"\n"
"QScrollBar::add-page:vertical,\n"
"QScrollBar::sub-page:vertical {\n"
"        background: none;\n"
"    }\n"
"\n"
"QScrollBar:horizontal {\n"
"    background: transparent;\n"
"    height: 6px;\n"
"    margin: 0 2px 0 2px;\n"
"}\n"
"\n"
"QScrollBar::handle:horizontal {\n"
"    background: #1D83D5;\n"
"    border-radius: 3px;\n"
"    min-width: 20px;\n"
"}\n"
"\n"
"QScrollBar::add-line:horizontal,\n"
"QScrollBar::sub-line:horizontal {\n"
"    width: 0px;\n"
"    background: none;\n"
"}\n"
"\n"
"QScrollBar::add-page:horizontal,\n"
"QScrollBar::sub-p"
                        "age:horizontal {\n"
"    background: none;\n"
"}")
        self.logOutput.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.logOutput.setReadOnly(True)
        self.inputLabel = QLineEdit(CovSimulatorGUI)
        self.inputLabel.setObjectName(u"inputLabel")
        self.inputLabel.setGeometry(QRect(10, 50, 571, 22))
        self.inputLabel.setStyleSheet(u"QWidget{background-color: white; color: black;}")
        self.inputLabel.setReadOnly(True)
        self.targetLabel = QLineEdit(CovSimulatorGUI)
        self.targetLabel.setObjectName(u"targetLabel")
        self.targetLabel.setGeometry(QRect(10, 120, 571, 22))
        self.targetLabel.setStyleSheet(u"QWidget{background-color: white; color: black;}")
        self.targetLabel.setReadOnly(True)
        self.outputFolderLabel = QLineEdit(CovSimulatorGUI)
        self.outputFolderLabel.setObjectName(u"outputFolderLabel")
        self.outputFolderLabel.setGeometry(QRect(10, 610, 571, 22))
        self.outputFolderLabel.setStyleSheet(u"QWidget{background-color: white; color: black;}")
        self.outputFolderLabel.setReadOnly(True)
        self.frame = QFrame(CovSimulatorGUI)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(30, 200, 531, 341))
        self.frame.setStyleSheet(u"QFrame {\n"
"    background-color: white;\n"
"                border: 1px solid #ccc;}\n"
"QLabel {    background-color: white;                border: 0px solid}\n"
"\n"
"")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.mutationLayout = QHBoxLayout()
        self.mutationLayout.setObjectName(u"mutationLayout")
        self.mutationLabel = QLabel(self.frame)
        self.mutationLabel.setObjectName(u"mutationLabel")
        self.mutationLabel.setStyleSheet(u"QWidget{background-color: white; color: black;}")

        self.mutationLayout.addWidget(self.mutationLabel)

        self.mutationRate = QDoubleSpinBox(self.frame)
        self.mutationRate.setObjectName(u"mutationRate")
        sizePolicy.setHeightForWidth(self.mutationRate.sizePolicy().hasHeightForWidth())
        self.mutationRate.setSizePolicy(sizePolicy)
        self.mutationRate.setStyleSheet(u"QWidget{background-color: white; color: black;}")
        self.mutationRate.setDecimals(10)
        self.mutationRate.setValue(0.000001000000000)

        self.mutationLayout.addWidget(self.mutationRate)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.mutationLabel_2 = QLabel(self.frame)
        self.mutationLabel_2.setObjectName(u"mutationLabel_2")
        font = QFont()
        font.setPointSize(8)
        self.mutationLabel_2.setFont(font)
        self.mutationLabel_2.setStyleSheet(u"QWidget{background-color: white; color: black;}")

        self.verticalLayout_2.addWidget(self.mutationLabel_2)

        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font)

        self.verticalLayout_2.addWidget(self.label_2)


        self.mutationLayout.addLayout(self.verticalLayout_2)


        self.verticalLayout.addLayout(self.mutationLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.subIndelLabel = QLabel(self.frame)
        self.subIndelLabel.setObjectName(u"subIndelLabel")
        self.subIndelLabel.setStyleSheet(u"QWidget{background-color: white; color: black;}")

        self.horizontalLayout_2.addWidget(self.subIndelLabel)

        self.subRatio = QDoubleSpinBox(self.frame)
        self.subRatio.setObjectName(u"subRatio")
        sizePolicy.setHeightForWidth(self.subRatio.sizePolicy().hasHeightForWidth())
        self.subRatio.setSizePolicy(sizePolicy)
        self.subRatio.setStyleSheet(u"QWidget{background-color: white; color: black;}")
        self.subRatio.setDecimals(2)
        self.subRatio.setMinimum(1.000000000000000)
        self.subRatio.setValue(24.000000000000000)

        self.horizontalLayout_2.addWidget(self.subRatio)

        self.indelRatio = QDoubleSpinBox(self.frame)
        self.indelRatio.setObjectName(u"indelRatio")
        sizePolicy.setHeightForWidth(self.indelRatio.sizePolicy().hasHeightForWidth())
        self.indelRatio.setSizePolicy(sizePolicy)
        self.indelRatio.setStyleSheet(u"QWidget{background-color: white; color: black;}")
        self.indelRatio.setMinimum(0.000000000000000)
        self.indelRatio.setValue(1.000000000000000)

        self.horizontalLayout_2.addWidget(self.indelRatio)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.tranTransvLabel = QLabel(self.frame)
        self.tranTransvLabel.setObjectName(u"tranTransvLabel")
        self.tranTransvLabel.setStyleSheet(u"QWidget{background-color: white; color: black;}")

        self.horizontalLayout_3.addWidget(self.tranTransvLabel)

        self.tranRatio = QDoubleSpinBox(self.frame)
        self.tranRatio.setObjectName(u"tranRatio")
        sizePolicy.setHeightForWidth(self.tranRatio.sizePolicy().hasHeightForWidth())
        self.tranRatio.setSizePolicy(sizePolicy)
        self.tranRatio.setStyleSheet(u"QWidget{background-color: white; color: black;}")
        self.tranRatio.setValue(2.000000000000000)

        self.horizontalLayout_3.addWidget(self.tranRatio)

        self.transvRatio = QDoubleSpinBox(self.frame)
        self.transvRatio.setObjectName(u"transvRatio")
        sizePolicy.setHeightForWidth(self.transvRatio.sizePolicy().hasHeightForWidth())
        self.transvRatio.setSizePolicy(sizePolicy)
        self.transvRatio.setStyleSheet(u"QWidget{background-color: white; color: black;}")
        self.transvRatio.setValue(1.000000000000000)

        self.horizontalLayout_3.addWidget(self.transvRatio)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.cyclesLabel = QLabel(self.frame)
        self.cyclesLabel.setObjectName(u"cyclesLabel")
        self.cyclesLabel.setStyleSheet(u"QWidget{background-color: white; color: black;}")

        self.horizontalLayout_4.addWidget(self.cyclesLabel)

        self.cyclesSpinBox = QSpinBox(self.frame)
        self.cyclesSpinBox.setObjectName(u"cyclesSpinBox")
        sizePolicy.setHeightForWidth(self.cyclesSpinBox.sizePolicy().hasHeightForWidth())
        self.cyclesSpinBox.setSizePolicy(sizePolicy)
        self.cyclesSpinBox.setStyleSheet(u"QWidget{background-color: white; color: black;}")
        self.cyclesSpinBox.setMinimum(1)
        self.cyclesSpinBox.setMaximum(99999999)
        self.cyclesSpinBox.setValue(1000)

        self.horizontalLayout_4.addWidget(self.cyclesSpinBox)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.replicationsLabel = QLabel(self.frame)
        self.replicationsLabel.setObjectName(u"replicationsLabel")
        self.replicationsLabel.setStyleSheet(u"QWidget{background-color: white; color: black;}")

        self.horizontalLayout_5.addWidget(self.replicationsLabel)

        self.replicationsSpinBox = QSpinBox(self.frame)
        self.replicationsSpinBox.setObjectName(u"replicationsSpinBox")
        sizePolicy.setHeightForWidth(self.replicationsSpinBox.sizePolicy().hasHeightForWidth())
        self.replicationsSpinBox.setSizePolicy(sizePolicy)
        self.replicationsSpinBox.setStyleSheet(u"QWidget{background-color: white; color: black;}")
        self.replicationsSpinBox.setMinimum(1)
        self.replicationsSpinBox.setMaximum(999999999)
        self.replicationsSpinBox.setValue(10000)

        self.horizontalLayout_5.addWidget(self.replicationsSpinBox)


        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.topKLabel = QLabel(self.frame)
        self.topKLabel.setObjectName(u"topKLabel")
        self.topKLabel.setStyleSheet(u"QWidget{background-color: white; color: black;}")

        self.horizontalLayout_6.addWidget(self.topKLabel)

        self.topKSpinBox = QSpinBox(self.frame)
        self.topKSpinBox.setObjectName(u"topKSpinBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.topKSpinBox.sizePolicy().hasHeightForWidth())
        self.topKSpinBox.setSizePolicy(sizePolicy1)
        self.topKSpinBox.setStyleSheet(u"QWidget{background-color: white; color: black;}")
        self.topKSpinBox.setMinimum(1)
        self.topKSpinBox.setMaximum(999)
        self.topKSpinBox.setValue(10)

        self.horizontalLayout_6.addWidget(self.topKSpinBox)


        self.verticalLayout.addLayout(self.horizontalLayout_6)

        self.label = QLabel(CovSimulatorGUI)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(30, 170, 531, 31))
        self.label.setStyleSheet(u"QLabel{background-color: #B7BBBC;\n"
"         color: white; font-weight: bold;}")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.CancelBtn = QPushButton(CovSimulatorGUI)
        self.CancelBtn.setObjectName(u"CancelBtn")
        self.CancelBtn.setGeometry(QRect(1010, 690, 111, 31))
        self.CancelBtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.CancelBtn.setStyleSheet(u"     QPushButton {\n"
"                background-color: red;\n"
"                color: white;\n"
"                font-weight: bold;\n"
"                border: 1px solid red;\n"
"                border-radius: 6px;\n"
"            }\n"
"            QPushButton:hover {\n"
"                background-color: #B71C1C;\n"
"            }")
        self.frame.raise_()
        self.loadInputBtn.raise_()
        self.loadTargetBtn.raise_()
        self.chooseOutputFolderBtn.raise_()
        self.startBtn.raise_()
        self.progressBar.raise_()
        self.logOutput.raise_()
        self.inputLabel.raise_()
        self.targetLabel.raise_()
        self.outputFolderLabel.raise_()
        self.label.raise_()
        self.CancelBtn.raise_()

        self.retranslateUi(CovSimulatorGUI)

        QMetaObject.connectSlotsByName(CovSimulatorGUI)
    # setupUi

    def retranslateUi(self, CovSimulatorGUI):
        CovSimulatorGUI.setWindowTitle(QCoreApplication.translate("CovSimulatorGUI", u"Mutation Simulator", None))
        self.loadInputBtn.setText(QCoreApplication.translate("CovSimulatorGUI", u"Load Input FASTA file", None))
        self.loadTargetBtn.setText(QCoreApplication.translate("CovSimulatorGUI", u"Load Target FASTA file", None))
        self.chooseOutputFolderBtn.setText(QCoreApplication.translate("CovSimulatorGUI", u"Choose Output Folder", None))
        self.startBtn.setText(QCoreApplication.translate("CovSimulatorGUI", u"Run Simulation", None))
        self.inputLabel.setText(QCoreApplication.translate("CovSimulatorGUI", u"No input file selected", None))
        self.targetLabel.setText(QCoreApplication.translate("CovSimulatorGUI", u"No target file selected", None))
        self.outputFolderLabel.setText(QCoreApplication.translate("CovSimulatorGUI", u"No output folder selected", None))
        self.mutationLabel.setText(QCoreApplication.translate("CovSimulatorGUI", u"Total Mutation Rate =", None))
        self.mutationLabel_2.setText(QCoreApplication.translate("CovSimulatorGUI", u"ex) 0.00000376 or 3.76e-6", None))
        self.label_2.setText(QCoreApplication.translate("CovSimulatorGUI", u"     0.01 = 1%", None))
        self.subIndelLabel.setText(QCoreApplication.translate("CovSimulatorGUI", u"Substitution : INDEL Ratio =    ", None))
        self.tranTransvLabel.setText(QCoreApplication.translate("CovSimulatorGUI", u"Transition : Transversion Ratio =", None))
        self.cyclesLabel.setText(QCoreApplication.translate("CovSimulatorGUI", u"Number of Cycles:                 ", None))
        self.replicationsLabel.setText(QCoreApplication.translate("CovSimulatorGUI", u"Replications per Cycle:            ", None))
        self.topKLabel.setText(QCoreApplication.translate("CovSimulatorGUI", u"Top-N Sequences to select each cycle:", None))
        self.label.setText(QCoreApplication.translate("CovSimulatorGUI", u"User setting", None))
        self.CancelBtn.setText(QCoreApplication.translate("CovSimulatorGUI", u"Cancel", None))
    # retranslateUi

