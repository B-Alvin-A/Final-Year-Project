from email.mime import multipart
import smtplib
import sys
from tkinter import messagebox

from PyQt5.uic import loadUi
from fileinput import filename
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QTextCursor

from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

import pathlib
from stegano import lsb
from os.path import splitext

imagename = ""
limit = 400 #limit for number of characters in input text box

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("encoder.ui", self)

        self.pushButton.clicked.connect(self.login)
        self.pushButton_4.clicked.connect(self.select_file)
        self.pushButton_5.clicked.connect(self.encode_message)
        self.pushButton_3.clicked.connect(self.send_mail)
        self.textEdit.textChanged.connect(self.updatecounter)
    
    def login(self):
        try:
            self.server = smtplib.SMTP("smtp-mail.outlook.com", 587)
            self.server.ehlo()
            self.server.starttls()
            self.server.ehlo()
            self.server.login(self.lineEdit.text(), self.lineEdit_2.text())

            self.lineEdit.setEnabled(False)
            self.lineEdit_2.setEnabled(False)
            self.pushButton.setEnabled(False)

            self.lineEdit_5.setEnabled(True)
            self.lineEdit_6.setEnabled(True)
            self.textEdit.setEnabled(True)
            self.lineEdit_7.setEnabled(True)
            self.pushButton_4.setEnabled(True)
            #self.pushButton_5.setEnabled(False)
            self.pushButton_3.setEnabled(True)

            self.msg = MIMEMultipart()
        except smtplib.SMTPAuthenticationError:
            message_box = QMessageBox()
            message_box.setText("Invalid Login Info!")
            message_box.exec()
        except:
            message_box = QMessageBox()
            message_box.setText("Login Failed!")
            message_box.exec()

    def select_file(self):
        print('Button select image clicked')
        self.openFileNameDialog()

    def openFileNameDialog(self):
        global imagename
        options = QFileDialog.Options()
        selectedImage = QFileDialog.getOpenFileName(self, "Select Image", "", "Image files (*.png *.jpg *.jpeg *.gif)")
        fileName, _ = selectedImage
        if fileName:
            print(fileName)  
            imagename = fileName
            self.pushButton_5.setEnabled(True)
            
    def encode_message(self):
        print('Button encrypt clicked')
        secret = lsb.hide(imagename, self.textEdit.toPlainText()) 

        file_name,extension = splitext(imagename)
        file_name += '-message'
        file_name += extension

        file = pathlib.Path(file_name)
        if file.exists ():
            print ("encrypted file already exist")

            buttonReply = QMessageBox.question(self, 'Encrypted file already exist', "Do you wish to overwrite?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if buttonReply == QMessageBox.Yes: #files already exist but overwrite
                print('Overwrite file')
                secret.save(file_name)
                print("\n")
                print("Message saved to image")
            else: #files exist so don't overwrite
                print('Cancel save file')
        else:        
            secret.save(file_name)
            print("\n")
            print("Message saved to image")
        
        self.attach_image()

    def updatecounter(self):
        msg = self.textEdit.toPlainText()
        global limit
        if len(msg)>limit:   
            print('Input testbox limit reached')
            TextData = msg[:limit]
            self.textEdit.setText(TextData)  
            self.textEdit.moveCursor(QTextCursor.End)
        msg = self.textEdit.toPlainText()  
        self.label_4.setText(f"Characters remaining: {round(int(limit - len(msg)),0)} chars")

    def attach_image(self):
        options = QFileDialog.Options()
        filenames, _ = QFileDialog.getOpenFileNames(self, "Select Image", "", "Image files (*.png *.jpg *.jpeg *.gif)")
        
        if filenames != []:
            for filename in filenames:
                attachment = open(filename, 'rb')
                filename = filename[filename.rfind("/") + 1:]

                p = MIMEBase('application' , 'octet-stream')
                p.set_payload(attachment.read())
                encoders.encode_base64(p)
                p.add_header("Content-Disposition", f"attachment; filename={filename}")
                self.msg.attach(p)
                if not self.label_3.text().endswith(": "):
                    self.label_3.setText(self.label_3.text() + ",")
                self.label_3.setText(self.label_3.text() + " " + filename)

    def send_mail(self):
        dialog = QMessageBox()
        dialog.setText("Do you want to send this mail?")
        dialog.addButton(QPushButton("Yes"), QMessageBox.YesRole)
        dialog.addButton(QPushButton("No"), QMessageBox.NoRole)

        if dialog.exec_() == 0:
            try:
                self.msg['From'] = "BSE22-22"
                self.msg['To'] = self.lineEdit_5.text()
                self.msg['Subject'] = self.lineEdit_6.text()
                #self.msg.attach(MIMEText(self.textEdit.toPlainText(), 'plain'))
                text = self.msg.as_string()
                self.server.sendmail(self.lineEdit.text(), self.lineEdit_5.text(), text)
                message_box = QMessageBox()
                message_box.setText("Mail Sent!")
                message_box.exec()
            except:
                message_box = QMessageBox()
                message_box.setText("Sending Mail Failed!")
                message_box.exec()

app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()
mainwindow = MainWindow()

widget.addWidget(mainwindow)

widget.setFixedHeight(675)
widget.setFixedWidth(550)
widget.show()

try:
    sys.exit(app.exec_())
except:
    print("Exiting Application")