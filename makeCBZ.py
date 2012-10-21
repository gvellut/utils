import zipfile
import os
import glob
from sys import argv


def makeCBZ(prefix, outputPath, coverPath):
    with zipfile.ZipFile(outputPath + '.cbz', 'w') as cbz:
        _, coverFileName = os.path.split(coverPath)
        cbz.write(coverPath, '____' + coverFileName)
        for filePath in glob.glob(prefix + '*'):
            _, fileName = os.path.split(filePath)
            fileNameRoot, _ = os.path.splitext(fileName)
            input = zipfile.ZipFile(filePath)
            for pagePath in input.namelist():
                if pagePath.endswith('/'):
                    continue
                _, pageName = os.path.split(pagePath)
                pageFile = input.open(pagePath)
                cbz.writestr(fileNameRoot + '_' + pageName, pageFile.read())
    
_, prefix, outputPath, coverPath = argv

makeCBZ(prefix, outputPath, coverPath)
    
    

