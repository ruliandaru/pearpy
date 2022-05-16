# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'layout.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(887, 541)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_22 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setAcceptDrops(False)
        self.MainPage = QWidget()
        self.MainPage.setObjectName(u"MainPage")
        self.verticalLayout_7 = QVBoxLayout(self.MainPage)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_10 = QVBoxLayout()
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.label_8 = QLabel(self.MainPage)
        self.label_8.setObjectName(u"label_8")

        self.verticalLayout_10.addWidget(self.label_8)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.mainpage_input_earlier_dsm = QLineEdit(self.MainPage)
        self.mainpage_input_earlier_dsm.setObjectName(u"mainpage_input_earlier_dsm")

        self.horizontalLayout_15.addWidget(self.mainpage_input_earlier_dsm)

        self.mainpage_button_earlier_dsm = QPushButton(self.MainPage)
        self.mainpage_button_earlier_dsm.setObjectName(u"mainpage_button_earlier_dsm")

        self.horizontalLayout_15.addWidget(self.mainpage_button_earlier_dsm)


        self.verticalLayout_10.addLayout(self.horizontalLayout_15)


        self.verticalLayout_7.addLayout(self.verticalLayout_10)

        self.verticalLayout_11 = QVBoxLayout()
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.label_9 = QLabel(self.MainPage)
        self.label_9.setObjectName(u"label_9")

        self.verticalLayout_11.addWidget(self.label_9)

        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.mainpage_input_later_dsm = QLineEdit(self.MainPage)
        self.mainpage_input_later_dsm.setObjectName(u"mainpage_input_later_dsm")

        self.horizontalLayout_16.addWidget(self.mainpage_input_later_dsm)

        self.mainpage_button_later_dsm = QPushButton(self.MainPage)
        self.mainpage_button_later_dsm.setObjectName(u"mainpage_button_later_dsm")

        self.horizontalLayout_16.addWidget(self.mainpage_button_later_dsm)


        self.verticalLayout_11.addLayout(self.horizontalLayout_16)


        self.verticalLayout_7.addLayout(self.verticalLayout_11)

        self.verticalLayout_12 = QVBoxLayout()
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.label_10 = QLabel(self.MainPage)
        self.label_10.setObjectName(u"label_10")

        self.verticalLayout_12.addWidget(self.label_10)

        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.mainpage_input_output_folder = QLineEdit(self.MainPage)
        self.mainpage_input_output_folder.setObjectName(u"mainpage_input_output_folder")

        self.horizontalLayout_17.addWidget(self.mainpage_input_output_folder)

        self.mainpage_button_output_folder = QPushButton(self.MainPage)
        self.mainpage_button_output_folder.setObjectName(u"mainpage_button_output_folder")

        self.horizontalLayout_17.addWidget(self.mainpage_button_output_folder)


        self.verticalLayout_12.addLayout(self.horizontalLayout_17)


        self.verticalLayout_7.addLayout(self.verticalLayout_12)

        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.verticalLayout_18 = QVBoxLayout()
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.label_16 = QLabel(self.MainPage)
        self.label_16.setObjectName(u"label_16")

        self.verticalLayout_18.addWidget(self.label_16)

        self.mainpage_input_confidencelimit = QComboBox(self.MainPage)
        self.mainpage_input_confidencelimit.setObjectName(u"mainpage_input_confidencelimit")

        self.verticalLayout_18.addWidget(self.mainpage_input_confidencelimit)

        self.label_22 = QLabel(self.MainPage)
        self.label_22.setObjectName(u"label_22")

        self.verticalLayout_18.addWidget(self.label_22)

        self.mainpage_input_stream_buffer = QLineEdit(self.MainPage)
        self.mainpage_input_stream_buffer.setObjectName(u"mainpage_input_stream_buffer")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainpage_input_stream_buffer.sizePolicy().hasHeightForWidth())
        self.mainpage_input_stream_buffer.setSizePolicy(sizePolicy)

        self.verticalLayout_18.addWidget(self.mainpage_input_stream_buffer)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_18.addItem(self.verticalSpacer_5)


        self.horizontalLayout_19.addLayout(self.verticalLayout_18)

        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.label_6 = QLabel(self.MainPage)
        self.label_6.setObjectName(u"label_6")

        self.verticalLayout_8.addWidget(self.label_6)

        self.mainpage_input_streamthreshold = QLineEdit(self.MainPage)
        self.mainpage_input_streamthreshold.setObjectName(u"mainpage_input_streamthreshold")
        sizePolicy.setHeightForWidth(self.mainpage_input_streamthreshold.sizePolicy().hasHeightForWidth())
        self.mainpage_input_streamthreshold.setSizePolicy(sizePolicy)

        self.verticalLayout_8.addWidget(self.mainpage_input_streamthreshold)

        self.label_23 = QLabel(self.MainPage)
        self.label_23.setObjectName(u"label_23")

        self.verticalLayout_8.addWidget(self.label_23)

        self.mainpage_input_max_pct_stream = QLineEdit(self.MainPage)
        self.mainpage_input_max_pct_stream.setObjectName(u"mainpage_input_max_pct_stream")
        sizePolicy.setHeightForWidth(self.mainpage_input_max_pct_stream.sizePolicy().hasHeightForWidth())
        self.mainpage_input_max_pct_stream.setSizePolicy(sizePolicy)

        self.verticalLayout_8.addWidget(self.mainpage_input_max_pct_stream)

        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_8.addItem(self.verticalSpacer_6)


        self.horizontalLayout_19.addLayout(self.verticalLayout_8)

        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.label_11 = QLabel(self.MainPage)
        self.label_11.setObjectName(u"label_11")

        self.verticalLayout_9.addWidget(self.label_11)

        self.mainpage_button_run = QPushButton(self.MainPage)
        self.mainpage_button_run.setObjectName(u"mainpage_button_run")

        self.verticalLayout_9.addWidget(self.mainpage_button_run)

        self.mainpage_check_preservedata = QCheckBox(self.MainPage)
        self.mainpage_check_preservedata.setObjectName(u"mainpage_check_preservedata")
        self.mainpage_check_preservedata.setChecked(True)

        self.verticalLayout_9.addWidget(self.mainpage_check_preservedata)

        self.verticalSpacer_7 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_9.addItem(self.verticalSpacer_7)

        self.label_18 = QLabel(self.MainPage)
        self.label_18.setObjectName(u"label_18")

        self.verticalLayout_9.addWidget(self.label_18)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.radioButton_2 = QRadioButton(self.MainPage)
        self.output_type = QButtonGroup(MainWindow)
        self.output_type.setObjectName(u"output_type")
        self.output_type.addButton(self.radioButton_2)
        self.radioButton_2.setObjectName(u"radioButton_2")

        self.horizontalLayout_13.addWidget(self.radioButton_2)

        self.radioButton = QRadioButton(self.MainPage)
        self.output_type.addButton(self.radioButton)
        self.radioButton.setObjectName(u"radioButton")
        self.radioButton.setChecked(True)

        self.horizontalLayout_13.addWidget(self.radioButton)


        self.verticalLayout_9.addLayout(self.horizontalLayout_13)


        self.horizontalLayout_19.addLayout(self.verticalLayout_9)


        self.verticalLayout_7.addLayout(self.horizontalLayout_19)

        self.mainpage_label_progressbar_overall = QLabel(self.MainPage)
        self.mainpage_label_progressbar_overall.setObjectName(u"mainpage_label_progressbar_overall")

        self.verticalLayout_7.addWidget(self.mainpage_label_progressbar_overall)

        self.mainpage_progressbar_overall = QProgressBar(self.MainPage)
        self.mainpage_progressbar_overall.setObjectName(u"mainpage_progressbar_overall")
        self.mainpage_progressbar_overall.setValue(0)

        self.verticalLayout_7.addWidget(self.mainpage_progressbar_overall)

        self.mainpage_label_progressbar_sub = QLabel(self.MainPage)
        self.mainpage_label_progressbar_sub.setObjectName(u"mainpage_label_progressbar_sub")

        self.verticalLayout_7.addWidget(self.mainpage_label_progressbar_sub)

        self.mainpage_progressbar_sub = QProgressBar(self.MainPage)
        self.mainpage_progressbar_sub.setObjectName(u"mainpage_progressbar_sub")
        self.mainpage_progressbar_sub.setValue(0)

        self.verticalLayout_7.addWidget(self.mainpage_progressbar_sub)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_7.addItem(self.verticalSpacer_3)

        self.tabWidget.addTab(self.MainPage, "")
        self.SurfaceHydroPage = QWidget()
        self.SurfaceHydroPage.setObjectName(u"SurfaceHydroPage")
        self.verticalLayout_20 = QVBoxLayout(self.SurfaceHydroPage)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.verticalLayout_19 = QVBoxLayout()
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.verticalLayout_23 = QVBoxLayout()
        self.verticalLayout_23.setObjectName(u"verticalLayout_23")
        self.label_7 = QLabel(self.SurfaceHydroPage)
        self.label_7.setObjectName(u"label_7")

        self.verticalLayout_23.addWidget(self.label_7)

        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.surfacehydro_input_later_dsm = QLineEdit(self.SurfaceHydroPage)
        self.surfacehydro_input_later_dsm.setObjectName(u"surfacehydro_input_later_dsm")

        self.horizontalLayout_14.addWidget(self.surfacehydro_input_later_dsm)

        self.surfacehydro_button_later_dsm = QPushButton(self.SurfaceHydroPage)
        self.surfacehydro_button_later_dsm.setObjectName(u"surfacehydro_button_later_dsm")

        self.horizontalLayout_14.addWidget(self.surfacehydro_button_later_dsm)


        self.verticalLayout_23.addLayout(self.horizontalLayout_14)


        self.verticalLayout_19.addLayout(self.verticalLayout_23)

        self.verticalLayout_24 = QVBoxLayout()
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.label_17 = QLabel(self.SurfaceHydroPage)
        self.label_17.setObjectName(u"label_17")

        self.verticalLayout_24.addWidget(self.label_17)

        self.horizontalLayout_20 = QHBoxLayout()
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.surfacehydro_input_output_folder = QLineEdit(self.SurfaceHydroPage)
        self.surfacehydro_input_output_folder.setObjectName(u"surfacehydro_input_output_folder")

        self.horizontalLayout_20.addWidget(self.surfacehydro_input_output_folder)

        self.surfacehydro_button_output_folder = QPushButton(self.SurfaceHydroPage)
        self.surfacehydro_button_output_folder.setObjectName(u"surfacehydro_button_output_folder")

        self.horizontalLayout_20.addWidget(self.surfacehydro_button_output_folder)


        self.verticalLayout_24.addLayout(self.horizontalLayout_20)


        self.verticalLayout_19.addLayout(self.verticalLayout_24)

        self.horizontalLayout_22 = QHBoxLayout()
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.verticalLayout_21 = QVBoxLayout()
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.surfacehydro_label_stream_threshold = QLabel(self.SurfaceHydroPage)
        self.surfacehydro_label_stream_threshold.setObjectName(u"surfacehydro_label_stream_threshold")

        self.verticalLayout_21.addWidget(self.surfacehydro_label_stream_threshold)

        self.surfacehydro_input_stream_threshold = QLineEdit(self.SurfaceHydroPage)
        self.surfacehydro_input_stream_threshold.setObjectName(u"surfacehydro_input_stream_threshold")
        sizePolicy.setHeightForWidth(self.surfacehydro_input_stream_threshold.sizePolicy().hasHeightForWidth())
        self.surfacehydro_input_stream_threshold.setSizePolicy(sizePolicy)

        self.verticalLayout_21.addWidget(self.surfacehydro_input_stream_threshold)


        self.horizontalLayout_22.addLayout(self.verticalLayout_21)

        self.verticalLayout_13 = QVBoxLayout()
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.label_20 = QLabel(self.SurfaceHydroPage)
        self.label_20.setObjectName(u"label_20")

        self.verticalLayout_13.addWidget(self.label_20)

        self.surfacehydro_button_run = QPushButton(self.SurfaceHydroPage)
        self.surfacehydro_button_run.setObjectName(u"surfacehydro_button_run")

        self.verticalLayout_13.addWidget(self.surfacehydro_button_run)


        self.horizontalLayout_22.addLayout(self.verticalLayout_13)


        self.verticalLayout_19.addLayout(self.horizontalLayout_22)

        self.surfacehydro_progressbar = QProgressBar(self.SurfaceHydroPage)
        self.surfacehydro_progressbar.setObjectName(u"surfacehydro_progressbar")
        self.surfacehydro_progressbar.setMaximum(100)
        self.surfacehydro_progressbar.setValue(0)

        self.verticalLayout_19.addWidget(self.surfacehydro_progressbar)


        self.verticalLayout_20.addLayout(self.verticalLayout_19)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_20.addItem(self.verticalSpacer_4)

        self.tabWidget.addTab(self.SurfaceHydroPage, "")
        self.InitialPoint = QWidget()
        self.InitialPoint.setObjectName(u"InitialPoint")
        self.InitialPoint.setCursor(QCursor(Qt.ArrowCursor))
        self.verticalLayout = QVBoxLayout(self.InitialPoint)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout_17 = QVBoxLayout()
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.label_15 = QLabel(self.InitialPoint)
        self.label_15.setObjectName(u"label_15")

        self.verticalLayout_17.addWidget(self.label_15)

        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.startingpoint_input_flow_directoin = QLineEdit(self.InitialPoint)
        self.startingpoint_input_flow_directoin.setObjectName(u"startingpoint_input_flow_directoin")

        self.horizontalLayout_18.addWidget(self.startingpoint_input_flow_directoin)

        self.startingpoint_button_flow_directoin = QPushButton(self.InitialPoint)
        self.startingpoint_button_flow_directoin.setObjectName(u"startingpoint_button_flow_directoin")
        self.startingpoint_button_flow_directoin.setCursor(QCursor(Qt.PointingHandCursor))

        self.horizontalLayout_18.addWidget(self.startingpoint_button_flow_directoin)


        self.verticalLayout_17.addLayout(self.horizontalLayout_18)


        self.verticalLayout.addLayout(self.verticalLayout_17)

        self.verticalLayout_25 = QVBoxLayout()
        self.verticalLayout_25.setObjectName(u"verticalLayout_25")
        self.label_21 = QLabel(self.InitialPoint)
        self.label_21.setObjectName(u"label_21")

        self.verticalLayout_25.addWidget(self.label_21)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.startingpoint_input_stream = QLineEdit(self.InitialPoint)
        self.startingpoint_input_stream.setObjectName(u"startingpoint_input_stream")

        self.horizontalLayout.addWidget(self.startingpoint_input_stream)

        self.startingpoint_button_stream = QPushButton(self.InitialPoint)
        self.startingpoint_button_stream.setObjectName(u"startingpoint_button_stream")

        self.horizontalLayout.addWidget(self.startingpoint_button_stream)


        self.verticalLayout_25.addLayout(self.horizontalLayout)


        self.verticalLayout.addLayout(self.verticalLayout_25)

        self.verticalLayout_14 = QVBoxLayout()
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.label_12 = QLabel(self.InitialPoint)
        self.label_12.setObjectName(u"label_12")

        self.verticalLayout_14.addWidget(self.label_12)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.startingpoint_input_earlier_dsm = QLineEdit(self.InitialPoint)
        self.startingpoint_input_earlier_dsm.setObjectName(u"startingpoint_input_earlier_dsm")

        self.horizontalLayout_2.addWidget(self.startingpoint_input_earlier_dsm)

        self.startingpoint_button_earlier_dsm = QPushButton(self.InitialPoint)
        self.startingpoint_button_earlier_dsm.setObjectName(u"startingpoint_button_earlier_dsm")
        self.startingpoint_button_earlier_dsm.setCursor(QCursor(Qt.PointingHandCursor))

        self.horizontalLayout_2.addWidget(self.startingpoint_button_earlier_dsm)


        self.verticalLayout_14.addLayout(self.horizontalLayout_2)


        self.verticalLayout.addLayout(self.verticalLayout_14)

        self.verticalLayout_15 = QVBoxLayout()
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.label_13 = QLabel(self.InitialPoint)
        self.label_13.setObjectName(u"label_13")

        self.verticalLayout_15.addWidget(self.label_13)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.startingpoint_input_later_dsm = QLineEdit(self.InitialPoint)
        self.startingpoint_input_later_dsm.setObjectName(u"startingpoint_input_later_dsm")

        self.horizontalLayout_4.addWidget(self.startingpoint_input_later_dsm)

        self.startingpoint_button_later_dsm = QPushButton(self.InitialPoint)
        self.startingpoint_button_later_dsm.setObjectName(u"startingpoint_button_later_dsm")
        self.startingpoint_button_later_dsm.setCursor(QCursor(Qt.PointingHandCursor))

        self.horizontalLayout_4.addWidget(self.startingpoint_button_later_dsm)


        self.verticalLayout_15.addLayout(self.horizontalLayout_4)


        self.verticalLayout.addLayout(self.verticalLayout_15)

        self.horizontalLayout_23 = QHBoxLayout()
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.verticalLayout_28 = QVBoxLayout()
        self.verticalLayout_28.setObjectName(u"verticalLayout_28")
        self.label_24 = QLabel(self.InitialPoint)
        self.label_24.setObjectName(u"label_24")

        self.verticalLayout_28.addWidget(self.label_24)

        self.startingpoint_input_stream_buffer = QLineEdit(self.InitialPoint)
        self.startingpoint_input_stream_buffer.setObjectName(u"startingpoint_input_stream_buffer")
        sizePolicy.setHeightForWidth(self.startingpoint_input_stream_buffer.sizePolicy().hasHeightForWidth())
        self.startingpoint_input_stream_buffer.setSizePolicy(sizePolicy)

        self.verticalLayout_28.addWidget(self.startingpoint_input_stream_buffer)


        self.horizontalLayout_23.addLayout(self.verticalLayout_28)

        self.verticalLayout_27 = QVBoxLayout()
        self.verticalLayout_27.setObjectName(u"verticalLayout_27")
        self.label_25 = QLabel(self.InitialPoint)
        self.label_25.setObjectName(u"label_25")

        self.verticalLayout_27.addWidget(self.label_25)

        self.startingpoint_input_max_pct_stream = QLineEdit(self.InitialPoint)
        self.startingpoint_input_max_pct_stream.setObjectName(u"startingpoint_input_max_pct_stream")
        sizePolicy.setHeightForWidth(self.startingpoint_input_max_pct_stream.sizePolicy().hasHeightForWidth())
        self.startingpoint_input_max_pct_stream.setSizePolicy(sizePolicy)

        self.verticalLayout_27.addWidget(self.startingpoint_input_max_pct_stream)


        self.horizontalLayout_23.addLayout(self.verticalLayout_27)


        self.verticalLayout.addLayout(self.horizontalLayout_23)

        self.verticalLayout_16 = QVBoxLayout()
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.label_14 = QLabel(self.InitialPoint)
        self.label_14.setObjectName(u"label_14")

        self.verticalLayout_16.addWidget(self.label_14)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.startingpoint_input_output_location = QLineEdit(self.InitialPoint)
        self.startingpoint_input_output_location.setObjectName(u"startingpoint_input_output_location")

        self.horizontalLayout_5.addWidget(self.startingpoint_input_output_location)

        self.startingpoint_button_output_location = QPushButton(self.InitialPoint)
        self.startingpoint_button_output_location.setObjectName(u"startingpoint_button_output_location")
        self.startingpoint_button_output_location.setCursor(QCursor(Qt.PointingHandCursor))

        self.horizontalLayout_5.addWidget(self.startingpoint_button_output_location)


        self.verticalLayout_16.addLayout(self.horizontalLayout_5)


        self.verticalLayout.addLayout(self.verticalLayout_16)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.startingpoint_progressbar_starting_point = QProgressBar(self.InitialPoint)
        self.startingpoint_progressbar_starting_point.setObjectName(u"startingpoint_progressbar_starting_point")
        self.startingpoint_progressbar_starting_point.setValue(0)

        self.horizontalLayout_3.addWidget(self.startingpoint_progressbar_starting_point)

        self.startingpoint_button_find_starting_point = QPushButton(self.InitialPoint)
        self.startingpoint_button_find_starting_point.setObjectName(u"startingpoint_button_find_starting_point")
        self.startingpoint_button_find_starting_point.setCursor(QCursor(Qt.PointingHandCursor))

        self.horizontalLayout_3.addWidget(self.startingpoint_button_find_starting_point)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.tabWidget.addTab(self.InitialPoint, "")
        self.InundationZone = QWidget()
        self.InundationZone.setObjectName(u"InundationZone")
        self.gridLayout_4 = QGridLayout(self.InundationZone)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_2 = QLabel(self.InundationZone)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_3.addWidget(self.label_2)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.inundation_input_coordinate_file = QLineEdit(self.InundationZone)
        self.inundation_input_coordinate_file.setObjectName(u"inundation_input_coordinate_file")

        self.horizontalLayout_8.addWidget(self.inundation_input_coordinate_file)

        self.inundation_button_coordinate_file = QPushButton(self.InundationZone)
        self.inundation_button_coordinate_file.setObjectName(u"inundation_button_coordinate_file")
        self.inundation_button_coordinate_file.setCursor(QCursor(Qt.PointingHandCursor))

        self.horizontalLayout_8.addWidget(self.inundation_button_coordinate_file)


        self.verticalLayout_3.addLayout(self.horizontalLayout_8)


        self.gridLayout_4.addLayout(self.verticalLayout_3, 1, 0, 1, 1)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(self.InundationZone)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.inundation_input_stream_raster = QLineEdit(self.InundationZone)
        self.inundation_input_stream_raster.setObjectName(u"inundation_input_stream_raster")

        self.horizontalLayout_6.addWidget(self.inundation_input_stream_raster)

        self.inundation_button_stream_raster = QPushButton(self.InundationZone)
        self.inundation_button_stream_raster.setObjectName(u"inundation_button_stream_raster")
        self.inundation_button_stream_raster.setCursor(QCursor(Qt.PointingHandCursor))

        self.horizontalLayout_6.addWidget(self.inundation_button_stream_raster)


        self.verticalLayout_2.addLayout(self.horizontalLayout_6)


        self.gridLayout_4.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.label_5 = QLabel(self.InundationZone)
        self.label_5.setObjectName(u"label_5")

        self.verticalLayout_6.addWidget(self.label_5)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.inundation_input_output_folder = QLineEdit(self.InundationZone)
        self.inundation_input_output_folder.setObjectName(u"inundation_input_output_folder")

        self.horizontalLayout_12.addWidget(self.inundation_input_output_folder)

        self.inundation_button_output_folder = QPushButton(self.InundationZone)
        self.inundation_button_output_folder.setObjectName(u"inundation_button_output_folder")

        self.horizontalLayout_12.addWidget(self.inundation_button_output_folder)


        self.verticalLayout_6.addLayout(self.horizontalLayout_12)


        self.gridLayout_4.addLayout(self.verticalLayout_6, 4, 0, 1, 1)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.inundation_progressbar_inundation_zone = QProgressBar(self.InundationZone)
        self.inundation_progressbar_inundation_zone.setObjectName(u"inundation_progressbar_inundation_zone")
        self.inundation_progressbar_inundation_zone.setValue(0)

        self.horizontalLayout_11.addWidget(self.inundation_progressbar_inundation_zone)

        self.inundation_button_generate_inundation_zone = QPushButton(self.InundationZone)
        self.inundation_button_generate_inundation_zone.setObjectName(u"inundation_button_generate_inundation_zone")

        self.horizontalLayout_11.addWidget(self.inundation_button_generate_inundation_zone)


        self.gridLayout_4.addLayout(self.horizontalLayout_11, 5, 0, 1, 1)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_3 = QLabel(self.InundationZone)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout_4.addWidget(self.label_3)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.inundation_input_confidence_limit = QComboBox(self.InundationZone)
        self.inundation_input_confidence_limit.setObjectName(u"inundation_input_confidence_limit")

        self.horizontalLayout_7.addWidget(self.inundation_input_confidence_limit)


        self.verticalLayout_4.addLayout(self.horizontalLayout_7)


        self.horizontalLayout_9.addLayout(self.verticalLayout_4)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label_4 = QLabel(self.InundationZone)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout_5.addWidget(self.label_4)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.inundation_input_volume = QLineEdit(self.InundationZone)
        self.inundation_input_volume.setObjectName(u"inundation_input_volume")
        sizePolicy.setHeightForWidth(self.inundation_input_volume.sizePolicy().hasHeightForWidth())
        self.inundation_input_volume.setSizePolicy(sizePolicy)

        self.horizontalLayout_10.addWidget(self.inundation_input_volume)


        self.verticalLayout_5.addLayout(self.horizontalLayout_10)


        self.horizontalLayout_9.addLayout(self.verticalLayout_5)


        self.gridLayout_4.addLayout(self.horizontalLayout_9, 3, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer_2, 6, 0, 1, 1)

        self.tabWidget.addTab(self.InundationZone, "")

        self.verticalLayout_22.addWidget(self.tabWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"pearpy", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"input earlier dsm (epoch 1)", None))
        self.mainpage_button_earlier_dsm.setText(QCoreApplication.translate("MainWindow", u"open dsm epoch 1", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"input later dsm (epoch 2)", None))
        self.mainpage_button_later_dsm.setText(QCoreApplication.translate("MainWindow", u"open dsm epoch 2", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"output folder", None))
        self.mainpage_button_output_folder.setText(QCoreApplication.translate("MainWindow", u"open output folder", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"Confidence Limit", None))
        self.label_22.setText(QCoreApplication.translate("MainWindow", u"Stream buffer size", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Stream Threshold", None))
        self.label_23.setText(QCoreApplication.translate("MainWindow", u"Maximum stream length percentage", None))
        self.label_11.setText("")
        self.mainpage_button_run.setText(QCoreApplication.translate("MainWindow", u"Run", None))
#if QT_CONFIG(tooltip)
        self.mainpage_check_preservedata.setToolTip(QCoreApplication.translate("MainWindow", u"Save processing data to output directory", None))
#endif // QT_CONFIG(tooltip)
        self.mainpage_check_preservedata.setText(QCoreApplication.translate("MainWindow", u"Preserve processing data", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"Output type:", None))
        self.radioButton_2.setText(QCoreApplication.translate("MainWindow", u"Raster", None))
        self.radioButton.setText(QCoreApplication.translate("MainWindow", u"Vector", None))
        self.mainpage_label_progressbar_overall.setText(QCoreApplication.translate("MainWindow", u"overalll progressbar", None))
        self.mainpage_label_progressbar_sub.setText(QCoreApplication.translate("MainWindow", u"sub progressbar", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.MainPage), QCoreApplication.translate("MainWindow", u"Main", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"input later dsm (epoch 2)", None))
        self.surfacehydro_button_later_dsm.setText(QCoreApplication.translate("MainWindow", u"open dsm 2", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"output directory", None))
        self.surfacehydro_button_output_folder.setText(QCoreApplication.translate("MainWindow", u"open output folder", None))
        self.surfacehydro_label_stream_threshold.setText(QCoreApplication.translate("MainWindow", u"Stream threshold", None))
        self.label_20.setText("")
        self.surfacehydro_button_run.setText(QCoreApplication.translate("MainWindow", u"Create surface hydro!", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.SurfaceHydroPage), QCoreApplication.translate("MainWindow", u"Surface Hydro", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"input flow direction raster (d8, esri style)", None))
        self.startingpoint_button_flow_directoin.setText(QCoreApplication.translate("MainWindow", u"open flow direction", None))
        self.label_21.setText(QCoreApplication.translate("MainWindow", u"input stream raster", None))
        self.startingpoint_button_stream.setText(QCoreApplication.translate("MainWindow", u"open stream raster", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"input earlier dsm (epoch 1)", None))
        self.startingpoint_button_earlier_dsm.setText(QCoreApplication.translate("MainWindow", u"open dsm epoch 1", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"input later dsm (epoch 2)", None))
        self.startingpoint_button_later_dsm.setText(QCoreApplication.translate("MainWindow", u"open dsm epoch 2", None))
        self.label_24.setText(QCoreApplication.translate("MainWindow", u"Stream buffer size", None))
        self.label_25.setText(QCoreApplication.translate("MainWindow", u"Maximum stream length percentage", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"output text location", None))
        self.startingpoint_button_output_location.setText(QCoreApplication.translate("MainWindow", u"open output", None))
        self.startingpoint_button_find_starting_point.setText(QCoreApplication.translate("MainWindow", u"Find starting point", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.InitialPoint), QCoreApplication.translate("MainWindow", u"Starting Point", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Input Coordinates File", None))
        self.inundation_button_coordinate_file.setText(QCoreApplication.translate("MainWindow", u"open text file", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"input fill raster from laharz", None))
        self.inundation_button_stream_raster.setText(QCoreApplication.translate("MainWindow", u"open raster", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Output Folder", None))
        self.inundation_button_output_folder.setText(QCoreApplication.translate("MainWindow", u"open folder", None))
        self.inundation_button_generate_inundation_zone.setText(QCoreApplication.translate("MainWindow", u"Generate!", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Confidence Limit", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Input Volume (optional)", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.InundationZone), QCoreApplication.translate("MainWindow", u"Inundation Zone", None))
    # retranslateUi

