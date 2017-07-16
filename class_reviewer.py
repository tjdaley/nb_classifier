# JDBOT - Classification Reviewer
#
# Reads through a file of json-formatted objects and lets the user
# review the classification of each record.
#
# Copyright (c) 2017 by Thomas J. Daley, J.D.
# Author: Thomas J. Daley, J.D. <tjd@jdbot.us>
# URL: <http://www.jdbot.us>
# For license information, see LICENSE.TXT
#

from lib import labels
import json
import os
import wx

# # # # # # # # # #
# C L A S S E S 
# # # # # # # # # #
class AnalyzeWindow(wx.Frame):
	"""
	Class to present the GUI to the user
	"""
	def __init__(self, *args, **kwargs):
		"""
		Constructor.
		
		Example:
		
		aw = AnalyzeWindow(None, title="Class Analyzer", size=(900, 300))
		"""
		super(AnalyzeWindow, self).__init__(*args, **kwargs)
		self.InitUI()
		self.Centre()
		self.Show(True)
	
	def InitUI(self):
		"""
		Initialize the UI and prompt the user to open a file to process
		"""
		self._initMenuBar()
		self._initLayout()
		
		# Bindings
		self.Bind(wx.EVT_BUTTON, self.OnButtonClicked)
		
		# We can't even start without an input file
		self.OnOpen(None)
		
	def _initLayout(self):
		"""
		Lay out all the controls on the window.
		"""
		panel = wx.Panel(self)

		# Create a font object
		font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
		font.SetPointSize(9)

		# Vertical sizer will contain multiple horizontal sizers as rows
		vbox = wx.BoxSizer(wx.VERTICAL)

		# First Row: The text we need to categorize
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		st1 = wx.StaticText(panel, label='Text')
		st1.SetFont(font)
		hbox1.Add(st1, flag=wx.RIGHT, border=8)
		tc = wx.TextCtrl(panel)
		self._textControl = tc
		hbox1.Add(tc, proportion=1)
		vbox.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
		
		# The existing class assignment
		hboxExisting = wx.BoxSizer(wx.HORIZONTAL)
		label = wx.StaticText(panel, label='Current')
		label.SetFont(font)
		hboxExisting.Add(label, flag=wx.RIGHT, border=8)
		
		label = wx.StaticText(panel, label="(unassigned)")
		self._existingClass = "(unassigned)"
		self._existingClassLabel = label
		label.SetFont(font)
		hboxExisting.Add(label, flag=wx.RIGHT, border=8)
		vbox.Add(hboxExisting, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
		
		# Button to keep the current class assignment
		button = wx.Button(panel, label="KEEP", name="*KEEP")
		hboxExisting.Add(button, flag=wx.RIGHT)

		# Button to skip this record, i.e., move to next record without writing this one out
		button = wx.Button(panel, label="DELETE", name="*KILL")
		hboxExisting.Add(button, flag=wx.RIGHT)

		vbox.Add((-1, 10))

		# Buttons for classes that can be assigned to the text
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		st2 = wx.StaticText(panel, label='Reassign to...')
		st2.SetFont(font)
		hbox2.Add(st2)
		vbox.Add(hbox2, flag=wx.LEFT | wx.TOP, border=10)

		vbox.Add((-1, 10))

		# Grid of buttons, one for each class label
		hbox3 = wx.GridSizer(8,5,50)
	
		for label in sorted(labels.LABELS):
			button = MyButton(panel, label=label, size=(70, 30), name=label)
			hbox3.Add(button)

		vbox.Add(hbox3, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, 
			border=10)
		
		panel.SetSizer(vbox)
		
	def _initMenuBar(self):
		"""
		Initialize the menu bar. Maybe we don't really need this.
		"""
		menubar = wx.MenuBar()
		fileMenu = wx.Menu()
		
		# File -> Open
		openItem = wx.MenuItem(fileMenu, wx.ID_OPEN)
		fileMenu.Append(openItem)
		self.Bind(wx.EVT_MENU, self.OnOpen, openItem)

		# File -> Save
		#saveItem = wx.MenuItem(fileMenu, wx.ID_SAVE)
		#fileMenu.Append(saveItem)
		#self.Bind(wx.EVT_MENU, self.OnSave, saveItem)
		
		fileMenu.AppendSeparator()
		
		# File -> Quit
		quitItem = wx.MenuItem(fileMenu, wx.ID_EXIT)
		fileMenu.Append(quitItem)
		self.Bind(wx.EVT_MENU, self.OnQuit, quitItem)
		
		# Connect the menu bar
		menubar.Append(fileMenu, "&File")
		self.SetMenuBar(menubar)
		
		
	def OnQuit(self, e):
		"""
		When user indicates he or she wants to quit the program, end grecefully.
		"""
		self.EndRun()
		
	def OnOpen(self, e):
		"""
		Prompt for an input file to process. Open the file and the output file.
		
		The file must be arranged so that there is one json-encoded object on each line. Each
		json-encoded object must have a "descrption" and "class" property.
		
		N.B. FOR NOW, ALL OTHER PROPERTIES ARE LOST.
		"""
		openFileDialog = wx.FileDialog(self, "Open Training file", "", "",
			"JSON files (*.json)|*.json", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
			
		if openFileDialog.ShowModal() == wx.ID_CANCEL:
			return
			
		self._fin = open(openFileDialog.GetPath(), "r")
		path, filename = os.path.split(openFileDialog.GetPath())
		newName = path  + os.path.sep + "REV-" + filename
		self._fout = open(newName, "w")
		self.GetNextLine()
	
	def OnButtonClicked(self, e):
		"""
		Button event handler.
		"""
		buttonName = e.GetEventObject().GetName()
		className = None
		
		if buttonName == "*KEEP":
			className = self._existingClass
		elif buttonName != "*KILL":
			className = buttonName
		
		if className != None:
			obj = {"description" : self._textControl.GetValue(), "class": className}
			s = json.dumps(obj)
			self._fout.write(s+"\n")
			
		self.GetNextLine()
		e.Skip()
		
	def GetNextLine(self):
		"""
		Try to read the next line from the file. If we encounter a blank line, we're done.
		"""
		line = self._fin.readline()

		if len(line) == 0:
			wx.MessageBox("All records processed", "DONE!", wx.ICON_INFORMATION | wx.OK)
			self.EndRun()
			
		else:
			line = line[:-1]
			obj = json.loads(line)
			self._textControl.SetValue(obj["description"])
			self._existingClass = obj["class"]
			self._existingClassLabel.SetLabel(obj["class"])
			
	def EndRun(self):
		"""
		A clean end.
		"""
		try:
			self._fin.close()
			self._fout.close()
		except:
			print ("Good bye")

		exit()
		

class MyButton(wx.Button):
	"""
	Custom class-assignment button.
	"""
    
	def __init__(self, *args, **kwargs):
		super(MyButton, self).__init__(*args, **kwargs)
		self.Bind(wx.EVT_BUTTON, self.OnButtonClicked)

	def OnButtonClicked(self, e):
		# Send this event to the containing window
		e.Skip()

# # # # # # # # # #
# F U N C T I O N S 
# # # # # # # # # #
def main():
	app = wx.App()
	AnalyzeWindow(None, title="Class Analyzer", size=(900, 300))
	app.MainLoop()
	
# # # # # # # # # #
# M A I N
# # # # # # # # # #
if __name__ == "__main__":
	main()