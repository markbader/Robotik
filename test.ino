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
}

void loop() {   // in der loop werden dauerhaft alle Werte aktualisiert
  char c;
  char kommando;
  if(Serial.available()){
    c = Serial.read();
    if(c&0b10000000){
      Serial.write("comando");
      kommando = c&0b01111111;
    }
    else{
      if(kommando == '1'){
        speicher[MOTOR_L_WERT] = c*2;
      }
      else if(kommando == '2'){
        speicher[MOTOR_R_WERT] = c*2;
      }
      else if(kommando == '3'){
        speicher[MOTOR_STANDBY_WERT] = c;
      }
      else if(kommando == '4'){
        speicher[LAMPE_WERT] = c;
      }
      else if(kommando == '5'){
        speicher[MOTORRICHTUNG_WERT] = c;
      }
      else if(kommando == '6'){
        speicher[SERVO_WERT] = c*2;
      }
      Serial.write("data");
    }
  }
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
  speicher[TASTER_WERT] = taster1 + 2*taster2 + 4*taster3;  // die aktuellen Tasterwerte werden für den Raspberry bereitgestellt
}

void showArray(){
  for (int i=0; i<11; i++){
    Serial.println(speicher[i]);  
  }
}

// callback for sending data

