import sys
import pathlib
from fileinput import filename
from os.path import splitext

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QPixmap, QTextCursor

import smtplib
from email.mime import multipart
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

from stegano import lsb

imagename = ""
limit = 400 #limit for number of characters in input text box

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("main.ui", self)
        self.encryptImagesButton.clicked.connect(self.gotoscreen2)
        self.decryptImagesButton.clicked.connect(self.gotoscreen3)
        self.quitButton.clicked.connect(QCoreApplication.instance().quit)
        #self.decryptBackButton.clicked.connect(self.closeEvent)

    def gotoscreen2(self):
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    def gotoscreen3(self):
        widget.setCurrentIndex(widget.currentIndex() + 2)

class Screen2(QMainWindow):
    def __init__(self):
        super(Screen2, self).__init__()
        loadUi("encoder.ui", self)
        self.encryptorBackButton.clicked.connect(self.gotoscreen1)
        self.loginButton.clicked.connect(self.login)
        self.selectImageButton.clicked.connect(self.select_file)
        self.encryptImageButton.clicked.connect(self.encode_message)
        self.sendMailButton.clicked.connect(self.send_mail)
        self.mailComposition.textChanged.connect(self.updatecounter)

    def gotoscreen1(self):
        widget.setCurrentIndex(widget.currentIndex() - 1)

    def login(self):
        try:
            self.server = smtplib.SMTP("smtp-mail.outlook.com", 587)
            self.server.ehlo()
            self.server.starttls()
            self.server.ehlo()
            self.server.login(self.inputEmail.text(), self.emailPassword.text())

            self.inputEmail.setEnabled(False)
            self.emailPassword.setEnabled(False)
            self.loginButton.setEnabled(False)

            self.destinationEmail.setEnabled(True)
            self.emailSubject.setEnabled(True)
            self.mailComposition.setEnabled(True)
            self.selectedImagePath.setEnabled(True)
            self.selectImageButton.setEnabled(True)
            #self.encryptImageButton.setEnabled(False)
            self.sendMailButton.setEnabled(True)

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
        selectedImage = QFileDialog.getOpenFileName(self, "Select Image", "", "Image files (*.png)")
        fileName, _ = selectedImage
        if fileName:
            print(fileName)  
            imagename = fileName
            self.encryptImageButton.setEnabled(True)
            
    def encode_message(self):
        print('Button encrypt clicked')
        secret = lsb.hide(imagename, self.mailComposition.toPlainText()) 

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
        msg = self.mailComposition.toPlainText()
        global limit
        if len(msg)>limit:   
            print('Input testbox limit reached')
            TextData = msg[:limit]
            self.mailComposition.setText(TextData)  
            self.mailComposition.moveCursor(QTextCursor.End)
        msg = self.mailComposition.toPlainText()  
        self.charCounter.setText(f"Characters remaining: {round(int(limit - len(msg)),0)} chars")

    def attach_image(self):
        options = QFileDialog.Options()
        filenames, _ = QFileDialog.getOpenFileNames(self, "Select Image", "", "Image files (*.png)")
        
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
                self.msg['To'] = self.destinationEmail.text()
                self.msg['Subject'] = self.emailSubject.text()
                #self.msg.attach(MIMEText(self.mailComposition.toPlainText(), 'plain'))
                text = self.msg.as_string()
                self.server.sendmail(self.inputEmail.text(), self.destinationEmail.text(), text)
                message_box = QMessageBox()
                message_box.setText("Mail Sent!")
                message_box.exec()
            except:
                message_box = QMessageBox()
                message_box.setText("Sending Mail Failed!")
                message_box.exec()

class Screen3(QMainWindow):
    def __init__(self):
        super(Screen3, self).__init__()
        loadUi("decoder.ui", self)
        self.decryptBackButton.clicked.connect(self.gotoscreen1)
        self.decryptButton.clicked.connect(self.select_file)
        self.displayText.setText('')

    def gotoscreen1(self):
        widget.setCurrentIndex(widget.currentIndex() - 2)
    
    def select_file(self):
        # Open File Dialog
        global imageName
        options = QFileDialog.Options()
        selectedImage = QFileDialog.getOpenFileName(self, "Select Image", "", "Image files (*.png)")
        fname, _ = selectedImage

        # Output filename to screen
        if fname:
            self.encryptedImagePath.setText(selectedImage[0])
            self.decryptButton.setEnabled(False)
            print(fname)  
            imageName = fname

            self.displayText.setText('')  
            self.displayText.repaint() 
            pixmap = QPixmap(fname)
            self.imagePreview.setPixmap(pixmap)

            clear_message = lsb.reveal(fname)
            if (clear_message == None):
                no_message = "No message to extract from image"
                print("\n")
                print("No message to extract from image")
                self.displayText.setText(no_message)
                
                message_box = QMessageBox()
                message_box.setText("No message to extract from image")  
                
                self.decryptButton.setEnabled(True)
                self.decryptButton.repaint()
            else:
                print("\n")
                print("Message extracted from image - ", clear_message)
                self.displayText.setText(clear_message)  
                self.decryptButton.setEnabled(True)
                self.decryptButton.repaint()
                
        self.displayText.repaint()

app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()
mainwindow = MainWindow()
screen2 = Screen2()
screen3 = Screen3()
widget.addWidget(mainwindow)
widget.addWidget(screen2)
widget.addWidget(screen3)
widget.setFixedHeight(675)
widget.setFixedWidth(600)
widget.show()

try:
    sys.exit(app.exec_())
except:
    print("Exiting Application")