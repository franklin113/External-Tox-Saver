"""
Extension classes enhance TouchDesigner components with python. An
extension is accessed via ext.ExtensionClassName from any operator
within the extended component. If the extension is promoted via its
Promote Extension parameter, all its attributes with capitalized names
can be accessed externally, e.g. op('yourComp').PromotedFunction().

Help: search "Extensions" in wiki
"""

from TDStoreTools import StorageManager
# TDF = op.TDModules.mod.TDFunctions

import os
from datetime import datetime
class eSaver:
	"""
	eSaver description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.myOp = ownerComp

		self.ExternalOpPar = self.myOp.par.Comptoexternalize
		
		self.DefaultPath = 'Tox/Objects/'

		#stored items (persistent across saves and re-initialization):
		storedItems = [
			# Only 'name' is required...
			{'name': 'ExternalToxs', 'default': [], 'readOnly': False,
			 						'property': True, 'dependable': True},
		]

		self.stored = StorageManager(self, ownerComp, storedItems)
		self.ToxLibrary = self.stored['ExternalToxs']

		self.Timer = self.myOp.op('timer1')

		#self.myOp.fetch('ToxLibrary',[],storeDefault = True)



	def BuildDirectory(self,baseOp = None) -> tuple : 
		if baseOp:
			relPath = baseOp#self.myOp.relativePath(baseOp)
			path = self.DefaultPath+ relPath
		else:
			relPath = self.myOp.relativePath(self._ExternalOp)
			path = self.DefaultPath+ relPath
			
		
		try:
			os.makedirs(path + '/Backup')
			self.Debug("Building path here: '", path,"'")

			#os.makedirs(path)
		except FileExistsError:
			pass
		return (path,relPath)

	def SaveTox(self, path,baseOP=None):
		# baseOP is an op object
		if baseOP:
			try:
				baseOP.save(path)
			except Exception as e:
				debug(e)			
		else:
			self._ExternalOp.save(path)


	def Externalize(self):
		assert self._ExternalOp, "Error Externalizing: Invalid path to op"
		self.Debug("Externalizing Tox", self.ExternalOpPar.val)
		
		paths = self.BuildDirectory()
		
		filepath = paths[0]
		relPath = paths[1]
		
		self.Saveincremental(relPath)
		self.MarkExternal(filepath)

		tempSet = set(self.ToxLibrary)

		if relPath not in tempSet:
			self.ToxLibrary.append(relPath)

		

		#self.Debug("Added Item to Tox Library: ")

	def MarkExternal(self,path):
		self._ExternalOp.tags = ['TOX']
		self._ExternalOp.color = (0,.05,.6)
		self._ExternalOp.par.externaltox = path
		self._ExternalOp.par.savebackup = self.myOp.par.Savebackup.eval()
		self._ExternalOp.par.reloadtoxonstart = self.myOp.par.Reloadtoxonstart.eval()
		self._ExternalOp.par.reloadbuiltin = self.myOp.par.Reloadbuiltin.eval()
		self._ExternalOp.par.reloadcustom = self.myOp.par.Reloadcustom.eval()

	def GetRelativePath(self):
		return self.myOp.relativePath(self._ExternalOp)

	def Cleartoxlist(self):
		self.ToxLibrary.clear()

	def Debug(self,*args):
		if self.myOp.par.Debug:
			print('Tox Saver Debug: ', *args)
			
	def GetTimestamp(self):
		now = datetime.now()
		timeString = now.strftime("---%m-%d-%Y--%H-%M-%S")
		return timeString

	def Saveincremental(self,baseOpPath,backupOnly = False):

		timestamp = self.GetTimestamp()

		baseOp = self.myOp.parent().op(baseOpPath)

		if baseOp:
			fullPath = self.BuildDirectory(baseOpPath)[0]

			fullPathWithFilename = fullPath + '/' + baseOp.name + '.tox'
			fullBackupPathWithTimestamp = fullPath + '/Backup/' + baseOp.name + timestamp + '.tox'
			try:

				if backupOnly == False:
					print("Save Location: ", fullPathWithFilename)

					self.SaveTox(fullPathWithFilename,baseOp)			# save the base

				print("Backup Location: ", fullBackupPathWithTimestamp)
				self.SaveTox(fullBackupPathWithTimestamp,baseOp)	# save a copy to the backup folder
				self.Debug("Successfuly saved primary and backup tox files: ", baseOp)
			except Exception as e:
				self.Debug("Error Saving the tox: \n\n", e)

	def Saveallcomps(self):

		for i in self.ToxLibrary:
			
			self.Saveincremental(i)

	def Savechangedcomps(self):
		self.Debug("Comps that have unsaved changes: ----")
		
		for i in self.ToxLibrary:
			curOp = self.myOp.parent().op(i)
			if curOp != None:
				try:
					if curOp.dirty:
						print("Showing",curOp.path)
						self.Saveincremental(i)
				except Exception as e:
					self.Debug("While Saved Changed Comps: ",e)

	def Saveallbackuponly(self):
		for i in self.ToxLibrary:
			self.Saveincremental(i,backupOnly=True)

	def StartAutoSave(self):
		self.Timer.par.start.pulse()

	def AutoSaveNow(self):
		self.Saveallbackuponly()

	@property
	def _ExternalOp(self):
		thisOp = None
		try:
			thisOp = self.ExternalOpPar.eval()
		except:
			print("Op Error: Op does not exist")
		
		return thisOp
