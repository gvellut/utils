# -*- coding: utf-8 *-*

import sys, os, subprocess

_, dirPath = sys.argv

convertedDirPath = os.path.join(dirPath, "__converted")
if not os.path.exists(convertedDirPath):
    os.makedirs(convertedDirPath)

for fileName in os.listdir(dirPath):
    if fileName.endswith(".mobi"):
        rootFileName, _ = os.path.splitext(fileName)
        epubFileName = rootFileName + ".epub"
        mobiFilePath = os.path.join(dirPath, fileName)
        convertedMobiFilePath = os.path.join(convertedDirPath, fileName)
        epubFilePath = os.path.join(dirPath, epubFileName)
        conversionResult = subprocess.call(["ebook-convert", mobiFilePath, epubFilePath])
        if conversionResult == 0:
            os.rename(mobiFilePath, convertedMobiFilePath)
