# External-Tox-Saver
A tool for externalizing your tox files. 


## Usage
Bring "External-Tox-Saver.tox" into your project. It should immediately search for comps with the tag EXTERNALTOX. 
If this is the first time you've opened it, you can start externalizing your tox files.

#Externalizing Tox Files
Set the 'Comp to Externalize' parameter to the path of your comp, then hit Externalize.

This will build a new directory in your project's folder to mirror your network. It will also create a "Backup" folder.
Anytime this saves a tox, it saves the primary file as well as incrementally saves the tox into the backup folder.

