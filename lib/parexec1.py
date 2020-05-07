# me - this DAT
# par - the Par object that has changed
# val - the current value
# prev - the previous value
# 
# Make sure the corresponding toggle is enabled in the Parameter Execute DAT.

def onValueChange(par, prev):
	# use par.eval() to get current value
	if par.name == 'Saveall':
		parent().ToggleSaveAll(par.eval())

	return

def onPulse(par):
	if par.name == 'Externalizeops':
		parent().ExternalizeOps()
		
	elif par.name == 'Unexternalizeops':
		parent().UnexternalizeOps()
		
	elif par.name == 'Findexternalops':
		parent().FindExternalOps()

	elif par.name == 'Clearparameters':
		parent().ClearOpPars()

	elif par.name == 'Backupall':
		parent().Save(backupOnly=True)
		
	elif par.name == 'Deletebackups':
		parent().DeleteBackups()
		
	elif par.name == 'Generatethumbs':
		parent().GenerateThumbs()
	
	elif par.name == 'Clearthumbs':
		parent().ClearThumbs()
	
	
	return

def onExpressionChange(par, val, prev):
	return

def onExportChange(par, val, prev):
	return

def onEnableChange(par, val, prev):
	return

def onModeChange(par, val, prev):
	return
	