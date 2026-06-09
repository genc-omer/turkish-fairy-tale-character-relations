from analizClass import MetinAnaliz
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QGraphicsScene

from iliskiClass import CharacterRelations

class Ui_MainWindow(object):
        def setupUi(self, MainWindow):
                self.iliski = CharacterRelations(story_path=None)
                MainWindow.setObjectName("MainWindow")
                MainWindow.resize(1200, 750)
                palette = QtGui.QPalette()
                brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
                brush = QtGui.QBrush(QtGui.QColor(221, 239, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
                brush = QtGui.QBrush(QtGui.QColor(238, 247, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
                brush = QtGui.QBrush(QtGui.QColor(110, 119, 127))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
                brush = QtGui.QBrush(QtGui.QColor(147, 159, 170))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
                brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
                brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
                brush = QtGui.QBrush(QtGui.QColor(221, 239, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
                brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
                brush = QtGui.QBrush(QtGui.QColor(238, 247, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
                brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
                brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 127))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                # palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Accent, brush)
                brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
                brush = QtGui.QBrush(QtGui.QColor(221, 239, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
                brush = QtGui.QBrush(QtGui.QColor(238, 247, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
                brush = QtGui.QBrush(QtGui.QColor(110, 119, 127))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
                brush = QtGui.QBrush(QtGui.QColor(147, 159, 170))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
                brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
                brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
                brush = QtGui.QBrush(QtGui.QColor(221, 239, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
                brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
                brush = QtGui.QBrush(QtGui.QColor(238, 247, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
                brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
                brush = QtGui.QBrush(QtGui.QColor(0, 0, 0, 127))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                # palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Accent, brush)
                brush = QtGui.QBrush(QtGui.QColor(110, 119, 127))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
                brush = QtGui.QBrush(QtGui.QColor(221, 239, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
                brush = QtGui.QBrush(QtGui.QColor(238, 247, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
                brush = QtGui.QBrush(QtGui.QColor(110, 119, 127))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
                brush = QtGui.QBrush(QtGui.QColor(147, 159, 170))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
                brush = QtGui.QBrush(QtGui.QColor(110, 119, 127))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
                brush = QtGui.QBrush(QtGui.QColor(110, 119, 127))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
                brush = QtGui.QBrush(QtGui.QColor(221, 239, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
                brush = QtGui.QBrush(QtGui.QColor(221, 239, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
                brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
                brush = QtGui.QBrush(QtGui.QColor(221, 239, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
                brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
                brush = QtGui.QBrush(QtGui.QColor(110, 119, 127, 127))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                # palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Accent, brush)
                MainWindow.setPalette(palette)
                self.centralwidget = QtWidgets.QWidget(MainWindow)
                self.centralwidget.setObjectName("centralwidget")
                self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
                self.verticalLayout.setObjectName("verticalLayout")
                self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(1)
                sizePolicy.setHeightForWidth(self.stackedWidget.sizePolicy().hasHeightForWidth())
                self.stackedWidget.setSizePolicy(sizePolicy)
                self.stackedWidget.setObjectName("stackedWidget")
                self.page = QtWidgets.QWidget()
                self.page.setObjectName("page")
                self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.page)
                self.horizontalLayout_3.setObjectName("horizontalLayout_3")
                self.hikayeYoluLine = QtWidgets.QLineEdit(self.page)
                self.hikayeYoluLine.setMinimumSize(QtCore.QSize(0, 35))
                self.hikayeYoluLine.setObjectName("hikayeYoluLine")
                self.horizontalLayout_3.addWidget(self.hikayeYoluLine)
                self.hikayeSecButton = QtWidgets.QPushButton(self.page)
                self.hikayeSecButton.setMinimumSize(QtCore.QSize(90, 30))
                palette = QtGui.QPalette()
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
                brush = QtGui.QBrush(QtGui.QColor(41, 128, 185))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
                brush = QtGui.QBrush(QtGui.QColor(41, 128, 185))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
                brush = QtGui.QBrush(QtGui.QColor(41, 128, 185))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 128))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.PlaceholderText, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
                brush = QtGui.QBrush(QtGui.QColor(41, 128, 185))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
                brush = QtGui.QBrush(QtGui.QColor(41, 128, 185))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
                brush = QtGui.QBrush(QtGui.QColor(41, 128, 185))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 128))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.PlaceholderText, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
                brush = QtGui.QBrush(QtGui.QColor(41, 128, 185))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
                brush = QtGui.QBrush(QtGui.QColor(41, 128, 185))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
                brush = QtGui.QBrush(QtGui.QColor(41, 128, 185))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
                brush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 128))
                brush.setStyle(QtCore.Qt.SolidPattern)
                palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.PlaceholderText, brush)
                self.hikayeSecButton.setPalette(palette)
                self.hikayeSecButton.setStyleSheet("QPushButton {\n"
        "    /* Butonun normal durumu */\n"
        "    background-color: #2980b9; /* Mavi */\n"
        "    color: white; /* Beyaz yazı */\n"
        "    border: none;\n"
        "    padding: 10px 20px;\n"
        "    border-radius: 5px;\n"
        "}\n"
        "\n"
        "QPushButton:hover {\n"
        "    /* Butonun üzerine gelindiğinde (hover) durumu */\n"
        "    background-color: #3498db; /* Daha koyu mavi */\n"
        "    color: #f0f0f0; /* Hafif kırık beyaz yazı */\n"
        "}\n"
        "\n"
        "QPushButton:pressed {\n"
        "    /* Butona basıldığında (tıklandığında) durumu */\n"
        "    background-color: #1a5276; /* Çok daha koyu mavi */\n"
        "}")
                self.hikayeSecButton.setObjectName("hikayeSecButton")
                self.horizontalLayout_3.addWidget(self.hikayeSecButton)
                self.analizEtButton = QtWidgets.QPushButton(self.page)
                self.analizEtButton.setMinimumSize(QtCore.QSize(90, 30))
                self.analizEtButton.setStyleSheet("QPushButton {\n"
        "    /* Butonun normal durumu */\n"
        "    background-color: #2980b9; /* Mavi */\n"
        "    color: white; /* Beyaz yazı */\n"
        "    border: none;\n"
        "    padding: 10px 20px;\n"
        "    border-radius: 5px;\n"
        "}\n"
        "\n"
        "QPushButton:hover {\n"
        "    /* Butonun üzerine gelindiğinde (hover) durumu */\n"
        "    background-color: #3498db; /* Daha koyu mavi */\n"
        "    color: #f0f0f0; /* Hafif kırık beyaz yazı */\n"
        "}\n"
        "QPushButton:pressed {\n"
        "    /* Butona basıldığında (tıklandığında) durumu */\n"
        "    background-color: #1a5276; /* Çok daha koyu mavi */\n"
        "}")
                self.analizEtButton.setObjectName("analizEtButton")
                self.horizontalLayout_3.addWidget(self.analizEtButton)
                self.stackedWidget.addWidget(self.page)
                self.page_2 = QtWidgets.QWidget()
                self.page_2.setObjectName("page_2")
                self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.page_2)
                self.horizontalLayout_2.setObjectName("horizontalLayout_2")
                self.duyguDegisimGrafigiButton = QtWidgets.QPushButton(self.page_2)
                self.duyguDegisimGrafigiButton.setMinimumSize(QtCore.QSize(0, 30))
                self.duyguDegisimGrafigiButton.setStyleSheet("QPushButton {\n"
        "    /* Butonun normal durumu */\n"
        "    background-color: #2980b9; /* Mavi */\n"
        "    color: white; /* Beyaz yazı */\n"
        "    border: none;\n"
        "    padding: 10px 20px;\n"
        "    border-radius: 5px;\n"
        "}\n"
        "\n"
        "QPushButton:hover {\n"
        "    /* Butonun üzerine gelindiğinde (hover) durumu */\n"
        "    background-color: #3498db; /* Daha koyu mavi */\n"
        "    color: #f0f0f0; /* Hafif kırık beyaz yazı */\n"
        "}\n"
        "QPushButton:pressed {\n"
        "    /* Butona basıldığında (tıklandığında) durumu */\n"
        "    background-color: #1a5276; /* Çok daha koyu mavi */\n"
        "}")
                self.duyguDegisimGrafigiButton.setObjectName("duyguDegisimGrafigiButton")
                self.horizontalLayout_2.addWidget(self.duyguDegisimGrafigiButton)
                self.girisButton = QtWidgets.QPushButton(self.page_2)
                self.girisButton.setMinimumSize(QtCore.QSize(0, 30))
                self.girisButton.setStyleSheet("QPushButton {\n"
        "    /* Butonun normal durumu */\n"
        "    background-color: #2980b9; /* Mavi */\n"
        "    color: white; /* Beyaz yazı */\n"
        "    border: none;\n"
        "    padding: 10px 20px;\n"
        "    border-radius: 5px;\n"
        "}\n"
        "\n"
        "QPushButton:hover {\n"
        "    /* Butonun üzerine gelindiğinde (hover) durumu */\n"
        "    background-color: #3498db; /* Daha koyu mavi */\n"
        "    color: #f0f0f0; /* Hafif kırık beyaz yazı */\n"
        "}\n"
        "QPushButton:pressed {\n"
        "    /* Butona basıldığında (tıklandığında) durumu */\n"
        "    background-color: #1a5276; /* Çok daha koyu mavi */\n"
        "}")
                self.girisButton.setObjectName("girisButton")
                self.horizontalLayout_2.addWidget(self.girisButton)
                self.gelismeButton = QtWidgets.QPushButton(self.page_2)
                self.gelismeButton.setMinimumSize(QtCore.QSize(0, 30))
                self.gelismeButton.setStyleSheet("QPushButton {\n"
        "    /* Butonun normal durumu */\n"
        "    background-color: #2980b9; /* Mavi */\n"
        "    color: white; /* Beyaz yazı */\n"
        "    border: none;\n"
        "    padding: 10px 20px;\n"
        "    border-radius: 5px;\n"
        "}\n"
        "\n"
        "QPushButton:hover {\n"
        "    /* Butonun üzerine gelindiğinde (hover) durumu */\n"
        "    background-color: #3498db; /* Daha koyu mavi */\n"
        "    color: #f0f0f0; /* Hafif kırık beyaz yazı */\n"
        "}\n"
        "QPushButton:pressed {\n"
        "    /* Butona basıldığında (tıklandığında) durumu */\n"
        "    background-color: #1a5276; /* Çok daha koyu mavi */\n"
        "}")
                self.gelismeButton.setObjectName("gelismeButton")
                self.horizontalLayout_2.addWidget(self.gelismeButton)
                self.sonucButton = QtWidgets.QPushButton(self.page_2)
                self.sonucButton.setMinimumSize(QtCore.QSize(0, 30))
                self.sonucButton.setStyleSheet("QPushButton {\n"
        "    /* Butonun normal durumu */\n"
        "    background-color: #2980b9; /* Mavi */\n"
        "    color: white; /* Beyaz yazı */\n"
        "    border: none;\n"
        "    padding: 10px 20px;\n"
        "    border-radius: 5px;\n"
        "}\n"
        "\n"
        "QPushButton:hover {\n"
        "    /* Butonun üzerine gelindiğinde (hover) durumu */\n"
        "    background-color: #3498db; /* Daha koyu mavi */\n"
        "    color: #f0f0f0; /* Hafif kırık beyaz yazı */\n"
        "}\n"
        "QPushButton:pressed {\n"
        "    /* Butona basıldığında (tıklandığında) durumu */\n"
        "    background-color: #1a5276; /* Çok daha koyu mavi */\n"
        "}")
                self.sonucButton.setObjectName("sonucButton")
                self.horizontalLayout_2.addWidget(self.sonucButton)
                self.genelButton = QtWidgets.QPushButton(self.page_2)
                self.genelButton.setMinimumSize(QtCore.QSize(0, 30))
                self.genelButton.setStyleSheet("QPushButton {\n"
        "    /* Butonun normal durumu */\n"
        "    background-color: #2980b9; /* Mavi */\n"
        "    color: white; /* Beyaz yazı */\n"
        "    border: none;\n"
        "    padding: 10px 20px;\n"
        "    border-radius: 5px;\n"
        "}\n"
        "\n"
        "QPushButton:hover {\n"
        "    /* Butonun üzerine gelindiğinde (hover) durumu */\n"
        "    background-color: #3498db; /* Daha koyu mavi */\n"
        "    color: #f0f0f0; /* Hafif kırık beyaz yazı */\n"
        "}\n"
        "\n"
        "QPushButton:pressed {\n"
        "    /* Butona basıldığında (tıklandığında) durumu */\n"
        "    background-color: #1a5276; /* Çok daha koyu mavi */\n"
        "}")
                self.genelButton.setObjectName("genelButton")
                self.horizontalLayout_2.addWidget(self.genelButton)

                self.geriButton = QtWidgets.QPushButton(self.page_2)
                self.geriButton.setMinimumSize(QtCore.QSize(0, 30))
                self.geriButton.setStyleSheet("QPushButton {\n"
        "    /* Butonun normal durumu */\n"
        "    background-color: #2980b9; /* Mavi */\n"
        "    color: white; /* Beyaz yazı */\n"
        "    border: none;\n"
        "    padding: 10px 20px;\n"
        "    border-radius: 5px;\n"
        "}\n"
        "\n"
        "QPushButton:hover {\n"
        "    /* Butonun üzerine gelindiğinde (hover) durumu */\n"
        "    background-color: #3498db; /* Daha koyu mavi */\n"
        "    color: #f0f0f0; /* Hafif kırık beyaz yazı */\n"
        "}\n"
        "QPushButton:pressed {\n"
        "    /* Butona basıldığında (tıklandığında) durumu */\n"
        "    background-color: #1a5276; /* Çok daha koyu mavi */\n"
        "}")
                self.geriButton.setObjectName("geriButton")
                self.horizontalLayout_2.addWidget(self.geriButton)


                self.stackedWidget.addWidget(self.page_2)
                self.verticalLayout.addWidget(self.stackedWidget)
                self.bottomPart = QtWidgets.QWidget(self.centralwidget)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(7)
                sizePolicy.setHeightForWidth(self.bottomPart.sizePolicy().hasHeightForWidth())
                self.bottomPart.setSizePolicy(sizePolicy)
                self.bottomPart.setObjectName("bottomPart")
                self.horizontalLayout = QtWidgets.QHBoxLayout(self.bottomPart)
                self.horizontalLayout.setObjectName("horizontalLayout")
                self.widget = QtWidgets.QWidget(self.bottomPart)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
                sizePolicy.setHorizontalStretch(2)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
                self.widget.setSizePolicy(sizePolicy)
                self.widget.setMinimumSize(QtCore.QSize(0, 0))
                self.widget.setStyleSheet("background-color: #edf6fc;\n"
        "border-radius:20px;\n"
        "")
                self.widget.setObjectName("widget")
                self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget)
                self.verticalLayout_3.setContentsMargins(-1, -1, 9, -1)
                self.verticalLayout_3.setSpacing(6)
                self.verticalLayout_3.setObjectName("verticalLayout_3")
                self.label_2 = QtWidgets.QLabel(self.widget)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(1)
                sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
                self.label_2.setSizePolicy(sizePolicy)
                self.label_2.setStyleSheet("background-color: #2980b9; color:white;\n"
        "border-radius:5px;\n"
        "")
                self.label_2.setAlignment(QtCore.Qt.AlignCenter)
                self.label_2.setObjectName("label_2")
                self.verticalLayout_3.addWidget(self.label_2)
                self.widget_3 = QtWidgets.QWidget(self.widget)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(10)
                sizePolicy.setHeightForWidth(self.widget_3.sizePolicy().hasHeightForWidth())
                self.widget_3.setSizePolicy(sizePolicy)
                self.widget_3.setStyleSheet("background-color:rgba(196, 229, 255, 200);")
                self.widget_3.setObjectName("widget_3")
                self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.widget_3)
                self.horizontalLayout_5.setObjectName("horizontalLayout_5")
                self.IliskiGraphicsView = QtWidgets.QGraphicsView(self.widget_3)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(self.IliskiGraphicsView.sizePolicy().hasHeightForWidth())
                self.IliskiGraphicsView.setSizePolicy(sizePolicy)
                self.IliskiGraphicsView.setStyleSheet("border-radius:10px;")
                self.IliskiGraphicsView.setObjectName("IliskiGraphicsView")
                self.horizontalLayout_5.addWidget(self.IliskiGraphicsView)
                self.verticalLayout_3.addWidget(self.widget_3)
                self.horizontalLayout.addWidget(self.widget)
                self.widget_2 = QtWidgets.QWidget(self.bottomPart)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
                sizePolicy.setHorizontalStretch(1)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(self.widget_2.sizePolicy().hasHeightForWidth())
                self.widget_2.setSizePolicy(sizePolicy)
                self.widget_2.setStyleSheet("background-color: #edf6fc;\n"
        "border-radius:20px;\n"
        "")
                self.widget_2.setObjectName("widget_2")
                self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget_2)
                self.verticalLayout_2.setObjectName("verticalLayout_2")
                self.label = QtWidgets.QLabel(self.widget_2)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(1)
                sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
                self.label.setSizePolicy(sizePolicy)
                self.label.setStyleSheet("background-color: #2980b9; color:white;\n"
        "border-radius:5px;\n"
        "")
                self.label.setAlignment(QtCore.Qt.AlignCenter)
                self.label.setObjectName("label")
                self.verticalLayout_2.addWidget(self.label)
                self.widget_4 = QtWidgets.QWidget(self.widget_2)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(10)
                sizePolicy.setHeightForWidth(self.widget_4.sizePolicy().hasHeightForWidth())
                self.widget_4.setSizePolicy(sizePolicy)
                self.widget_4.setStyleSheet("background-color:rgba(196, 229, 255, 200);")
                self.widget_4.setObjectName("widget_4")
                self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.widget_4)
                self.horizontalLayout_4.setObjectName("horizontalLayout_4")
                self.karakterlerListView = QtWidgets.QListView(self.widget_4)
                self.karakterlerListView.setObjectName("karakterlerListView")
                self.horizontalLayout_4.addWidget(self.karakterlerListView)
                self.verticalLayout_2.addWidget(self.widget_4)
                self.horizontalLayout.addWidget(self.widget_2)
                self.verticalLayout.addWidget(self.bottomPart)
                MainWindow.setCentralWidget(self.centralwidget)
                self.menubar = QtWidgets.QMenuBar(MainWindow)
                self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 25))
                self.menubar.setObjectName("menubar")
                MainWindow.setMenuBar(self.menubar)
                self.statusbar = QtWidgets.QStatusBar(MainWindow)
                self.statusbar.setObjectName("statusbar")
                MainWindow.setStatusBar(self.statusbar)

                self.retranslateUi(MainWindow)
                self.stackedWidget.setCurrentIndex(0)
                QtCore.QMetaObject.connectSlotsByName(MainWindow)

        def retranslateUi(self, MainWindow):
                _translate = QtCore.QCoreApplication.translate
                MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
                self.hikayeSecButton.setText(_translate("MainWindow", "Hikaye Seç"))
                self.analizEtButton.setText(_translate("MainWindow", "Analiz Et"))
                self.duyguDegisimGrafigiButton.setText(_translate("MainWindow", "Duygu Değişimi Grafiği"))
                self.girisButton.setText(_translate("MainWindow", "Giriş"))
                self.gelismeButton.setText(_translate("MainWindow", "Gelişme"))
                self.sonucButton.setText(_translate("MainWindow", "Sonuç"))
                self.genelButton.setText(_translate("MainWindow", "Genel"))
                self.geriButton.setText(_translate("MainWindow", "Geri Git"))
                self.label_2.setText(_translate("MainWindow", "İlişkiler"))
                self.label.setText(_translate("MainWindow", "Karakterler"))

        def geri_git(self):
                # Geri gitmek için stackedWidget'in indeksini 0 yap
                self.stackedWidget.setCurrentIndex(0)
                #grafik alanını temizle
                self.IliskiGraphicsView.setScene(None)
                #listeyi temizle
                self.karakterlerListView.setModel(QtGui.QStandardItemModel())

                self.iliski.story_path = None
                self.iliski.variation_to_character = {}
                self.iliski.text = ""
                self.iliski.segments = []
                self.iliski.all_relations = []
                self.iliski.past_sentences = []

        def hikaye_sec(self):
                dosya_yolu, _ = QtWidgets.QFileDialog.getOpenFileName(
                        None,                           # parent widget
                        "Hikaye Dosyasını Seç",         # başlık
                        "",                             # varsayılan dizin
                        "Metin Dosyaları (*.txt);;Tüm Dosyalar (*)"  # filtre
                )
                if dosya_yolu:
                        self.hikayeYoluLine.setText(dosya_yolu)
        def analiz_et(self):
                hikaye_yolu = self.hikayeYoluLine.text()
                if hikaye_yolu:
                        print(f"Hikaye analizi yapılıyor: {hikaye_yolu}")
                        self.stackedWidget.setCurrentIndex(1)
                        analiz = MetinAnaliz(hikaye_yolu)
                        sirali_gruplar = analiz.tum_islemler()
                        model = QtGui.QStandardItemModel()
                        for karakter, gecis_sayisi in sirali_gruplar:
                                item = QtGui.QStandardItem(f"-> {karakter} ({gecis_sayisi} kez geçiş)")
                                item.setEditable(False)
                                model.appendRow(item)
                        self.karakterlerListView.setModel(model)

                        self.iliski.story_path = hikaye_yolu
                        self.iliski.load_text()
                        self.iliski.split_sentence_dialog()
                        self.iliski.process()
                             
                else:
                        QtWidgets.QMessageBox.warning(None, "Hata", "Lütfen bir hikaye dosyası seçin.")

        def giris_iliski(self):
                pixmap = self.iliski.section_based_graph("Giriş Bölümü")
                scene = QGraphicsScene()
                view_size = self.IliskiGraphicsView.size()
                scaled_pixmap = pixmap.scaled(
                    view_size,
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation
                )
                scene.addPixmap(scaled_pixmap)
                self.IliskiGraphicsView.setScene(scene)
                self.IliskiGraphicsView.fitInView(scene.sceneRect(), QtCore.Qt.KeepAspectRatio)
        def gelisme_iliski(self):
                pixmap = self.iliski.section_based_graph("Gelişme Bölümü")
                scene = QGraphicsScene()
                view_size = self.IliskiGraphicsView.size()
                scaled_pixmap = pixmap.scaled(
                    view_size,
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation
                )
                scene.addPixmap(scaled_pixmap)
                self.IliskiGraphicsView.setScene(scene)
                self.IliskiGraphicsView.fitInView(scene.sceneRect(), QtCore.Qt.KeepAspectRatio)
        def sonuc_iliski(self):
                pixmap = self.iliski.section_based_graph("Sonuç Bölümü")
                scene = QGraphicsScene()
                view_size = self.IliskiGraphicsView.size()
                scaled_pixmap = pixmap.scaled(
                    view_size,
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation
                )
                scene.addPixmap(scaled_pixmap)
                self.IliskiGraphicsView.setScene(scene)
                self.IliskiGraphicsView.fitInView(scene.sceneRect(), QtCore.Qt.KeepAspectRatio)

        def duygu_degisim_grafigi_goster(self):
                pixmap = self.iliski.draw_emotion_curve()
                scene = QGraphicsScene()
                view_size = self.IliskiGraphicsView.size()
                scaled_pixmap = pixmap.scaled(
                    view_size,
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation
                )
                scene.addPixmap(scaled_pixmap)
                self.IliskiGraphicsView.setScene(scene)
                self.IliskiGraphicsView.fitInView(scene.sceneRect(), QtCore.Qt.KeepAspectRatio)

        def genel_iliski(self):
                pixmap = self.iliski.overall_relation_graph()
                scene = QGraphicsScene()
                view_size = self.IliskiGraphicsView.size()
                scaled_pixmap = pixmap.scaled(
                    view_size,
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation
                )
                scene.addPixmap(scaled_pixmap)
                self.IliskiGraphicsView.setScene(scene)
                self.IliskiGraphicsView.fitInView(scene.sceneRect(), QtCore.Qt.KeepAspectRatio)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
