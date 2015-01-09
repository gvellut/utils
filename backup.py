# -*- coding: utf-8 -*-

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import ApiRequestError
import sys
import os
import hashlib
import argparse
import time

def createDriveDirectory(name, parentId, retryCount = 3):
	try:
		files = drive.ListFile({'q': u"'%s' in parents and title = '%s'" % (parentId, name.replace("'", "\\'"))}).GetList()
		if len(files) > 0:
			print "Found folder %s in parent %s" % (name, parentId)
			return files[0]['id']
		
		folder = drive.CreateFile({'title':name, 'mimeType':'application/vnd.google-apps.folder', 
			'parents': [{"kind": "drive#fileLink","id": parentId}]})
		print u"Creating folder %s in parent %s" % (name, parentId)
		folder.Upload()	
		return folder['id']
	except:
		retryCount -= 1
		if retryCount == 0:
			print "Too many errors. Aborting..."
			raise
		else:
			print "Error communicating with Drive. Retrying in 30s..."
			time.sleep(30)
			createDriveDirectory(name, parentId, retryCount)		

def createDriveFile(filepath, parentId, retryCount = 3):
	try:
		name = os.path.basename(filepath)
		files = drive.ListFile({'q': u"'%s' in parents and title = '%s'" % (parentId, name.replace("'", "\\'"))}).GetList()
		if len(files) > 0:
			_file = files[0]
			print u"Found file %s in parent %s. Computing checksum...." % (name, parentId)
			if _file['md5Checksum'] == md5(filepath):
				# same file
				print "No change"
				return _file['id']		
		else:
			_file = drive.CreateFile({'title': name, 
				'parents': [{"kind": "drive#fileLink","id": parentId}]})
		_file.SetContentFile(filepath)
		print u"Uploading %s..." % filepath
		_file.Upload()
		return _file['id']
	except:
		retryCount -= 1
		if retryCount == 0:
			print "Too many errors. Aborting..."
			raise
		else:
			print "Error communicating with Drive. Retrying in 30s..."
			time.sleep(30)
			createDriveFile(filepath, parentId, retryCount)	

def md5(filepath):
	with open(filepath) as _file:
		return hashlib.md5(_file.read()).hexdigest()

parser = argparse.ArgumentParser('python backup.py')
parser.add_argument('folderToBackup')
parser.add_argument("--skipto", dest="skipTo")

args = parser.parse_args()
skipTo = args.skipTo

gauth = GoogleAuth()
gauth.LocalWebserverAuth() 

drive = GoogleDrive(gauth)
backupFolder = drive.ListFile({'q': "'root' in parents and title = '___BACKUP'"}).GetList()
if len(backupFolder) > 0:
	backupFolder = backupFolder[0]
else:
	print "Unexpected error: Can't find backup folder."
	exit()

folderToBackup = args.folderToBackup
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
	print u"In folder %s..." % root

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

	if skipTo and root != skipTo:
		print "Skipping."
		continue
	elif skipTo:
		print "Found skipTo file."
		skipTo = None	

	for _file in files:
		if _file == "Thumbs.db" or _file == ".DS_Store" or _file == 'P2050092.JPG':
			continue
		filepath = os.path.join(root, _file)
		filepath = filepath.decode('utf8')
		fileId = createDriveFile(filepath, rootDirId)

