import smbus
import time
import picamera
import picamera.array
import random
 
# for RPI version 1, use "bus = smbus.SMBus(0)"
bus = smbus.SMBus(1)
 
# I2C Adresse festlegen
MASTER_ADDRESS = 0x04
 
#Definition der Pins
SERVO_A = 0 
MOTOR_L = 2
MOTOR_R = 3
MOTOR_DIR = 4
TASTER = 6
LAMPE = 8
MOTOR_STANDBY = 10
 
#Richtungen definieren
FORWARD = 0b0
BACKWARD = 0b11000000
LINKS = 0b1000000
RECHTS = 0b10000000
 
####Kamera-KLasse
class MyAnalysis(picamera.array.PiRGBAnalysis):
    def __init__(self, camera):
        self.set(LAMPE,1)
        self.geschwindigkeit = 90
        self.set(MOTOR_STANDBY, 1)
        self.set(MOTOR_DIR,FORWARD)
        self.status = 0 #aus
        self.time = time.time()
        super(MyAnalysis, self).__init__(camera)
 
    def analyse(self, foto):#Lichtwerte ins Array
        #self.geschwindigkeit = 90
        if self.status == 0: # Warten bis der mittlere Taster gedrueckt wird
            if self.get(TASTER)^0b1111 == 0b0010:
                print('Start')
                while self.get(TASTER)^0b1111 == 0b0010: #Warten solange Taster gedrueckt ist
                    time.sleep(0.1)
                self.set(MOTOR_STANDBY,1)
                self.status = 1
        else:
            if self.get(TASTER)^0b1111 == 0b0010:
                    while self.get(TASTER)^0b1111 == 0b0010: #Warten solange Taster gedrueckt ist
                        time.sleep(0.5)
                    self.set(MOTOR_L, 0)
                    self.set(MOTOR_R, 0)
                    self.set(MOTOR_DIR,FORWARD)
                    self.set(TASTER,7)
                    self.set(MOTOR_STANDBY, 0)
                    self.status=0
            else:
                self.set(LAMPE,1)
                self.set(MOTOR_DIR, FORWARD)
                self.set(MOTOR_STANDBY, 1)
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
                '''if weiss1.count(0)>8 and weiss2.count(1)>7 and weiss3.count(1) >= 2:  
                    print('DOMINIKS PROGRAMM')
                    self.set(MOTOR_DIR,FORWARD)
                    self.set(MOTOR_L,self.geschwindigkeit)
                    self.set(MOTOR_R,self.geschwindigkeit)
                    time.sleep(0.15)
                    a = random.randint(0,1)
                    if a == 0:
                        self.set(MOTOR_DIR,RECHTS)
                    else:
                        self.set(MOTOR_DIR,LINKS)
                    time.sleep(0.5)
                else:
                    self.liniefolgen(licht1)'''
                
                if not (1 in weiss1):#Falls nur noch weiss, analysiert er die hinteren Zeilen
                    self.linieverloren(licht2,weiss3)
                if not (0 in weiss1):#Falls nur noch Schwarz -> Kreuzung: Fallunterscheidung, bei gruenem Punkt abbiegen, sonst geradeaus
                    self.kreuzung(licht2,licht3)
                elif weiss1[:5].count(1)>=5 and weiss2.count(1)<4:
                    pass
                elif weiss1[5:].count(1)>=5 and weiss2.count(1)<4:
                    pass
                else:
                    self.liniefolgen(licht1)
 
    def werte_berechnen(self, liste):#Berechnet die Helligkeitsdifferenzen
        gewichtung = [15, 4, 3.7, 1.3, 1, 1, 1.3, 3.7, 4, 15]
        for i in range (len(liste)): # Belegt die Ausgelesenen Pixel mit Prioritaeten um die Motorgeschwindigkeit zu steuern
            liste[i]=gewichtung[i]*liste[i]
        Licht1 = abs(sum(liste[:5]))
        Licht2 = abs(sum(liste[5:]))
        dif = Licht1 - Licht2
        return dif

    def hindernis_umfahren(self, richtung):
        self.set(MOTOR_L,self.geschwindigkeit)
        self.set(MOTOR_R,self.geschwindigkeit)
        if richtung == 0:
            self.set(MOTOR_DIR, RECHTS)
            time.sleep(1.2)
            self.set(MOTOR_DIR, FORWARD)
            time.sleep(2)
            self.set(MOTOR_DIR, LINKS)
            time.sleep(1.2)
            self.set(MOTOR_DIR, FORWARD)
            time.sleep(2)
        else:
            self.set(MOTOR_DIR, LINKS)
            time.sleep(1.2)
            self.set(MOTOR_DIR, FORWARD)
            time.sleep(2)
            self.set(MOTOR_DIR, RECHTS)
            time.sleep(1.2)
            self.set(MOTOR_DIR, FORWARD)
            time.sleep(2)

    def liniefolgen(self, liste):
        dif = self.werte_berechnen(liste) 
        faktor = 0.1
        rechterMotor, linkerMotor = int(self.geschwindigkeit + dif*faktor), int(self.geschwindigkeit - dif*faktor)
      	if rechterMotor > 200: rechterMotor = 200
      	if linkerMotor > 200: linkerMotor = 200
      	if rechterMotor < 0: rechterMotor= 0
      	if linkerMotor < 0: linkerMotor=0
        self.set(MOTOR_R, abs(rechterMotor)) #setzt die Motordrehzahl
        self.set(MOTOR_L, abs(linkerMotor))

    def linieverloren(self,licht2,weiss3):
        print('Linie verloren')
        sum_li = sum(licht2[0:5])
        sum_re = sum(licht2[5:])
        dif = sum_li - sum_re
        self.set(MOTOR_DIR,FORWARD)
        self.set(MOTOR_L,self.geschwindigkeit)
        self.set(MOTOR_R,self.geschwindigkeit)
        if dif < 450 and dif > -450: 
            if sum(weiss3)>=5: # zuvor Gruener Punkt gesehen, dementsprechend abbiegen
                self.linieverloren(weiss3*120,[0])
            else: # Differenz ist zu niedrig -> Luecke erkannt
                time.sleep(0.1)
        elif dif >= 450: #Auf der rechten Seite befand sich schwarz
      	    self.set(MOTOR_DIR,RECHTS)
      	    time.sleep(0.2)
      	    self.set(MOTOR_DIR,BACKWARD)
      	    time.sleep(0.15)
        else: #auf der linken Seite befand sich schwarz
            self.set(MOTOR_DIR,LINKS)
            time.sleep(0.2)
            self.set(MOTOR_DIR,BACKWARD)
            time.sleep(0.15)
        self.set(MOTOR_DIR,FORWARD)

    def kreuzung(self, licht2, licht3):
        print('Kreuzung')
        sum_li = sum(licht2[0:5]+licht3[0:5])
        sum_re = sum(licht2[5:]+licht3[5:])
        dif = sum_re - sum_li
        self.set(MOTOR_DIR,FORWARD)
        self.set(MOTOR_L,self.geschwindigkeit)
        self.set(MOTOR_R,self.geschwindigkeit)
        if dif < 300 and dif > -300:
            print('Gerade')
            time.sleep(0.1)
        elif dif <= 300:
            print('Rechts')
            time.sleep(0.1)
            self.set(MOTOR_DIR,RECHTS)
            time.sleep(0.4)
        else:
            print('Links')
            time.sleep(0.1)
            self.set(MOTOR_DIR,LINKS)
            time.sleep(0.4)

    def set(self, addresse, wert): #Schickt 1 Byte mit einer Position und dann 1 Byte mit dem Inhalt
    	try:	       	
    	    bus.write_byte_data(MASTER_ADDRESS,addresse,wert)
    	    time.sleep(0.001)
    	except:
    	    print('set() Fehler')        	
    	return -1
 
    def get(self, position):#man bekommt den Wert der uebergebenen Position im Array des Arduino
        try:
            self.set(255,position) #Legt einen Pointer fest
            wert=(bus.read_byte(MASTER_ADDRESS)) #Arduino schickt Wert mit Position des Pointers
            time.sleep(0.001)
        except:
            print('get() Fehler')
            wert=0
        return wert
 
time1 = 60000
 
with picamera.PiCamera() as camera:
    camera.resolution = (64,64)
    camera.framerate = 25
    output = MyAnalysis(camera)
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    camera.awb_mode = 'auto'
    camera.start_recording(output, 'rgb')
    camera.wait_recording(time1)
    camera.stop_recording()
