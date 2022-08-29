#importing libraries
import sys

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QPixmap

from stegano import lsb

#from fileinput import filename
#from tkinter import StringVar
#from tokenize import String
#from tkinter import *
#from tkinter.filedialog import *
#from PIL import ImageTk,Image
#from tkinter import messagebox

imageName = ""

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("decoder.ui", self)

        self.pushButton_3.clicked.connect(self.select_file)
        self.textEdit.setText('')

    def select_file(self):
        # Open File Dialog
        global imageName
        options = QFileDialog.Options()
        selectedImage = QFileDialog.getOpenFileName(self, "Select Image", "", "Image files (*.png)")
        fname, _ = selectedImage

        # Output filename to screen
        if fname:
            self.label_4.setText(selectedImage[0])
            self.pushButton_3.setEnabled(False)
            print(fname)  
            imageName = fname

            self.textEdit.setText('')  
            self.textEdit.repaint() 
            pixmap = QPixmap(fname)
            self.label_6.setPixmap(pixmap)

            clear_message = lsb.reveal(fname)
            if (clear_message == None):
                no_message = "No message to extract from image"
                print("\n")
                print("No message to extract from image")
                self.textEdit.setText(no_message)
                
                message_box = QMessageBox()
                message_box.setText("No message to extract from image")  
                
                self.pushButton_3.setEnabled(True)
                self.pushButton_3.repaint()
            else:
                print("\n")
                print("Message extracted from image - ", clear_message)
                self.textEdit.setText(clear_message)  
                self.pushButton_3.setEnabled(True)
                self.pushButton_3.repaint()
             
                
        self.textEdit.repaint()

app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()
mainwindow = MainWindow()

widget.addWidget(mainwindow)

widget.setFixedHeight(580)
widget.setFixedWidth(600)
widget.show()

try:
    sys.exit(app.exec_())
except:
    print("Exiting Application")