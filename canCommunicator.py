import can
import can.interfaces.etas #DA INCLUDERE ESPLICITAMENTE, IN QUANTO RICHIESTO DA .EXE
import time
import const

class canCommunicator():
	def __init__(self, configParams):
		self.bus = None;
		self.selectedInterface = None;
		self.configParams = configParams;
		self.timeTester = time.time();
		self.timeHeaterOn = None;
		self.isHeaterOn = False;

	def initInterface(self):
		configs = can.interface.detect_available_configs(interfaces=self.configParams.NAME);

		#Parametri temporanei nel caso di interfacce multiple collegate
		counter_interfaces = 0;
		stored_index = [];

		for i in range (0, len(configs) - 1):
			if(self.configParams.DRIVER in configs[i]['channel'] and self.configParams.CHANNEL in configs[i]['channel']):
				counter_interfaces = counter_interfaces + 1;
				stored_index.append(i);

		#Se c'è solo un'interfaccia collegata, collegati alla prima, altrimenti alla seconda
		if(counter_interfaces == 1):
			self.selectedInterface = configs[stored_index[0]]['channel'];
			print(f"Found interface: {self.selectedInterface}\n");

		elif(counter_interfaces > 1):
			self.selectedInterface = configs[stored_index[1]]['channel'];
			print(f"Found interface: {self.selectedInterface}\n");

		self.bus = can.ThreadSafeBus(interface='etas',channel=self.selectedInterface, bitrate=self.configParams.BAUDRATE, receive_own_messages=True, can_filters = [{"can_id": 0x18DAFA21, "can_mask": 0xFFFFFFFF, "extended": True}]);

	def closeInterface(self):
		if(self.bus != None):
			self.bus.shutdown();
			self.bus = None;

	def sendData(self, out, cmd):
		try:
			if(out in const.canDetails.DID):
				if(cmd == "Rte"):
					self.bus.send(can.Message(arbitration_id=const.canDetails.TX_ADDRESS, is_extended_id=True, data=[0x04, 0x2F, const.canDetails.DID[out]["HB"], const.canDetails.DID[out]["LB"], 0x00]));
					if(out == "Heater"):
						print("Heater RTE");
						self.isHeaterOn = False;
					elif(out == "Ventolone"):
						print("Ventolone RTE");
					elif(out == "Temperatura"):
						print("Temperatura olio RTE");
				elif(cmd == "Off"):
					self.bus.send(can.Message(arbitration_id=const.canDetails.TX_ADDRESS, is_extended_id=True, data=[0x05, 0x2F, const.canDetails.DID[out]["HB"], const.canDetails.DID[out]["LB"], 0x03, 0x00]));
					if(out == "Heater"):
						print("Heater Off");
						self.isHeaterOn = False;
					else:
						print("Ventolone Off");
				elif(cmd == "On"):
					print("Heater On");
					self.bus.send(can.Message(arbitration_id=const.canDetails.TX_ADDRESS, is_extended_id=True, data=[0x05, 0x2F, const.canDetails.DID[out]["HB"], const.canDetails.DID[out]["LB"], 0x03, 0x01]));
					self.isHeaterOn = True;
					self.timeHeaterOn = time.time();
				elif(cmd == "-20"):
					print("Temp. -20")
					self.bus.send(can.Message(arbitration_id=const.canDetails.TX_ADDRESS, is_extended_id=True, data=[0x06, 0x2F, const.canDetails.DID[out]["HB"], const.canDetails.DID[out]["LB"], 0x03, 0xA0, 0x1F]));
				elif(cmd == "0"):
					print("Temp. 0")
					self.bus.send(can.Message(arbitration_id=const.canDetails.TX_ADDRESS, is_extended_id=True, data=[0x06, 0x2F, const.canDetails.DID[out]["HB"], const.canDetails.DID[out]["LB"], 0x03, 0x20, 0x22]));
				elif(cmd == "20"):
					if(out == "Ventolone"):
						print("Vent. 20")
						self.bus.send(can.Message(arbitration_id=const.canDetails.TX_ADDRESS, is_extended_id=True, data=[0x05, 0x2F, const.canDetails.DID[out]["HB"], const.canDetails.DID[out]["LB"], 0x03, 0x01]));
					else:
						print("Temp. 20")
						self.bus.send(can.Message(arbitration_id=const.canDetails.TX_ADDRESS, is_extended_id=True, data=[0x06, 0x2F, const.canDetails.DID[out]["HB"], const.canDetails.DID[out]["LB"], 0x03, 0xA0, 0x24]));
				elif(cmd == "80"):
					print("Vent. 80");
					self.bus.send(can.Message(arbitration_id=const.canDetails.TX_ADDRESS, is_extended_id=True, data=[0x05, 0x2F, const.canDetails.DID[out]["HB"], const.canDetails.DID[out]["LB"], 0x03, 0x02]));
				elif(cmd == "100"):
					print("Vent. 100");
					self.bus.send(can.Message(arbitration_id=const.canDetails.TX_ADDRESS, is_extended_id=True, data=[0x05, 0x2F, const.canDetails.DID[out]["HB"], const.canDetails.DID[out]["LB"], 0x03, 0x03]));

			#Tester present
			elif(out == "Tester"):
				self.bus.send(can.Message(arbitration_id=const.canDetails.TX_ADDRESS, is_extended_id=True, data=[0x02, 0x3E, 0x00]));
				print("TESTER")

			self.timeTester = time.time();
			#OK
			return 0;

		except Exception as e:
			print(e);
			#In caso d'errore
			return -1;
				
	def releaseAll(self):
		self.timeTester = time.time();
		
		try:
			if(self.bus != None):
				for elem in const.canDetails.DID:
					self.bus.send(can.Message(arbitration_id=const.canDetails.TX_ADDRESS, is_extended_id=True, data=[0x04, 0x2F, const.canDetails.DID[elem]["HB"], const.canDetails.DID[elem]["LB"], 0x00]));
					#Sleep aggiunto per evitare conflitti tra diverse chiamate .send()
					time.sleep(0.1);
					print("Release");

				self.isHeaterOn = False;
		except Exception as e:
			print(e);