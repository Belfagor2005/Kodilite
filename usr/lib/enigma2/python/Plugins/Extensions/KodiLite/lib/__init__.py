#!/usr/bin/python
# -*- coding: utf-8 -*-

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import gettext
import os
from skin import loadSkin

PluginLanguageDomain = 'xbmcaddons'
PluginLanguagePath = 'Extensions/KodiLite/locale'
isDreamOS = False


def loadSkinReal(skinPath):
    if os.path.exists(skinPath):
        print('Loading skin',skinPath)
        loadSkin(skinPath)


def loadPluginSkin(pluginPath):
#    loadSkinReal(pluginPath + '/' + config.skin.primary_skin.value)
    loadSkinReal(config.skin.primary_skin.value)
    loadSkinReal(pluginPath + '/skin.xml')


if os.path.exists("/var/lib/dpkg/status"):
    isDreamOS = True


def localeInit():
    if isDreamOS:
        lang = language.getLanguage()[:2]
        os.environ["LANGUAGE"] = lang
    gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))


if isDreamOS:
    _ = lambda txt: gettext.dgettext(PluginLanguageDomain, txt) if txt else ""
    localeInit()
    language.addCallback(localeInit)
else:
    def _(txt):
        if gettext.dgettext(PluginLanguageDomain, txt):
            return gettext.dgettext(PluginLanguageDomain, txt)
        else:
            print(("[%s] fallback to default translation for %s" % (PluginLanguageDomain, txt)))
            return gettext.gettext(txt)
    language.addCallback(localeInit())
