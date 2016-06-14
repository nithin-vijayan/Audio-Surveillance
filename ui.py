import sys
from voiceid.sr import Voiceid
from voiceid.db import GMMVoiceDB
import urllib2 
from pydub import AudioSegment
from os import remove
import wave
import numpy as np
from PyQt4.QtCore import QString
from PyQt4 import QtGui,QtCore
from PyQt4.QtGui import QTextEdit,QTextCursor

global o
global filename
def voiceiden(fname,mname):
	db = GMMVoiceDB('models')
	fname=fname.strip('.wav')
	print fname
	db.add_model(str(fname),str(mname))
	out.insertHtml(QString("<font color=\"black\">%1</font>"))
	out.insertPlainText("\nModel "+mname+" Successfully added to database\n")

def noisered(fname):
	wr = wave.open(fname, 'r')
	par = list(wr.getparams()) 
	par[3] = 0
	ww = wave.open('filtered-talk.wav', 'w')
	ww.setparams(tuple(par)) 
	
	lowpass = 200 
	highpass = 6000 
	
	sz = wr.getframerate() 
	c = int(wr.getnframes()/sz) 
	for num in range(c):
	    da = np.fromstring(wr.readframes(sz), dtype=np.int16)
	    left, right = da[0::2], da[1::2] 
	    lf, rf = np.fft.rfft(left), np.fft.rfft(right)
	    lf[:lowpass], rf[:lowpass] = 0, 0  
	    lf[55:66], rf[55:66] = 0, 0  
	    lf[highpass:], rf[highpass:] = 0,0 
	    nl, nr = np.fft.irfft(lf), np.fft.irfft(rf)
	    ns = np.column_stack((nl,nr)).ravel().astype(np.int16)
	    ww.writeframes(ns.tostring())
	 
	wr.close()
	ww.close()
	fname='filtered-talk.wav'
	sptotex(fname)


def showsp():
	db = GMMVoiceDB('models')
	spk= str(db.get_speakers())
	out.insertHtml(QString("<font color=\"black\">%1</font>").arg(spk))
def voicerec(fname):
	db = GMMVoiceDB('models')
	v = Voiceid(db,fname)
	v.extract_speakers()
	txt=''
	for c in v.get_clusters():
	    cl= v.get_cluster(c)
	    cluster=str(cl)
	    cluster=cluster.split(' ')
	    cluster=cluster[1]
	    cluster=cluster.strip('(')
	    cluster=cluster.strip(')')
	    txt=txt+'Speaker : '+cluster
	    seg=str(cl.print_segments())
	    txt=txt+'\n'+seg
	out.insertPlainText(txt+"\n")


def sptotex(fname):
	def speechtotext():
		url = 'https://www.google.com/speech-api/v2/recognize?output=json&lang=en-us&key=AIzaSyCQVcq2zEstH2O5W_tLPRPi7MjJb4jGXlU'
		flac=open("temp.flac","rb").read()
		header = {'Content-Type' : 'audio/x-flac; rate=8000'}
		req = urllib2.Request(url, flac, header)
		data = urllib2.urlopen(req)
	
		
		a=data.read()
		print a
		a=a.replace('"','')
		print a
		b=a.split(',')
		print b
		c=b[0].split(':')
		print c		
		out=c[4]
		print out	
		remove("temp.flac")
		return(out)
	
	File=fname
	o=''
	new = AudioSegment.from_wav(File)
	length=len(new)
	i=0
	blk=12000
	j=blk
	while (j<length):
		audiosplit = new[i:j]
		i=i+blk
		j=j+blk
		audiosplit.export("temp.flac", format="flac")
		o=o+' '+speechtotext()
		
	audiosplit = new[i:]
	audiosplit.export("temp.flac", format="flac")
	o=o+' '+speechtotext()
	
	text_file = open("susp.txt", "r")
	keyword_list =  text_file.read().split()
	
	
	x=''
	sent=o.split(' ')
	out.insertPlainText("Audio transcript : ")
	for i in sent:
		for j in keyword_list:
			
			if (i==j):
				f=0
				out.insertPlainText(" ")
				out.insertHtml(QString("<font color=\"red\">%1</font>").arg(i))
				break	
			else:
				f=1
		if(f==1):
			out.insertPlainText(" ")
			out.insertHtml(QString("<font color=\"black\">%1</font>").arg(i))
	
	
	
	
	
		

class Example(QtGui.QWidget):
 
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()
        
    def initUI(self):
        
        self.setToolTip('Audio surveillance')
        global out
	out = QtGui.QTextEdit(self)
	
	
    	self.lbl=QtGui.QLabel('', self)
	lbl1 = QtGui.QLabel('Add model', self)
	lbl2 = QtGui.QLabel('Show model', self)
	lbl4 = QtGui.QLabel('Analyze model', self)
	lbl5 = QtGui.QLabel('Output:', self)
	 
	lbl1.move(30, 30)
	lbl2.move(30,70)
	lbl4.move(30, 110)
	lbl5.move(25, 160)
	self.lbl.move(38, 35)
	admd = QtGui.QPushButton('Add model', self)
	anmd = QtGui.QPushButton('Analyze', self)
	shmd = QtGui.QPushButton('Show Models', self)
	
	out.setGeometry(27, 190, 350, 290)  


	admd.setToolTip('Add new model to database')
        admd.resize(admd.sizeHint())
        admd.move(155,30) 
	admd.clicked.connect(self.showDialogad)
	

	anmd.setToolTip('Analyze given sample')
        anmd.resize(anmd.sizeHint())
        anmd.move(155, 70) 
	anmd.clicked.connect(self.showDialogan)

	shmd.setToolTip('Show saved models in database')
        shmd.resize(shmd.sizeHint())
        shmd.move(155,110 )  
	shmd.clicked.connect(showsp)   
	
	out.setReadOnly(True)
	out.setLineWrapMode(1)

	sb = out.verticalScrollBar()
	sb.setValue(sb.maximum())

	
        
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
	
        self.setGeometry(300, 100, 400, 500)
        self.setWindowTitle('Audio surveillance')    
        self.show()
	
    def showfiledialog(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 
            'Enter model name:')
        
        if ok:
	    return text
	    


    def showDialogad(self):
	fname = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file',"","wav files (*.wav)",'/home'))
	mname=self.showfiledialog()
	voiceiden(fname,mname)

    def showDialogan(self):
	fname = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file',"","wav files (*.wav)",'/home'))
	voicerec(fname)
	noisered(fname)

	
    	
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
 

