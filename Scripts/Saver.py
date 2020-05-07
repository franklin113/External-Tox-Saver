"""
Extension classes enhance TouchDesigner components with python. An
extension is accessed via ext.ExtensionClassName from any operator
within the extended component. If the extension is promoted via its
Promote Extension parameter, all its attributes with capitalized names
can be accessed externally, e.g. op('yourComp').PromotedFunction().

Help: search "Extensions" in wiki
"""
import os
import re
from datetime import datetime
from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions
import shutil

class Saver:
	"""
	Saver description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.myOp = ownerComp

	def Save(self, backupOnly=False, deleteBackups=False):
		
		togglePars, pathPars, pages = self.GetOpPars()

		ERROR_STATE = False

		# cycle through the parameters
		# if enabled, save the target op
		for curPar in togglePars:
			# if it's backupOnly, it means we are backup up everything
			if curPar.eval() or backupOnly == True:
				parName = curPar.name
				pathParName = parName + 'zzz2'	# the path parameter is the same name, except has a zzz2 at the end.
				pathToPar = getattr(self.myOp.par,pathParName)	# considering this is a string, we will retrieve the par object
				
				if pathToPar == None:
					print('SAVING ERROR  ', parName, '----------- No path supplied to path parameter --------------')
					raise TypeError

				targetOp = pathToPar.eval()	# the operator we will save

				# if op is not cooking, cook it before saving
				if targetOp.allowCooking != True:
					targetOp.allowCooking = True
					targetUncook = True
				else:
					targetUncook = False
			
				externalPath = targetOp.par.externaltox.eval()	# the external path designated in the target comp

				if externalPath == '' or externalPath == None:	# 
					print("INVALID SAVE LOCATION FOR ", targetOp.name)
					raise TypeError

				# we can save only backups by pulsing the button in system tab
				if backupOnly != True:
					try:
						savedPath = targetOp.save(externalPath)
					except Exception as e:
						debug('Error saving Main of: ', targetOp,'\n\nError: ', e)
				
				# this is where we handle backups
				backupPath, backupFilename = os.path.split(externalPath) # get path, filename
				
				# check if it's in it's own directory. Every comp will have it's own backup folder
				if os.path.basename(backupPath) != targetOp.name:
					backupPath = os.path.join(backupPath, targetOp.name)
				# put backups into the Tox\Backup folder
				backupPath = os.path.join(os.path.join(self.myOp.par.Savefoldername.val,'Backup'), backupPath)

				name, fileExt = os.path.splitext(backupFilename)		# get name and file extension

				backupFilename = name + self.GetTimestamp() + fileExt	# add a timestamp to the file

				# backupPath = os.path.join(backupPath, 'Backup')			# ensure the path is compatible

				try:
					os.makedirs(backupPath)
				except FileExistsError:
					pass		
				#print(externalPath, os.path.join(backupPath, backupFilename) )
				# copying the file is a lot faster than packaging it considering they are only 1kb.
			
				try:
					shutil.copyfile(externalPath, os.path.join(backupPath, backupFilename))
				except PermissionError as e:
					debug('Could not create backup of : ', targetOp.name, '\n\nError: ', e)


				## retrieve all the files in the directory, discard directories

				dirList = os.listdir(os.path.join(project.folder, backupPath))
				
				fullPath = []
				for i in dirList:
					newFilepath = os.path.join(backupPath, i)
					if os.path.isfile(newFilepath) == True:
						fullPath.append(newFilepath)

				if deleteBackups:
					for i in fullPath:
						os.remove(i)
				else:
					if len(dirList) > self.myOp.par.Maxbackups.eval():
						oldest_file = min(fullPath, key=os.path.getctime)
						os.remove(oldest_file)

				# reset op's original cook status
				if targetUncook == True:
					targetOp.allowCooking = False

				# print('Saving: ', targetOp.name, ' to : ', externalPath)

		if ERROR_STATE:
			print("THERE WAS AN ERROR SAVING --- \n\n ----- SEE ABOVE FOR DETAILS ---- \n\n ----")
			raise Exception

	def DeleteBackups(self):
		self.Save(deleteBackups=True)

	def GetTimestamp(self):
		now = datetime.now()
		timeString = now.strftime("---%m-%d-%Y--%H-%M-%S")
		return timeString

	def ToggleSaveAll(self, val):
		togglePars, pathPars, pages = self.GetOpPars()

		for i in togglePars:
			i.val = val

	def DetermineOpPaths(self, opToExternalize):
		# set external tox par
		fileExtension = '.tox'

		# Build a valid relative directory
		relativeDirectory, filename = os.path.split(parent().relativePath(opToExternalize))
		relativeDirectory = os.path.join(self.myOp.par.Savefoldername.val,relativeDirectory)
		# if Hasnochildren tag is present, we will NOT add this comp's name as a directory
		if self.myOp.par.Hasnochildrentag.eval() not in opToExternalize.tags:
			relativeDirectory = os.path.join(relativeDirectory, opToExternalize.name)	# the tox itself is a directory
		
		# now that we've added the comp name as a directory, put the filename in
		relativeFilePath = os.path.join(relativeDirectory, filename + fileExtension)

		# make sure tox is the head of the path
		absFolderpath = project.folder
		
		# join the relative directory into the project folder
		absFolderpath = os.path.join(absFolderpath, relativeDirectory)			
		
		# add the filename + extension to the abs path
		absSaveFilepath = os.path.join(absFolderpath, filename + fileExtension)  # make a legal path
		
		# for the hell of it, make sure it's a valid path. maek sure an incorrect \ or / got thrown in  there!
		absSaveFilepath = os.path.normpath(absSaveFilepath)					

		return absFolderpath, absSaveFilepath, relativeDirectory, relativeFilePath

	def ExternalizeOps(self, removeToxes=False):
		# find & loop thru ops that haven't been externalized yet

		compsToExternalize = self.myOp.parent().findChildren(type=COMP, key=lambda x: self.IsOpEligibleToBeExternalized(x, 'comp'))
		datsToExternalize = self.myOp.parent().findChildren(type=DAT, key=lambda x: self.IsOpEligibleToBeExternalized(x, 'dat'))

		opsToExternalize = compsToExternalize + datsToExternalize

		print(opsToExternalize)
		
		for i in opsToExternalize:
			
			absFolderpath, saveFilepath, relativeDirectory, relativeFilePath = self.DetermineOpPaths(i)
			
			try:
				os.makedirs(absFolderpath)
			except FileExistsError:
				pass

			if i.type == 'base' or i.type == 'container':
				# save out tox file
				i.par.externaltox = relativeFilePath
				i.save(saveFilepath)

				i.par.reloadbuiltin.val = False
				i.par.savebackup.val = False

			else:
				i.par.file = relativeFilePath
				i.save(saveFilepath)

				i.par.syncfile = True

		# now that all new ops have been externalized, find all externalized toxes
		if not removeToxes:
			self.FindExternalOps()
		else:
			pass

	def IsOpEligibleToBeExternalized(self, opToTest, compType):
		print(compType)
		if compType =='comp':
			return all((
				opToTest.par.externaltox.eval() == '',
				self.myOp.par.Toxtag.eval() in opToTest.tags
			))
		else:
			return all((
				#opToTest.par.file.eval() == '', 
				#self.myOp.par.Dattag.eval() in opToTest.tags
			))

	def UnexternalizeOps(self):
		opsToUnexternalize = self.myOp.parent().findChildren(type=COMP, key=lambda x: x.par.externaltox.eval() != '')

		for i in opsToUnexternalize:
			i.par.externaltox = ''	

		self.ClearOpPars()
		self.myOp.unstore('*')

	def FindExternalOps(self):
		externalOps = self.myOp.parent().findChildren(type=COMP, key=lambda x: x.par.externaltox.eval() != '')
		
		self.Tox = externalOps

		togglePars, pathPars, pages = self.GetOpPars()
		self.ClearOpPars()
		
		for i in externalOps:
			pat = r'_+'
			label = i.name
			name = i.name[0].upper() + i.name[1:].lower()
			name = re.sub(pat, '', name)
			newPar = pages[0].appendToggle(name,label=label)[0]
			if self.myOp.par.Saveall:
				newPar.val = True
			else:
				newPar.val = False
			newPar2 = pages[1].appendCOMP(name + 'zzz2')[0]
			newPar2.val = self.myOp.relativePath(i)
			newPar2.readOnly = True


	def GetOpPars(self):
		pages = self.myOp.customPages
		togglePars = set(pages[0].pars)
		pathPars = set(pages[1].pars)
		return (togglePars,pathPars, pages)

	def ClearOpPars(self):
		togglePars, pathPars, pages = self.GetOpPars()
		[x.destroy() for x in togglePars]
		[x.destroy() for x in pathPars]

	@property
	def Tox(self):
		tox = self.myOp.fetch('externalOps',tuple(),storeDefault=True)
		return tox
		
	@Tox.setter
	def Tox(self, val):
		assert type(val) == list, 'incorrect type assigned to Tox'
		self.myOp.store('externalOps', val)
		