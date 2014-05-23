from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import sys
import os
import hashlib

def createDriveDirectory(name, parentId):
	files = drive.ListFile({'q': "'%s' in parents and title = '%s'" % (parentId, name)}).GetList()
	if len(files) > 0:
		print "Found folder %s in parent %s" % (name, parentId)
		return files[0]['id']
	else:
		folder = drive.CreateFile({'title':name, 'mimeType':'application/vnd.google-apps.folder', 
			'parents': [{"kind": "drive#fileLink","id": parentId}]})
		print "Creating folder %s in parent %s" % (name, parentId)
		folder.Upload()	
		return folder['id']		

def createDriveFile(filepath, parentId):
	name = os.path.basename(filepath)
	files = drive.ListFile({'q': "'%s' in parents and title = '%s'" % (parentId, name)}).GetList()
	if len(files) > 0:
		_file = files[0]
		print "Found file %s in parent %s. Computing checksum...." % (name, parentId)
		if _file['md5Checksum'] == md5(filepath):
			# same file
			print "No change"
			return _file['id']		
	else:
		_file = drive.CreateFile({'title': name, 
			'parents': [{"kind": "drive#fileLink","id": parentId}]})

	_file.SetContentFile(filepath)
	print "Uploading %s..." % filepath
	_file.Upload()
	return _file['id']

def md5(filepath):
	with open(filepath) as _file:
		return hashlib.md5(_file.read()).hexdigest()

gauth = GoogleAuth()
gauth.LocalWebserverAuth() 

drive = GoogleDrive(gauth)
backupFolder = drive.ListFile({'q': "'root' in parents and title = '___BACKUP'"}).GetList()
if len(backupFolder) > 0:
	backupFolder = backupFolder[0]
else:
	print "Unexpected error: Can't find backup folder."
	exit()

folderToBackup = sys.argv[1]
if not os.path.isdir(folderToBackup):
	print "Only folders can be backed up"
	exit()

if folderToBackup.endswith("/"):
	folderToBackup = folderToBackup[:-1]

# so same name as returned by os.walk
folderToBackup = os.path.abspath(folderToBackup)

driveIds = {}
name = os.path.basename(folderToBackup)
folderToBackupId = createDriveDirectory(name, backupFolder["id"])
driveIds[folderToBackup] = folderToBackupId	
print "ID of folder to backup: %s" % folderToBackupId

for root, dirs, files in os.walk(folderToBackup):
    	if 'selected' in dirs:
        	dirs.remove('selected')
	
	if root in driveIds:
		rootDirId = driveIds[root]
		print "RootId:" + rootDirId
	else:
		print "Unexpected: Cannot find Id. Abort"
		exit()			 	

	for _dir in dirs:
		print os.path.join(root, _dir)
		dirId = createDriveDirectory(_dir, rootDirId)
		driveIds[os.path.join(root,_dir)] = dirId

	for _file in files:
		if _file == "Thumbs.db" or _file == ".DS_Store":
			continue
		filepath = os.path.join(root, _file)
		fileId = createDriveFile(filepath, rootDirId)

