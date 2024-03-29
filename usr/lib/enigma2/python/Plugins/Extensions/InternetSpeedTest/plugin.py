# -*- coding: utf-8 -*-
#Code by madhouse
#Code Speedtest-cli from source https://github.com/sivel/speedtest-cli
from . import _, headers, png_tmp, cmd, plugin_path, HD
from Components.Button import Button
from os import remove, path
try:
	from urllib.request import urlopen, Request
except ImportError:
	from urllib2 import urlopen, Request
from enigma import eConsoleAppContainer, ePicLoad, eTimer
from Components.config import ConfigText, ConfigSubsection, config, configfile
from Plugins.Plugin import PluginDescriptor
from Components.MenuList import MenuList
from Screens.Screen import Screen
from Components.ActionMap import HelpableActionMap
from Components.Pixmap import Pixmap
from Components.Label import Label
from sys import version_info

config.internetspeedtest = ConfigSubsection()
config.internetspeedtest.server = ConfigText(default="9636", visible_width = 250, fixed_size = False)


class internetspeedtest(Screen):
	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self["data"] = Label(_("I check Internet speedtest, be patient..."))
		self["ping"] = Label("")
		self["host"] = Label("")
		self["ip"] = Label("")
		self["download"] = Label("")
		self["upload"] = Label("")
		self["key_red"] = Button(_("Exit"))
		self["key_green"] = Label()
		self["green"] = Pixmap()
		self["green"].hide()
		self["key_yellow"] = Label()
		self["favServ"] = Label(_("Server list"))
		self["yellow"] = Pixmap()
		self["yellow"].hide()
		self["key_blue"] = Label()
		self["blue"] = Pixmap()
		self["blue"].hide()
		self["actions"] = HelpableActionMap(self, "internetspeedtest", {
			"cancel": self.exit,
			"red": self.exit,
			"blue": self.showresults,
			"green": self.testagain,
			"Help": self.listServer,
			"yellow": self.save_result}, -2)
		self.finished = False
		self.data = ""
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.action)
		self.container.dataAvail.append(self.dataAvail)
		self.container.execute(cmd)

	def listServer(self):
		self.session.openWithCallback(self.quit, ListServers)

	def quit(self):
		self.close()

	def showresults(self):
		if path.exists(png_tmp):
			self.session.open(showresult)
		else:
			pass

	def testagain(self):
		self["data"].setText("")
		self["green"].hide()
		self["key_green"].setText("")
		self["yellow"].hide()
		self["key_yellow"].setText("")
		self["blue"].hide()
		self["key_blue"].setText("")
		self["ping"].setText("")
		self["host"].setText("")
		self["ip"].setText("")
		self["download"].setText("")
		self["upload"].setText("")
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
						host = part.split("Hosted by")[1].strip()
					except:
						host = ""
					self["host"].setText(str(host))
				if "Ping" in part:
					try:
						ping = rstr.split("Ping")[1].strip()
					except:
						ping = ""
					self["ping"].setText(str(ping))
				if "Testing download from" in part:
					ip = part.split("Testing download from")[1].split(")")[0].replace("(","").strip()
					self["ip"].setText(str(ip))
					self.data = (_("Testing download from"))
				if "Download:" in rstr:
					try:
						download = rstr.split(":")[1].split("\n")[0].strip()
					except:
						download = ""
					self["download"].setText(str(download))
					self.data = (_("Testing upload speed"))
				if "Upload:" in rstr:
					try:
						upload = rstr.split(":")[1].split("\n")[0].strip()
					except:
						upload = ""
					self["upload"].setText(str(upload))
				if "Share results:" in rstr:
					try:
						url_results = rstr.split()[2]
					except:
						url_results = ""
					self.url_png = str(url_results)
					if path.exists(png_tmp):
						remove(png_tmp)
					try:
						request_site = Request(self.url_png, None, headers)
						speed_image = urlopen(request_site).read()
						image = open(png_tmp, "wb")
						image.write(speed_image)
						image.close()
					except Exception as e:
						print(e)
						self.DownloadPngTest()
					self["key_yellow"].setText(_("Save results"))
					self["yellow"].show()
					self["key_green"].setText(_("Repeat test"))
					self["green"].show()
					self.data = "Test completed, to test again press green button"
					self["data"].setText(_(self.data))
					return
				self["data"].setText(_(self.data).replace("Hosted by", "").replace(".", ""))

	def DownloadPngTest(self):
		try:
			request_site = Request(self.url_png, None, headers)
			speed_image = urlopen(request_site).read()
			image = open(png_tmp, "wb")
			image.write(speed_image)
			image.close()
		except Exception as e:
			print(e)

	def save_result(self):
		if path.exists(png_tmp):
			self["data"].setText(_("Result successfully saved in /tmp/speedtest.png"))
			self["key_blue"].setText(_("Show results"))
			self["blue"].show()
			return
		else:
			try:
				request_site = Request(self.url_png, None, headers)
				speed_image = urlopen(request_site).read()
				image = open(png_tmp, "wb")
				image.write(speed_image)
				image.close()
			except Exception as e:
				print(e)
			if path.exists(png_tmp):
				self["data"].setText(_("Result successfully saved in /tmp/speedtest.png"))
				self["key_blue"].setText(_("Show results"))
				self["blue"].show()
			else:
				self["data"].setText(_("Download speedtest.png failed!"))

	def exit(self):
		self.container.appClosed.remove(self.action)
		self.container.dataAvail.remove(self.dataAvail)
		self.close()


class ListServers(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self["introduction"] = Label()
		self.resultlist = []
		self["list"] = MenuList(self.resultlist)
		self["key_red"] = Label(_("Exit"))
		self["key_green"] = Label(_("Ok"))
		self["wait"] = Label()
		self["actions"] = HelpableActionMap(self, "internetspeedtest", {"cancel": self.exit,
		"ok": self.okClicked,
		"green": self.okClicked,
		"back": self.exit,
		"red": self.exit,
		"left": self.pageUp,
		"right": self.pageDown,
		"down": self.moveDown,
		"up": self.moveUp
		}, -1)
		self.onLayoutFinish.append(self.showwait)

	def pageUp(self):
		self["list"].instance.moveSelection(self["list"].instance.pageUp)

	def pageDown(self):
		self["list"].instance.moveSelection(self["list"].instance.pageDown)

	def moveUp(self):
		self["list"].instance.moveSelection(self["list"].instance.moveUp)

	def moveDown(self):
		self["list"].instance.moveSelection(self["list"].instance.moveDown)

	def exit(self):
		self.close()

	def showwait(self):
		self["wait"].setText(_("I check the available servers"))
		self.Timer = eTimer()
		try:
			self.Timer_conn = self.Timer.timeout.connect(self.showMenu)
		except:
			self.Timer.callback.append(self.showMenu)
		self.Timer.start(10, True)

	def showMenu(self):
		self.Timer.stop()
		try:
			import subprocess
			myfavserv= subprocess.Popen(["python", "/usr/lib/enigma2/python/Plugins/Extensions/InternetSpeedTest/speedtest.py", "--list", "--secure"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			stdout,stderr = myfavserv.communicate()
			PY3 = version_info[0] == 3
			try:
				if PY3:
					results = stdout.decode().split("\n")[:-1]
				else:
					results = stdout.split("\n")[:-1]
			except:
				pass
		except:
			results = []
			if results == 0:
				return False
		self.resultlist = []
		for searchResult in results:
			try:
				self["introduction"].setText(_("Choose server and press ok"))
				self.resultlist.append(searchResult)
			except:
				self.resultlist.append(_("No servers received!"))
		self["wait"].setText("")
		self["list"].setList(self.resultlist)

	def okClicked(self):
		id = self["list"].getCurrent()
		part = id.partition(")")
		if part:
			config.internetspeedtest.server.value = (part[0])
			config.internetspeedtest.server.save()
			configfile.save()
			self.session.openWithCallback(self.exit, ListServersFav)


class ListServersFav(Screen):
	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self["data"] = Label(_("I check Internet speedtest, be patient..."))
		self["ping"] = Label("")
		self["host"] = Label("")
		self["ip"] = Label("")
		self["download"] = Label("")
		self["upload"] = Label("")
		self["key_red"] = Button(_("Exit"))
		self["favServ"] = Label(_("Server list"))
		self["key_green"] = Label()
		self["green"] = Pixmap()
		self["green"].hide()
		self["key_yellow"] = Label()
		self["yellow"] = Pixmap()
		self["yellow"].hide()
		self["key_blue"] = Label()
		self["blue"] = Pixmap()
		self["blue"].hide()
		self["image"] = Pixmap()
		self["actions"] = HelpableActionMap(self, "internetspeedtest", {
			"cancel": self.exit,
			"red": self.exit,
			"blue": self.showresults,
			"green": self.testagain,
			"Help": self.listServer,
			"yellow": self.save_result}, -2)
		self.server = config.internetspeedtest.server.value
		self.cmd = "python " + plugin_path + " --no-pre-allocate --server %s --share --secure" % (self.server)
		self.finished = False
		self.data = ""
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.action)
		self.container.dataAvail.append(self.dataAvail)
		self.container.execute(self.cmd)

	def listServer(self):
		self.session.openWithCallback(self.quit, ListServers)

	def quit(self):
		self.close()

	def showresults(self):
		if path.exists(png_tmp):
			self.session.open(showresult)
		else:
			pass

	def testagain(self):
		self["data"].setText("")
		self["green"].hide()
		self["key_green"].setText("")
		self["yellow"].hide()
		self["key_yellow"].setText("")
		self["blue"].hide()
		self["key_blue"].setText("")
		self["ping"].setText("")
		self["host"].setText("")
		self["ip"].setText("")
		self["download"].setText("")
		self["upload"].setText("")
		if self.finished == False:
			return
		self.data = ""
		self.container.execute(self.cmd)

	def action(self, retval):
		print("retval",retval)
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
						host = part.split("Hosted by")[1].strip()
					except:
						host = ""
					self["host"].setText(str(host))
				if "Ping" in part:
					try:
						ping = rstr.split("Ping")[1].strip()
					except:
						ping = ""
					self["ping"].setText(str(ping))
				if "Testing download from" in part:
					ip = part.split("Testing download from")[1].split(")")[0].replace("(","").strip()
					self["ip"].setText(str(ip))
					self.data = (_("Testing download from"))
				if "Download:" in rstr:
					try:
						download = rstr.split(":")[1].split("\n")[0].strip()
					except:
						download = ""
					self["download"].setText(str(download))
					self.data = (_("Testing upload speed"))
				if "Upload:" in rstr:
					try:
						upload = rstr.split(":")[1].split("\n")[0].strip()
					except:
						upload = ""
					self["upload"].setText(str(upload))
				if "Share results:" in rstr:
					try:
						url_results = rstr.split()[2]
					except:
						url_results = ""
					self.url_png = str(url_results)
					if path.exists(png_tmp):
						remove(png_tmp)
					try:
						request_site = Request(self.url_png, None, headers)
						speed_image = urlopen(request_site).read()
						image = open(png_tmp, "wb")
						image.write(speed_image)
						image.close()
					except Exception as e:
						print(e)
						self.DownloadPngTest()
					self["key_yellow"].setText(_("Save results"))
					self["yellow"].show()
					self["key_green"].setText(_("Repeat test"))
					self["green"].show()
					self.data = "Test completed, to test again press green button"
					self["data"].setText(_(self.data))
					return
				self["data"].setText(_(self.data).replace("Hosted by", "").replace(".", ""))

	def DownloadPngTest(self):
		try:
			request_site = Request(self.url_png, None, headers)
			speed_image = urlopen(request_site).read()
			image = open(png_tmp, "wb")
			image.write(speed_image)
			image.close()
		except Exception as e:
			print(e)

	def save_result(self):
		if path.exists(png_tmp):
			self["data"].setText(_("Result successfully saved in /tmp/speedtest.png"))
			self["key_blue"].setText(_("Show results"))
			self["blue"].show()
			return
		try:
			request_site = Request(self.url_png, None, headers)
			speed_image = urlopen(request_site).read()
			image = open(png_tmp, "wb")
			image.write(speed_image)
			image.close()
		except Exception as e:
			print(e)
		if path.exists(png_tmp):
			self["data"].setText(_("Result successfully saved in /tmp/speedtest.png"))
			self["key_blue"].setText(_("Show results"))
			self["blue"].show()
		else:
			self["data"].setText(_("Download speedtest.png failed!"))

	def exit(self):
		self.container.appClosed.remove(self.action)
		self.container.dataAvail.remove(self.dataAvail)
		self.close()


class showresult(Screen):
	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self["key_red"] = Button(_("Exit"))
		self["image"] = Pixmap()
		self["actions"] = HelpableActionMap(self, "internetspeedtest", {
			"cancel": self.close_screen,
			"red": self.close_screen}, -2)
		self.onLayoutFinish.append(self.showpng)

	def close_screen(self):
		self.close()

	def showpng(self):
		if path.exists(png_tmp):
			self["image"].instance.setScale(1)
			self["image"].instance.setPixmapFromFile(png_tmp)
			self["image"].instance.show()
		else:
			pass


def main(session, iface):
	session.open(internetspeedtest)


def callFunction(iface):
	return main


def Plugins(**kwargs):
	return PluginDescriptor(name=_("InternetSpeedTest"), description=_("Internet Speed Test") + "\n", where=PluginDescriptor.WHERE_NETWORKSETUP, needsRestart=False, fnc={"ifaceSupported": callFunction, "menuEntryName": lambda x: _("InternetSpeedTest"), "menuEntryDescription": lambda x: _("Internet Speed Test...") + "\n"})
