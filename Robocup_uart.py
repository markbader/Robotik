#import smbus
import serial
import time
import picamera
import picamera.array
import thread
 
# for RPI version 1, use "bus = smbus.SMBus(0)"
#bus = smbus.SMBus(1)
ser = serial.Serial(port="/dev/ttyAMA0",baudrate=9600)

def get():
    global taster
    while 1:
        print("get")
        empfangen = ser.read()
        print(empfangen)
        if empfangen:
            taster = ser.read()
        else:
            taster = 15
    
 
####Kamera-KLasse
class MyAnalysis(picamera.array.PiRGBAnalysis):
    def __init__(self, camera):
        self.set("LAMPE=1")
        self.set("STANDBY=1")
        self.richtung("FORWARD")
        self.status = 0 #aus
        self.geschwindigkeit = 100
        self.time = time.time()
        thr = thread.start_new_thread(get,())
        super(MyAnalysis, self).__init__(camera)
 
    def analyse(self, foto):#Lichtwerte ins Array
        global taster
        self.set("TASTER=1")
        time.sleep(0.1)
        print(taster)
        if self.status == 0: # Warten bis der mittlere Taster gedrueckt wird
            print("aus")
            self.set("TASTER=1")
            time.sleep(0.1)
            if taster^0b1111 == 0b0010:
                print('Start')
                while taster^0b1111 == 0b0010: #Warten solange Taster gedrueckt ist
                    self.set("TASTER=1")
                    time.sleep(0.1)
                self.set("MOTOR_STANDBY=1")
                self.status = 1
            else:print("Taster_aus")
        else:
            self.set("TASTER=1")
            if taster^0b1111 == 0b0010:
                while taster^0b1111 == 0b0010: #Warten solange Taster gedrueckt ist
                    self.set("TASTER=1")
                    time.sleep(0.5)
                self.set("MOTOR_L=0")
                self.set("MOTOR_R=0")
                self.richtung("FORWARD")
                self.set("MOTOR_STANDBY=0")
                self.status=0
            elif taster^0b1111 == 0b1000:
                self.hindernis(0)
            else:
                self.set("LAMPE=1")
                self.richtung("FORWARD")
                self.set("MOTOR_STANDBY=1")
                #print('Aufnahme')
                licht1 = []
                licht2 = []
                licht3 = []
                weiss1 = []
                weiss2 = []
                weiss3 = []
                for i in range(9, 55, 5):
                    r1 = int(foto[40][i][0])
                    r2 = int(foto[51][i][0])
                    r3 = int(foto[62][i][0])
                    g1 = int(foto[40][i][1])
                    g2 = int(foto[51][i][1])
                    g3 = int(foto[62][i][1])
                    b1 = int(foto[40][i][2])
                    b2 = int(foto[51][i][2])
                    b3 = int(foto[62][i][2])
                    wert1 = (r1 + g1 + b1) // 3
                    wert2 = (r2 + g2 + b2) // 3
                    wert3 = (r3 + g3 + b3) // 3
                    if wert1 > 50:
                        weiss1.append(0)
                    else:
                        weiss1.append(1)
                    if wert2 > 50:
                        weiss2.append(0)
                    else:
                        weiss2.append(1)
                    if wert3 > 50:
                        weiss3.append(0)
                    else:
                        weiss3.append(1)
                    licht1.append(int(wert1))
                    licht2.append(int(wert2))
                    licht3.append(int(wert3))
                print(r1,g1,b1)
                #if sum(licht1)//10<35 or sum(licht1)//10>45:
                if not (1 in weiss1):#Falls nur noch weiss, analysiert er die hinteren Zeilen
                    self.linieverloren(licht2,weiss3)
                elif not (0 in weiss1):#Falls nur noch Schwarz -> Kreuzung: Fallunterscheidung, bei gruenem Punkt abbiegen, sonst geradeaus
                    print('kreuzung')
                    self.kreuzung(licht2,licht3)
                elif weiss1[:5].count(1)>=5 and weiss2.count(1)<4:
                    pass
                elif weiss1[5:].count(1)>=5 and weiss2.count(1)<4:
                    pass
                else:
                    self.liniefolgen(licht1)
 
    def werte_berechnen(self, liste):#Berechnet die Helligkeitsdifferenzen
        gewichtung = [6, 3.5, 2.61, 1.4, 1, 1, 1.4, 2.61, 3.5, 6]
        for i in range (len(liste)): # Belegt die Ausgelesenen Pixel mit Prioritaeten um die Motorgeschwindigkeit zu steuern
            liste[i]=gewichtung[i]*liste[i]
        Licht1 = abs(sum(liste[:5]))
        Licht2 = abs(sum(liste[5:]))
        dif = Licht1 - Licht2
        return dif

    def hindernis(self, richtung):
        self.set("MOTOR_L="+str(self.geschwindigkeit))
        self.set("MOTOR_R="+str(self.geschwindigkeit))
        if richtung == 0:
            self.richtung("RIGHT")
            time.sleep(1.2)
            self.richtung("FORWARD")
            time.sleep(2)
            self.richtung("LEFT")
            time.sleep(1.2)
            self.richtung("FORWARD")
            time.sleep(2)
        else:
            self.richtung("LEFT")
            time.sleep(1.2)
            self.richtung("FORWARD")
            time.sleep(2)
            self.richtung("RIGHT")
            time.sleep(1.2)
            self.richtung("FORWARD")
            time.sleep(2)
            
    def liniefolgen(self, liste):
        dif = self.werte_berechnen(liste) 
        faktor = 0.05
        rechterMotor, linkerMotor = int(self.geschwindigkeit + dif*faktor), int(self.geschwindigkeit - dif*faktor)
      	if rechterMotor > 180: rechterMotor = 180
      	if linkerMotor > 180: linkerMotor = 180
      	if rechterMotor < 0: rechterMotor= 0
      	if linkerMotor < 0: linkerMotor=0
        self.set("MOTOR_R"+str(abs(rechterMotor))) #setzt die Motordrehzahl
        self.set("MOTOR_L"+str(abs(linkerMotor)))

    def linieverloren(self,licht2,weiss3):
        print('Linie verloren')
        sum_li = sum(licht2[0:5])
        sum_re = sum(licht2[5:])
        dif = sum_li - sum_re
        self.richtung("FORWARD")
        self.set("MOTOR_L="+str(self.geschwindigkeit))
        self.set("MOTOR_R="+str(self.geschwindigkeit))
        if dif < 240 and dif > -240: 
            if sum(weiss3)>=5: # zuvor Gruener Punkt gesehen, dementsprechend abbiegen
                self.linieverloren(weiss3*120,[0])
            else: # Differenz ist zu niedrig -> Luecke erkannt
                time.sleep(0.3)
        elif dif >= 240: #Auf der rechten Seite befand sich schwarz
            time.sleep(0.15)
      	    self.richtung("RIGHT")
      	    time.sleep(0.5)
      	    self.richtung("BACKWARD")
      	    time.sleep(0.32)
        else: #auf der linken Seite befand sich schwarz
            time.sleep(0.15)
            self.richtung("LEFT")
            time.sleep(0.5)
            self.richtung("BACKWARD")
            time.sleep(0.32)
        self.richtung("FORWARD")

    def kreuzung(self, licht2, licht3):
        print('Kreuzung')
        sum_li = sum(licht2[0:5]+licht3[0:5])//2
        sum_re = sum(licht2[5:]+licht3[5:])//2
        dif = sum_re - sum_li
        self.richtung("FORWARD")
        self.set("MOTOR_L="+str(self.geschwindigkeit))
        self.set("MOTOR_R="+str(self.geschwindigkeit))
        if dif < 100 and dif > -100:
            print('Gerade')
            time.sleep(0.3)
        elif dif <= 100:
            print('Rechts')
            time.sleep(0.1)
            self.richtung("RIGHT")
            time.sleep(0.5)
        else:
            print('Links')
            time.sleep(0.1)
            self.richtung("LEFT")
            time.sleep(0.5)

    def richtung(self, richtung):
        if richtung == "FORWARD":
            self.set("DIR_L=0")
            self.set("DIR_R=0")
        elif richtung == "BACKWARD":
            self.set("DIR_L=1")
            self.set("DIR_R=1")
        elif richtung == "LEFT":
            self.set("DIR_L=0")
            self.set("DIR_R=1")
        elif richtung == "RIGHT":
            self.set("DIR_L=1")
            self.set("DIR_R=0")
        else:
            print("Falsche RICHTUNG!")

    def set(self, befehl): #Schickt 1 Byte mit einer Position und dann 1 Byte mit dem Inhalt
    	try:
          ser.write(befehl+'\n')
    	except:
    	    print('set() Fehler')        	
    	return -1
 
    def get(self):#man bekommt den Wert der uebergebenen Position im Array des Arduino
        while 1:
            print("get")
            empfangen = ser.read()
            print(empfangen)
            if empfangen:
              self.taster = ser.read()
 
time1 = 60000
 
with picamera.PiCamera() as camera:
    camera.resolution = (64,64)
    camera.framerate = 30
    output = MyAnalysis(camera)
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    camera.awb_mode = 'auto'
    camera.start_recording(output, 'rgb')
    camera.wait_recording(time1)
    camera.stop_recording()
