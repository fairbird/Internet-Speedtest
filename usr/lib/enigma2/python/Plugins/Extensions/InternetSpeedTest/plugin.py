#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Mod by madhouse
from __future__ import print_function
import re
from Components.Button import Button
from os import remove, environ, chmod, path
import gettext
from enigma import getDesktop, eConsoleAppContainer, getPyExt
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label

plugin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/InternetSpeedTest/speedtest.")
font = resolveFilename(SCOPE_PLUGINS, "Extensions/InternetSpeedTest/fonts")
skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/InternetSpeedTest/")
cmd = "python " + plugin_path + getPyExt()
if path.exists(plugin_path):
    chmod(plugin_path, 0o755)
HD = getDesktop(0).size()

PluginLanguageDomain = "speedtest"
PluginLanguagePath = resolveFilename(SCOPE_PLUGINS, "Extensions/InternetSpeedTest/locale")


def localeInit():
    lang = language.getLanguage()[:2]
    environ["LANGUAGE"] = lang
    gettext.bindtextdomain(PluginLanguageDomain, PluginLanguagePath)
    gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE, ""))


def _(txt):
    t = gettext.dgettext(PluginLanguageDomain, txt)
    if t == txt:
        t = gettext.dgettext("enigma2", txt)
    return t


localeInit()
language.addCallback(localeInit)


class internetspeedtest(Screen):
    def __init__(self, session):
        self.session = session
        if HD.width() > 1280:
            skin = skin_path + "speedtest_fhd.xml"
        else:
            skin = skin_path + "speedtest_hd.xml"
        f = open(skin, "r")
        self.skin = f.read()
        f.close()
        Screen.__init__(self, session)
        self.color = "#800080"
        self["data"] = Label(_("I check Internet speedtest, be patient..."))
        self["ping"] = Label(" ")
        self["host"] = Label(" ")
        self["ip"] = Label(" ")
        self["download"] = Label(" ")
        self["upload"] = Label(" ")
        self["key_red"] = Button(_("Exit"))
        self["key_green"] = Button(_("Repeat test"))
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions"], {"cancel": self.exit, "red": self.exit, "green": self.testagain}, -1)
        self.finished = False
        self.data = ""
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.action)
        self.container.dataAvail.append(self.dataAvail)
        self.container.execute(cmd)

    def testagain(self):
        if self.finished == False:
            return
        self.data = ""
        self.container.execute(cmd)

    def action(self, retval):
        print("retval", retval)
        print("finished test")
        self.finished = True

    def dataAvail(self, rstr):
        if rstr:
            rstr = str(rstr.decode())
            self.data = self.data + rstr
            parts = rstr.split("\n")
            for part in parts:
                if "Hosted by" in part:
                    try:
                        host = part.split("Hosted by")[1].split("[")[0].strip()
                    except:
                        host = ""
                    self["host"].setText(str(host))
                    try:
                        ping = "   " + part.split(":")[1].strip()
                    except:
                        ping = ""
                    self["ping"].setText(str(ping))
                if "Testing download from" in part:
                    ip = part.split("Testing download from")[1].split(")")[0].replace("(", "").strip()
                    self["ip"].setText(str(ip))
                if "Download:" in rstr:
                    try:
                        download = rstr.split(":")[1].split("\n")[0].strip()
                    except:
                        download = ""
                    self["download"].setText(str(download))
                    self.data = ""
                    self.data = "Testing upload speed"
                if "Upload:" in rstr:
                    try:
                        upload = rstr.split(":")[1].split("\n")[0].strip()
                    except:
                        upload = ""
                    self["upload"].setText(str(upload))
                    self["data"].setText(_("Test completed, to test again press green button"))
                    return
                self["data"].setText(self.data)

    def exit(self):
        self.container.appClosed.remove(self.action)
        self.container.dataAvail.remove(self.dataAvail)
        self.close()


def main(session, iface):
    session.open(internetspeedtest)


def callFunction(iface):
    return main


def Plugins(**kwargs):
    return PluginDescriptor(name=_("InternetSpeedTest"), description=_("Internet Speed Test") + "\n", where=PluginDescriptor.WHERE_NETWORKSETUP, needsRestart=False, fnc={"ifaceSupported": callFunction, "menuEntryName": lambda x: _("InternetSpeedTest"), "menuEntryDescription": lambda x: _("Internet Speed Test...") + "\n"})
