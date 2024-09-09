/**************************************************************************
  This sketch was created for the CVHS ROV and was intened for an Arduino Uno R3 with 
  PCB 2302-30302 as an additional hat.  Generally the sketch intakes a serial output from the Controller.py on the sub  

  The Serial string is parsed and incoming duty cycle value sent to the correct pwm pin: 
  JP1,JP2,JP3, and JP4 from D3,D5,D6,D9 respectively.  Pin 1 is GND, pin 2 (NA),and pin 3 (PWM).  
  In 4 Thruster Configuration 3 = Vertial Starboard (right), 5 = Vertical Port (left), 6 = Horizontal Starboard, 9 = Horizontal Port

  Effectively the Arduino is really only increasing the number of hardware pwm outputs but with the additon of more serial input/output 
  could be given enhanced functionallity as an autopilot.  

  Written by Christopher Holm for Oregon State University Robotics holmch@oregonstate.edu
  
  MIT license, all text above must be included in any redistribution
 *****************************************************************************
 Revision History
 2023-11-14 Intial Version CEH
 2024-01-24 Attempted Frequency based version
 2024-01-24 Revert to Intial voltage Version CEH 
 2024-01-25 Altering to Serial incoming because software pwm is too noisy
 **************************************************************************/
 // Required Libraries
#include <Servo.h>

// Define Constants 
byte servoPin1 = 3;
byte servoPin2 = 5;
byte servoPin3 = 6;
byte servoPin4 = 9;
const int BattPin = A1; //Leaving here to implement battery monitoring
const int numReadings = 10; 
const unsigned long serialTimeout = 500; // timeout of 0.5s if no input values set back to 1500...
Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;

// Define variables
int totalBatt = 0;
int readingsBatt[numReadings];
int readIndex = 0;
int freq1 = 1500;
int freq2 = 1500;
int freq3 = 1500;
int freq4 = 1500;
int dc1 = 50; // 50% duty cycle is 1500 
int dc2 = 50;
int dc3 = 50;
int dc4 = 50;
volatile bool newData = false;
String receivedData = "";
float avgBatt = 0;
float voltBatt = 0;
unsigned long lastSerialTime = millis();

// Define Functions
void serialEvent() { // read incoming line when available
  while (Serial.available() > 0){
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      newData = true; // set incoming data flag to true
      Serial.println(receivedData);
    } else{
      receivedData += inChar; // Add incoming Characters to received data
    }
  }
} 
// parse out pwm integers and thruster type
void parseSerialData(String data) {
  char *token = strtok(const_cast<char*>(data.c_str()), ",");
  while (token != NULL) {
    char pwmLabel[5];
    int dcValue = 0;
    if (sscanf(token, "%4[^:]:%d", pwmLabel, &dcValue) == 2) {
      if (strcmp(pwmLabel, "pwm1") == 0) {
        dc1 = dcValue;
      } else if (strcmp(pwmLabel, "pwm2") == 0) {
        dc2 = dcValue;
      } else if (strcmp(pwmLabel, "pwm3") == 0) {
        dc3 = dcValue;
      } else if (strcmp(pwmLabel, "pwm4") == 0) {
        dc4 = dcValue;
      }
    }
    token = strtok(NULL, ",");
  }
  //Serial.print("PWM1 Value: ");
  //Serial.print(dc1);
  //Serial.print(", PWM2 Value: ");
  //Serial.print(dc2);
  //Serial.print(", PWM3 Value: ");
  //Serial.print(dc3);
  //Serial.print(", PWM4 Value: ");
  //Serial.println(dc4);
}

void printoutgoing() {
  Serial.print("Freq1: ");
  Serial.print(freq1);
  Serial.print(", Freq2: ");
  Serial.print(freq2);
  Serial.print(", Freq3: ");
  Serial.print(freq3);
  Serial.print(", Freq4: ");
  Serial.print(freq4);
  Serial.print(", Battery Voltage: ");
  Serial.println(voltBatt);
}

void setup() {
 Serial.begin(115200);
 Serial.setTimeout(10);

 servo1.attach(servoPin1);
 servo2.attach(servoPin2);
 servo3.attach(servoPin3);
 servo4.attach(servoPin4);
 
 servo1.writeMicroseconds(1500); // send "stop" signal to ESC.
 servo2.writeMicroseconds(1500); 
 servo3.writeMicroseconds(1500);
 servo4.writeMicroseconds(1500);
 delay(6000); // delay to allow the ESC to recognize the stopped signal
 pinMode(LED_BUILTIN, OUTPUT);
 //initialize all readings to Zero
 for (int thisReading = 0; thisReading < numReadings; thisReading++) {
  readingsBatt[thisReading] = 0;
 }
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(10);
  //subtract the last Battery Reading;
  totalBatt = totalBatt - readingsBatt[readIndex];
  
  //read from the Battery:
  readingsBatt[readIndex] = analogRead(BattPin);

  //add the reading to the total:
  totalBatt = totalBatt + readingsBatt[readIndex];

  //advance to the next position in the array:
  readIndex = readIndex + 1;
  //at the end wrap back to zero
  if (readIndex >= numReadings) {
    readIndex = 0;
  }
 //calculate the average
 avgBatt = totalBatt / numReadings;
 
 //calculate voltage
 voltBatt = (avgBatt * (5.0 / 1023.0)) * 3.41; // voltage divider emperically derived....
 delay(10);
  if (newData) {
    //process incoming serial data
    Serial.println(receivedData);
    parseSerialData(receivedData);
    // reset flag and clear bugger
    newData = false;
    receivedData = "";
    // get time of this serial event
    lastSerialTime = millis();
  }
  
  unsigned long currentTime = millis();
  if (currentTime - lastSerialTime > serialTimeout) {
    //reset all pwm values
    dc1=dc2=dc3=dc4=50; 
    //Serial.print("no serial for ");
    //Serial.print((currentTime - lastSerialTime)/1000);
    //Serial.println(" seconds");
  }
  // Convert incoming duto cycle to outgoing value from 1100 to 1475 (negative) 1500 (stopped) 1525 to 1900 (Positive) Servo
  freq1 = map(dc1,0,100,1100,1900); // CW Thruster
  freq2 = map(dc2,0,100,1900,1100); // CCW Thruster
  freq3 = map(dc3,0,100,1100,1900); // CW Thruster
  freq4 = map(dc4,0,100,1900,1100); // CCW Thruster
   
  printoutgoing();

  if(freq1 < 1100 || freq1 > 1900) {
    Serial.println("Starboard Vertical not valid"); } else {
    servo1.writeMicroseconds(freq1); // Send signal to ESC.
  }
  if(freq2 < 1100 || freq2 > 1900) {
    Serial.println("Port Vertical not valid"); } else {
    servo2.writeMicroseconds(freq2); // Send signal to ESC.
  }
  if(freq3 < 1100 || freq3 > 1900) {
    Serial.println("Starboard Horizontal not valid"); } else {
    servo3.writeMicroseconds(freq3); // Send signal to ESC.
  }
  if(freq4 < 1100 || freq4 > 1900) {
    Serial.println("Port Horizontal not valid"); } else {
    servo4.writeMicroseconds(freq4); // Send signal to ESC.
  }
  digitalWrite(LED_BUILTIN,LOW);
  delay(100);
}
