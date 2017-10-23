################################################################################################################
#import
################################################################################################################
from __future__ import absolute_import, print_function, division
import pypylon
import matplotlib.pyplot as plt
import tqdm
import numpy as np
import cv2
import sys
import datetime
import os
from multiprocessing import Pool

import datetime
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as patches
import matplotlib.dates as md
import time
import matplotlib as mpl
mpl.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


################################################################################################################
#initialize
################################################################################################################

xrange = 85.1*2
yrange = 64.1*2
xwindow = 42
ywindow = 42
xcenter = 4.51
ycenter = 4.66
xPixels = 2592
yPixels = 1944
xwindow_target = 28.4
ywindow_target = 28.4

#definition of position on image
xlowPixels = (int)(xPixels / 2 * (1 - xwindow / xrange + 2 * xcenter / xrange))
xupPixels = (int)(xPixels / 2 * (1 + xwindow / xrange + 2 * xcenter / xrange))
ylowPixels = (int)(yPixels / 2 * (1 - ywindow / yrange + 2 * ycenter / yrange))
yupPixels = (int)(yPixels / 2 * (1 + ywindow / yrange + 2 * ycenter / yrange))
xwidthPixels = (int)(xPixels*xwindow / xrange)
ywidthPixels = (int)(yPixels*ywindow / yrange)
xlowPixels_target = (int)(xPixels / 2 * (1 - xwindow_target / xrange + 2 * xcenter / xrange))
xupPixels_target = (int)(xPixels / 2 * (1 + xwindow_target / xrange + 2 * xcenter / xrange))
ylowPixels_target = (int)(yPixels / 2 * (1 - ywindow_target / yrange + 2 * ycenter / yrange))
yupPixels_target = (int)(yPixels / 2 * (1 + ywindow_target / yrange + 2 * ycenter / yrange))

xlowPixels_target_cm = (xlowPixels_target - xlowPixels)
xupPixels_target_cm = (xupPixels_target - xlowPixels)
ylowPixels_target_cm = (ylowPixels_target - ylowPixels)
yupPixels_target_cm = (yupPixels_target - ylowPixels)

xwidthPixels_target = (int)(xPixels*xwindow_target / xrange)
ywidthPixels_target = (int)(yPixels*ywindow_target / yrange)




################################################################################################################
#class ApplicationWindow
################################################################################################################
class ApplicationWindow(QMainWindow):
	def __init__(self):
		super().__init__()

		self.initUI()

	def initUI(self):
		fig_width = 4
		fig_height = 3
		self.colormap = ColorMap(self, width=fig_width, height=fig_height, dpi=100)
		self.graph_gross = GraphGross(self, width=fig_width, height=fig_height, dpi=100)
		self.colormap2 = ColorMap(self, width=fig_width, height=fig_height, dpi=100)
		self.graph_gross2 = GraphGross(self, width=fig_width, height=fig_height, dpi=100)
		self.vol_console = VolConsole() 

		saveButton = QPushButton("Save")
		saveButton.clicked.connect(self.save)

		bpm = QHBoxLayout()
		bpm.addWidget(self.colormap)
		bpm.addWidget(self.graph_gross)
		bpm.addWidget(self.colormap2)
		bpm.addWidget(self.graph_gross2)


		vbox = QVBoxLayout()
		vbox.addLayout(bpm)
		vbox.addWidget(self.vol_console)
		vbox.addWidget(saveButton)
		base = QWidget(self)
		base.setLayout(vbox)
		self.setCentralWidget(base)


		self.statusBar().showMessage('Ready')
		self.setWindowTitle("Profile Monitor Viewer")
		self.show()


		self.timer = QTimer(self)
		self.timer.timeout.connect(self.update)
		self.timer.start(1)		


	def update(self):
		image = cam.grab_image()
		self.colormap.updateFigure(image)
		self.graph_gross.updateFigure(image)
		self.colormap2.updateFigure(image)
		self.graph_gross2.updateFigure(image)

	def save(self):
		now_date = datetime.datetime.now()
		path = now_date.strftime('%Y%m%d')
		print(os.path.isfile(path))
		if os.path.isdir(path) is False:
			print("mkdir "+path )
			os.mkdir(path)
		image = cam.grab_image() 
		filename =now_date.now().strftime('%Y%m%d-%H%M%S')    
		cv2.imwrite("./"+path+"/"+filename+".tif",image )     
		aw.grab().save("./"+path+"/ss-"+filename+".png")

		f = open("./"+path+"/"+filename+".txt", 'w') 
		f.write(filename) 
		f.close() 


		try:
			elog_command = "cat " + "\"./"+path+"/"+filename+".txt\"  | elog -h localhost -p 8080 -l offline -a Author=\"tanaka\" -a ion=\"Rb\" -f \"./"+path+"/"+filename+".tif\" -f \"./"+path+"/ss-"+filename+".png\""
			res = os.system(elog_command)
			self.statusBar().showMessage("Save ./"+path+"/"+filename+".tif & ./"+path+"/ss-"+filename+".png")
		except:
			self.statusBar().showMessage("Save failed")



################################################################################################################
#class matplotlib canvas
################################################################################################################

class mplCanvas(FigureCanvas):
	def __init__(self, parent=None, width=6, height=5, dpi=100):
		self.fig = mpl.figure.Figure(figsize=(width, height), dpi=dpi)
		self.axes = self.fig.add_subplot(111)
		self.axes.hold(False)
		super(mplCanvas, self).__init__(self.fig)
		self.setParent(parent)

		self.initFigure()

	def initTime(self):
		ser.write("*".encode())
		self.data = ser.readline().strip().rsplit()            
		self.t0 = float(self.data[0])



################################################################################################################
#class colormap
################################################################################################################

class ColorMap(mplCanvas):
	def __init__(self, *args, **kwargs):
		mplCanvas.__init__(self, *args, **kwargs)

	def initFigure(self):
		pass

	def updateFigure(self,image):
		self.axes.cla()
		self.axes.add_patch(
			patches.Rectangle(
				(xlowPixels_target-xlowPixels, ylowPixels_target-ylowPixels),
				ywidthPixels_target,
				ywidthPixels_target,
				fill=False      # remove background
			)
		)
		self.axes.imshow(image)
		self.draw()



################################################################################################################
#class graph for gross
################################################################################################################

class GraphGross(mplCanvas):
	def __init__(self, *args, **kwargs):
		mplCanvas.__init__(self, *args, **kwargs)

	def initFigure(self):
		self.start_date = datetime.datetime.now()
		self.grosslog = []
		self.timelog = []

	def updateFigure(self,image):
		self.grosslog.append(np.sum(image))
		now_date =datetime.datetime.now()     
		self.timelog.append(now_date)
		if now_date - self.start_date > datetime.timedelta(seconds=10) : 
			self.timelog.pop(0)
			self.grosslog.pop(0)            
		self.axes.plot(self.timelog,self.grosslog)
		xfmt = md.DateFormatter('%H:%M:%S')
		self.axes.xaxis.set_major_formatter(xfmt)
		self.axes.tick_params(axis='x', labelsize=6)
		self.axes.tick_params(axis='y', labelsize=6)
		self.draw()

################################################################################################################
#class voltage list
################################################################################################################
class VolConsole(QWidget):
	def __init__(self):
		super().__init__()
		self.init_ui()

        
	def init_ui(self):
		vol_list = {\
		"VC":201, "VA":202,\
		"VL1p":202, "VL1m":202, "VL2p":202, "VL2m":202,\
		"ST1p":202, "ST1m":202,\
		"Dp":202, "Dm":202,\
		"ST2p":202, "ST2m":202, \
		"Q1ACp":202, "Q1ACm":202, \
		"BPM1front":202, "BPM1back":202, "BPM1phospher":202, \
		}

		for name, assign in vol_list.items():  
			print("read "+str(name))
			exec("self.vol_"+name+" = VolPart(\""+str(name)+"\","+str(assign)+")")


		self.vol_ionizer = QHBoxLayout()
		self.vol_ionizer.addWidget(self.vol_VC)
		self.vol_ionizer.addWidget(self.vol_VA)
		self.vol_ionizer.addWidget(self.vol_VL1p)		
		self.vol_ionizer.addWidget(self.vol_VL1m)	
		self.vol_ionizer.addWidget(self.vol_VL2p)		
		self.vol_ionizer.addWidget(self.vol_VL2m)	

		self.vol_transport1 = QHBoxLayout()
		self.vol_transport1.addWidget(self.vol_ST1p)		
		self.vol_transport1.addWidget(self.vol_ST1m)	
		self.vol_transport1.addWidget(self.vol_Dp)		
		self.vol_transport1.addWidget(self.vol_Dm)	
		self.vol_transport1.addWidget(self.vol_ST2p)		
		self.vol_transport1.addWidget(self.vol_ST2m)

		self.vol_transport2 = QHBoxLayout()
		self.vol_transport2.addWidget(self.vol_Q1ACp)		
		self.vol_transport2.addWidget(self.vol_Q1ACm)

		self.vol_bpm1 = QHBoxLayout()
		self.vol_bpm1.addWidget(self.vol_BPM1front)		
		self.vol_bpm1.addWidget(self.vol_BPM1back)
		self.vol_bpm1.addWidget(self.vol_BPM1phospher)

		self.vol_console = QVBoxLayout()
		self.vol_console.addLayout(self.vol_ionizer)
		self.vol_console.addLayout(self.vol_transport1)
		self.vol_console.addLayout(self.vol_transport2)
		self.vol_console.addLayout(self.vol_bpm1)
		self.setLayout(self.vol_console)

################################################################################################################
#class voltage part
################################################################################################################
class VolPart(QWidget):
	def __init__(self,name,assign):
		super().__init__()
		self.init_ui(name,assign)

        
	def init_ui(self,name,assign):


		self.vol_box = QHBoxLayout()
		self.vol_assign = QLabel(name)
		self.vol_set = QLineEdit("0")
		self.vol_read = QLabel('10')
		self.cur_leak = QLabel('3')
		self.vol_box.addWidget(self.vol_assign,1)
		self.vol_box.addWidget(self.vol_set,1)
		self.vol_box.addWidget(self.vol_read,1)
		self.vol_box.addWidget(self.cur_leak,1)
		self.setContentsMargins(5,2,5,2)
		self.setLayout(self.vol_box)

################################################################################################################
#prepare the camera
################################################################################################################

print('Build against pylon library version:', pypylon.pylon_version.version)

available_cameras = pypylon.factory.find_devices()
print('Available cameras are', available_cameras)

# Grep the first one and create a camera for it
cam = pypylon.factory.create_device(available_cameras[-1])

# We can still get information of the camera back
print('Camera info of camera object:', cam.device_info)

# Open camera and grep some images
cam.open()
# Hard code exposure time
cam.properties['ExposureTime'] = 10000.0
cam.properties['Gain'] = 23
cam.properties['PixelFormat'] = 'Mono8'
cam.properties['Width'] = xwidthPixels
cam.properties['Height'] = ywidthPixels
cam.properties['OffsetX'] = xlowPixels

cam.properties['OffsetY'] = ylowPixels

# Go to full available speed
cam.properties['DeviceLinkThroughputLimitMode'] = 'Off'

for key in cam.properties.keys():
	try:
		value = cam.properties[key]
	except IOError:
		value = '<NOT READABLE>'

	print('{0} ({1}):\t{2}'.format(key, cam.properties.get_description(key), value))


################################################################################################################
#open Mainwindow
################################################################################################################

if __name__ == "__main__":
	app = QApplication(sys.argv)
	aw = ApplicationWindow()
	aw.show()
	app.exec_()