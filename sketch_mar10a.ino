#include <Wire.h>

#define SLAVE_ADDRESS 0x04

uint8_t speicher[11] = {0};

#define SERVO 9      // Die Pins mit denen die Sensoren und Motoren angeschlossen sind werden festgelegt
#define MOTOR_STANDBY 4
#define MOTOR_L 6
#define MOTOR_R 5
#define MOTORRICHTUNG_L 8
#define MOTORRICHTUNG_R 7
#define TASTER_1 15
#define TASTER_2 16
#define TASTER_3 17
#define TASTER_4 2
#define LAMPE 14

#define SERVO_WERT 0       // Die Array-Speicheraddressen werden definiert
#define MOTOR_L_WERT 2
#define MOTOR_R_WERT 3
#define MOTORRICHTUNG_WERT 4
#define TASTER_WERT 6
#define LAMPE_WERT 8
#define MOTOR_STANDBY_WERT 10

int number = 0; // Variable ´fuer die Position die Position an die im Speicher geschrieben werden soll
int pointer; // Pointer auf Stelle die bei sendData ausgelesen und gesendet wird
int taster1 = 1;
int taster2 = 1;
int taster3 = 1;
int taster4 = 1;

void setup() {
  Serial.begin(9600); // Baudrate wird festgelegt
  pinMode(SERVO, OUTPUT);   // Die Pins werden entweder als Input oder als Output definiert je nachdem ob 
  pinMode(MOTOR_L, OUTPUT);
  pinMode(MOTOR_R, OUTPUT);
  pinMode(MOTORRICHTUNG_L, OUTPUT);
  pinMode(MOTORRICHTUNG_R, OUTPUT);
  pinMode(MOTOR_STANDBY, OUTPUT);
  pinMode(LAMPE, OUTPUT);
  pinMode(TASTER_1, INPUT_PULLUP);
  pinMode(TASTER_2, INPUT_PULLUP);
  pinMode(TASTER_3, INPUT_PULLUP);
  pinMode(TASTER_4, INPUT_PULLUP);
  Wire.begin(SLAVE_ADDRESS); // bestimmte I2C Adresse wird festgelegt
  Wire.onReceive(receiveData); // Wenn Daten gesendet werden wird die Funktion reveiveData gestartet
  Wire.onRequest(sendData); // Auf Nachfrage werden Daten an den Raspberry gesendet
}

void loop() {   // in der loop werden dauerhaft alle Werte aktualisiert
  analogWrite(SERVO, speicher[SERVO_WERT]);
  analogWrite(MOTOR_L, speicher[MOTOR_L_WERT]);
  analogWrite(MOTOR_R, speicher[MOTOR_R_WERT]);
  digitalWrite(LAMPE, speicher[LAMPE_WERT]);
  digitalWrite(MOTORRICHTUNG_L, speicher[MOTORRICHTUNG_WERT] & 0b10000000);
  digitalWrite(MOTORRICHTUNG_R, (speicher[MOTORRICHTUNG_WERT] & 0b01000000)<<1);
  digitalWrite(MOTOR_STANDBY, speicher[MOTOR_STANDBY_WERT]);
  if (taster1 != 0){
    taster1 = digitalRead(TASTER_1);
  }
  if (taster2 != 0){
    taster2 = digitalRead(TASTER_2);
  }
  if (taster3 != 0){
    taster3 = digitalRead(TASTER_3);
  }
  if (taster4 != 0){
    taster4 = digitalRead(TASTER_4);
  }
  speicher[TASTER_WERT] = taster1 + 2*taster2 + 4*taster3 + 8*taster4;  // die aktuellen Tasterwerte werden für den Raspberry bereitgestellt
}

void receiveData(int byteCount){
  if (Wire.available()){
    number = Wire.read();  
    }
   if (number == 255){
     if (Wire.available()){
      pointer = Wire.read();
      }
    }
   else{
     while (Wire.available()){
       if(number<=10) {
         speicher[number]=Wire.read();
         }
       number++;
     }
     //showArray();
    }
}

void showArray(){
  for (int i=0; i<11; i++){
    Serial.println(speicher[i]);  
  }
}

// callback for sending data
void sendData() {
    if (pointer == TASTER_WERT){
      Wire.write(speicher[pointer]);
      taster1=1;
      taster2=1;
      taster3=1;
    }
    else{
      if (pointer>=10){
        Wire.write(speicher[TASTER_WERT]);
      }
      else{
        Wire.write(speicher[pointer]);
      }
    }
 }
