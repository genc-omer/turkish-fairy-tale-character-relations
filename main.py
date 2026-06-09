from mainwindow import Ui_MainWindow
from PyQt5.QtWidgets import QApplication
import sys

from PyQt5.QtWidgets import QMainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    MainWindow.setWindowTitle("Karakter ve İlişki Analizi")
    ui.hikayeSecButton.clicked.connect(ui.hikaye_sec)
    ui.analizEtButton.clicked.connect(ui.analiz_et)
    ui.girisButton.clicked.connect(ui.giris_iliski)
    ui.gelismeButton.clicked.connect(ui.gelisme_iliski)
    ui.sonucButton.clicked.connect(ui.sonuc_iliski)
    ui.duyguDegisimGrafigiButton.clicked.connect(ui.duygu_degisim_grafigi_goster)
    ui.genelButton.clicked.connect(ui.genel_iliski)
    ui.geriButton.clicked.connect(ui.geri_git)
 
    sys.exit(app.exec_())
    