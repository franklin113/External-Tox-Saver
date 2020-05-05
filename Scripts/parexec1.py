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
	if par.name == 'Externalizetoxes':
		parent().ExternalizeToxes()
		
	elif par.name == 'Unexternalizetoxes':
		parent().UnexternalizeToxes()
		
	elif par.name == 'Findexternal':
		parent().FindExternalToxes()

	elif par.name == 'Clearparameters':
		parent().ClearOpPars()

	elif par.name == 'Backupall':
		parent().Save(backupOnly=True)
		
	elif par.name == 'Deletebackups':
		parent().DeleteBackups()
	
	
	return

def onExpressionChange(par, val, prev):
	return

def onExportChange(par, val, prev):
	return

def onEnableChange(par, val, prev):
	return

def onModeChange(par, val, prev):
	return
	