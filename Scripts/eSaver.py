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
		self.toxTag = 'EXTERNALTOX'
		
		self.Rebuildtoxlist()

		#self.myOp.fetch('ToxLibrary',[],storeDefault = True)



	def BuildDirectory(self,baseOpPath : str) -> tuple : 
		# baseOpPath should be a relative path from the saver comp

		assert type(baseOpPath) == str, "Passed an operator object into Build Directory method. String Expected."

		if baseOpPath:
			relPath = baseOpPath#self.myOp.relativePath(baseOp)
			path = self.DefaultPath+ relPath

		try:
			os.makedirs(path + '/Backup')
			self.Debug("Building path here: '", path,"'")

		except FileExistsError:
			pass

		return (path,relPath)

	def SaveTox(self, path,baseOP):
		# baseOP is an op object
		try:
			baseOP.save(path)
		except Exception as e:
			debug(e)			

	def Externalize(self):
		extOp = self.ExternalOpPar.eval()
		assert extOp, "Error Externalizing: Invalid path to op"
		
		self.Debug("Externalizing Tox", extOp)
		
		paths = self.BuildDirectory(self.GetRelativePath(extOp))
		
		filepath = paths[0]
		relPath = paths[1]
		
		self.SaveIncremental(relPath)
		self.MarkExternal(extOp,filepath)

		tempSet = set(self.ToxLibrary)

		if relPath not in tempSet:
			self.ToxLibrary.append(relPath)

	def MarkExternal(self,externalOp : op, path):
		
		externalOp.tags.add(self.toxTag)
		externalOp.color = (0,.05,.6)
		externalOp.par.externaltox = path
		externalOp.par.savebackup = False
		externalOp.par.reloadtoxonstart = self.myOp.par.Reloadtoxonstart.eval()
		externalOp.par.reloadbuiltin = self.myOp.par.Reloadbuiltin.eval()
		externalOp.par.reloadcustom = self.myOp.par.Reloadcustom.eval()

	def FindDirtyComps(self):
		dirtyOps = self.myOp.parent().findChildren(tags = [self.toxTag], key = lambda x: x.dirty)
		return dirtyOps

	def Rebuildtoxlist(self):
		compsWithTag = self.myOp.parent().findChildren(tags=[self.toxTag])
		self.ToxLibrary = [self.GetRelativePath(x) for x in compsWithTag]
		if self.myOp.par.Debug:
			print("Found Operators with tag: ", self.toxTag)
			for i in self.ToxLibrary:
				print(i)

	def Printdirtycomps(self):
		print("Found the below comps to be dirty: ")
		for i in self.FindDirtyComps():
			print(i)

	def GetRelativePath(self,opObject : op):
		return self.myOp.relativePath(opObject)

	def Cleartoxlist(self):
		self.ToxLibrary.clear()

	def Debug(self,*args):
		if self.myOp.par.Debug:
			print('Tox Saver Debug: ', *args)
			
	def GetTimestamp(self):
		now = datetime.now()
		timeString = now.strftime("---%m-%d-%Y--%H-%M-%S")
		return timeString

	def SaveIncremental(self,baseOpPath,backupOnly = False):

		timestamp = self.GetTimestamp()

		baseOp = self.myOp.parent().op(baseOpPath)

		assert baseOp, "Operator passed to SaveIncremental does not exist."

		fullPath = self.BuildDirectory(baseOpPath)[0]

		fullPathWithFilename = fullPath + '/' + baseOp.name + '.tox'
		fullBackupPathWithTimestamp = fullPath + '/Backup/' + baseOp.name + timestamp + '.tox'
		try:

			if backupOnly == False:
				self.SaveTox(fullPathWithFilename,baseOp)			# save the base
				self.Debug("Save Location: ", fullPathWithFilename)


			self.Debug("Backup Location: " + fullPath + '/Backup/')
			self.SaveTox(fullBackupPathWithTimestamp,baseOp)	# save a copy to the backup folder
			self.Debug("Saved Tox Files: ", baseOp)
		except Exception as e:
			self.Debug("Error Saving the tox: \n\n", e)

	def Saveallcomps(self):

		for i in self.ToxLibrary:
			
			self.SaveIncremental(i)

	def Savechangedcomps(self):
		
		for i in self.ToxLibrary:
			curOp = self.myOp.parent().op(i)
			if curOp != None:
				try:
					if curOp.dirty:
						self.Debug("Saving: ",curOp.path)
						self.SaveIncremental(i)
				except Exception as e:
					self.Debug("While Saved Changed Comps: ",e)

	# def Saveallbackuponly(self):
	# 	for i in self.ToxLibrary:
	# 		self.SaveIncremental(i,backupOnly=True)

	def StartAutoSave(self):
		self.Timer.par.start.pulse()

	def AutoSaveNow(self):
		self.Saveallbackuponly()

