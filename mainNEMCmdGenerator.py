import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from idlelib.tooltip import Hovertip
import time
import threading
import base64
import canCommunicator
import const
import ctypes
import os 

class mainNEMCmdGenerator():
	def __init__(self):
		self.configPars = const.configParams();
		self.configPars.initConstants();

		self.canCom = canCommunicator.canCommunicator(self.configPars);
		self.isAlive = True;
		self.returnCode = 0;

	def checkTimeout(self):
		while(self.isAlive):
			if(self.canCom.bus != None and ((time.time() - self.canCom.timeTester) >= const.canDetails.TESTER_TIMEOUT)):
				self.returnCode = self.canCom.sendData(out = "Tester", cmd = None);

			if(self.canCom.bus != None and self.canCom.isHeaterOn and ((time.time() - self.canCom.timeHeaterOn) >= self.configPars.TIMEOUT_HEATER)):
				self.returnCode = self.canCom.sendData(out = "Heater", cmd = "Off");
				#Thread separato per warning per evitare che il task sia bloccante
				
				if(self.returnCode == 0):
					warningMsg = threading.Thread(target=messagebox.showwarning, kwargs = {'title': "Warning", 'message': f"Il grid heater è stato disabilitato in quanto raggiunto il tempo di timeout ({self.configPars.TIMEOUT_HEATER}s)!"});
					warningMsg.start();

			time.sleep(1);

	def connectToInterface(self):
		if(self.connect_butt["text"] == "CONNECT"):
			self.connect_butt["state"] = "disable";
			self.connect_butt["text"] = "WAIT...";
			self.connect_butt["background"] = "LIGHTGREY";
			#Per forzatura aggiornamento elementi grafici
			self.connect_butt.update_idletasks();

			try:
				self.canCom.initInterface();

				self.connect_butt["background"] = "RED";
				self.connect_butt["text"] = "DISCONNECT"
				self.connect_butt["state"] = "normal";
				self.connect_butt.update_idletasks();

				self.ventolone_label["state"] = "normal";
				self.ventolone_rte["state"] = "normal";
				self.ventolone_off["state"] = "normal";
				self.ventolone_20["state"] = "normal";
				self.ventolone_80["state"] = "normal";
				self.ventolone_100["state"] = "normal";

				self.heater_label["state"] = "normal";
				self.heater_rte["state"] = "normal";
				self.heater_on["state"] = "normal";
				self.heater_off["state"] = "normal";

				self.temp_label["state"] = "normal";
				self.temp_rte["state"] = "normal";
				self.temp_neg_20["state"] = "normal";
				self.temp_0["state"] = "normal";
				self.temp_20["state"] = "normal";

			except Exception as e:
				self.connect_butt["text"] = "CONNECT"
				self.connect_butt["background"] = "GREEN";
				self.connect_butt["state"] = "normal";

				self.canCom.releaseAll();
				self.canCom.closeInterface();

				messagebox.showerror(title="Errore di comunicazione", message="Mancato collegamento con interfaccia di comunicazione ETAS!");
		else:
			self.connect_butt["text"] = "CONNECT"
			self.connect_butt["background"] = "GREEN";

			self.ventolone_label["state"] = "disable";
			self.ventolone_rte["state"] = "disable";
			self.ventolone_off["state"] = "disable";
			self.ventolone_20["state"] = "disable";
			self.ventolone_80["state"] = "disable";
			self.ventolone_100["state"] = "disable";

			self.heater_label["state"] = "disable";
			self.heater_rte["state"] = "disable";
			self.heater_on["state"] = "disable";
			self.heater_off["state"] = "disable";

			self.temp_label["state"] = "disable";
			self.temp_rte["state"] = "disable";
			self.temp_neg_20["state"] = "disable";
			self.temp_0["state"] = "disable";
			self.temp_20["state"] = "disable";

			self.canCom.releaseAll();
			self.canCom.closeInterface();

	def controlloVentolone(self, ctrl):
		self.returnCode = self.canCom.sendData(out = "Ventolone", cmd = ctrl);

	def controlloHeater(self, ctrl):
		self.returnCode = self.canCom.sendData(out = "Heater", cmd = ctrl);

	def controlloTempOlio(self, ctrl):
		self.returnCode = self.canCom.sendData(out = "Temperatura", cmd = ctrl);
	

	def initGraphics(self):
		self.window = tk.Tk();
		self.window.title("NEM cmd gen. v. 2.0");

		width= 350
		height= 400
		screenwidth = self.window.winfo_screenwidth();
		screenheight = self.window.winfo_screenheight();
		alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2);
		self.window.geometry(alignstr);
		self.window.resizable(width=False, height=False);
		self.window.config(background = "white");

		self.logo = tk.PhotoImage(data=const.generics.IDV_LOGO_SMALL);
		self.label_ico = tk.Label(self.window, image = self.logo, borderwidth= 2, relief="groove");
		self.window.wm_iconphoto(True, self.logo)
		self.label_ico.place(x=80, y=0);

		self.ventolone_label = tk.Label(self.window, background="white", text="Cooling fan", font = "Arial 10 bold", state = "disable");
		self.ventolone_label.place(x = 30 , y = 130);

		self.ventolone_rte = tk.Button(self.window, state = "disable", background = "LIGHTGREY", command = lambda: self.controlloVentolone('Rte'));
		self.ventolone_rte["text"] = "RTE";
		self.ventolone_rte.config(font= 'sans 11 bold',);
		self.ventolone_rte.place(width = 40, height = 30, x = 120, y = 130);

		self.ventolone_rte_tooltip = Hovertip(self.ventolone_rte, "Used to release I/O control on cooling fan.");

		self.ventolone_off = tk.Button(self.window, state = "disable", command = lambda: self.controlloVentolone('Off'));
		self.ventolone_off["text"] = "OFF";
		self.ventolone_off.config(background = "TOMATO", font= 'sans 11 bold',);
		self.ventolone_off.place(width = 50, height = 30, x = 170, y = 130);

		self.ventolone_20 = tk.Button(self.window, state = "disable", command = lambda: self.controlloVentolone('20'));
		self.ventolone_20["text"] = "20%";
		self.ventolone_20.config(font= 'sans 9 bold',);
		self.ventolone_20.place(width = 30, height = 30, x = 230, y = 130);

		self.ventolone_80 = tk.Button(self.window, state = "disable", command = lambda: self.controlloVentolone('80'));
		self.ventolone_80["text"] = "80%";
		self.ventolone_80.config(font= 'sans 9 bold',);
		self.ventolone_80.place(width = 30, height = 30, x = 262, y = 130);

		self.ventolone_100 = tk.Button(self.window, state = "disable", command = lambda: self.controlloVentolone('100'));
		self.ventolone_100["text"] = "100%";
		self.ventolone_100.config(font= 'sans 9 bold',);
		self.ventolone_100.place(width = 30, height = 30, x = 294, y = 130);

		self.heater_label = tk.Label(self.window, background="white", state = "disable", text="Grid heater", font = "Arial 10 bold");
		self.heater_label.place(x = 30 , y = 170);

		self.heater_rte = tk.Button(self.window, state = "disable", background = "LIGHTGREY", command = lambda: self.controlloHeater('Rte'));
		self.heater_rte["text"] = "RTE";
		self.heater_rte.config(font= 'sans 11 bold',);
		self.heater_rte.place(width = 40, height = 30, x = 120, y = 170);

		self.heater_rte_tooltip = Hovertip(self.heater_rte, "Used to release I/O control on grid heater.");

		self.heater_off = tk.Button(self.window, state = "disable", command = lambda: self.controlloHeater('Off'));
		self.heater_off["text"] = "OFF";
		self.heater_off.config(background = "TOMATO", font= 'sans 11 bold',);
		self.heater_off.place(width = 50, height = 30, x = 170, y = 170);

		self.heater_on = tk.Button(self.window, state = "disable", command = lambda: self.controlloHeater('On'));
		self.heater_on["text"] = "ON";
		self.heater_on.config(font= 'sans 11 bold',);
		self.heater_on.place(width = 50, height = 30, x = 230, y = 170);

		self.temp_label = tk.Label(self.window, background="white", text="Oil temp.", font = "Arial 10 bold", state = "disable");
		self.temp_label.place(x = 30 , y = 210);

		self.temp_rte = tk.Button(self.window, state = "disable", background = "LIGHTGREY", command = lambda: self.controlloTempOlio('Rte'));
		self.temp_rte["text"] = "RTE";
		self.temp_rte.config(font= 'sans 11 bold',);
		self.temp_rte.place(width = 40, height = 30, x = 120, y = 210);

		self.temp_rte_tooltip = Hovertip(self.temp_rte, "Used to release I/O control on the input oil temperature.");

		self.temp_neg_20 = tk.Button(self.window, state = "disable", command = lambda: self.controlloTempOlio('-20'));
		self.temp_neg_20["text"] = "-20°";
		self.temp_neg_20.config(font= 'sans 9 bold',);
		self.temp_neg_20.place(width = 30, height = 30, x = 170, y = 210);

		self.temp_0 = tk.Button(self.window, state = "disable", command = lambda: self.controlloTempOlio('0'));
		self.temp_0["text"] = "0°";
		self.temp_0.config(font= 'sans 9 bold',);
		self.temp_0.place(width = 30, height = 30, x = 202, y = 210);

		self.temp_20 = tk.Button(self.window, state = "disable", command = lambda: self.controlloTempOlio('20'));
		self.temp_20["text"] = "+20°";
		self.temp_20.config(font= 'sans 9 bold',);
		self.temp_20.place(width = 30, height = 30, x = 234, y = 210);

		self.connect_butt = tk.Button(self.window, command = self.connectToInterface);
		self.connect_butt["text"] = "CONNECT";
		self.connect_butt.config(background = "GREEN", font= 'sans 11 bold',);
		self.connect_butt.place(width = 200, height = 40, x = 80, y = 340);

		self.window.protocol('WM_DELETE_WINDOW', self.destroy);
		self.window.mainloop();

	def destroy(self):
		self.isAlive = False;
		self.window.destroy();
		self.canCom.releaseAll();
		self.canCom.closeInterface();

def __main__():
	mainNEMCmdGen = mainNEMCmdGenerator();

	GRAPH_window = threading.Thread(target=mainNEMCmdGen.initGraphics);
	TIMEOUT_thread = threading.Thread(target=mainNEMCmdGen.checkTimeout);

	TIMEOUT_thread.start();
	GRAPH_window.start();

	GRAPH_window.join();
	TIMEOUT_thread.join();

##############################
__main__();