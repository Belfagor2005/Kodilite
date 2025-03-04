#!/usr/bin/python
# -*- coding: utf-8 -*-

import pkgutil
import os.path
import xbmcaddon
import os


__addon__ = xbmcaddon.Addon(id='script.module.lambdascrapers')


def sources():
    try:
        sourceDict = []
        # provider = __addon__.getSetting('module.provider')
        provider = "Lambdascrapers"
        sourceFolder = getScraperFolder(provider)
        sourceFolderLocation = os.path.join(os.path.dirname(__file__), sourceFolder)
        sourceSubFolders = [x[1] for x in os.walk(sourceFolderLocation)][0]
        for i in sourceSubFolders:
            for loader, module_name, is_pkg in pkgutil.walk_packages([os.path.join(sourceFolderLocation, i)]):
                if is_pkg:
                    continue
                try:
                    module = loader.find_module(module_name).load_module(module_name)
                    sourceDict.append((module_name, module.source()))
                except:
                    pass
        print("Here in lambdascrapers __init__.py sourceDict =", sourceDict)
        return enabledHosters(sourceDict)
    except:
        print("Here in lambdascrapers __init__.py error")
        return []


def enabledHosters(sourceDict, function=False):
    enabledHosts = [i[0] for i in sourceDict if __addon__.getSetting('provider.' + i[0].split('_')[0]) == 'true']
    returnedHosts = [i for i in sourceDict if i[0] in enabledHosts]
    return returnedHosts


def providerSources():
    sourceSubFolders = [x[1] for x in os.walk(os.path.dirname(__file__))][0]
    return getModuleName(sourceSubFolders)


def providerNames():
    providerList = []
    provider = __addon__.getSetting('module.provider')
    sourceFolder = getScraperFolder(provider)
    sourceFolderLocation = os.path.join(os.path.dirname(__file__), sourceFolder)
    sourceSubFolders = [x[1] for x in os.walk(sourceFolderLocation)][0]
    for i in sourceSubFolders:
        for loader, module_name, is_pkg in pkgutil.walk_packages([os.path.join(sourceFolderLocation, i)]):
            if is_pkg:
                continue
            correctName = module_name.split('_')[0]
            providerList.append(correctName)
    return providerList


def getAllHosters():
    def _sources(sourceFolder, appendList):
        sourceFolderLocation = os.path.join(os.path.dirname(__file__), sourceFolder)
        sourceSubFolders = [x[1] for x in os.walk(sourceFolderLocation)][0]
        for i in sourceSubFolders:
            for loader, module_name, is_pkg in pkgutil.walk_packages([os.path.join(sourceFolderLocation, i)]):
                if is_pkg:
                    continue
                try:
                    mn = str(module_name).split('_')[0]
                except:
                    mn = str(module_name)
                appendList.append(mn)
    sourceSubFolders = [x[1] for x in os.walk(os.path.dirname(__file__))][0]
    appendList = []
    for item in sourceSubFolders:
        if item != 'modules':
            _sources(item, appendList)
    return list(set(appendList))


def getScraperFolder(scraper_source):
    sourceSubFolders = [x[1] for x in os.walk(os.path.dirname(__file__))][0]
    return [i for i in sourceSubFolders if scraper_source.lower() in i.lower()][0]


def getModuleName(scraper_folders):
    nameList = []
    for s in scraper_folders:
        try:
            nameList.append(s.split('_')[1].lower().title())
        except:
            pass
    return nameList
