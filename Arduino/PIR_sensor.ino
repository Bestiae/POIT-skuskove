int speaker = 3;
int ledPin = 6;
int inputPin = 8;               
int val = 0;                   
 
void setup() {
  pinMode(ledPin, OUTPUT);     
  pinMode(inputPin, INPUT);    
  pinMode(speaker, OUTPUT);
  digitalWrite(ledPin, LOW);
 
  Serial.begin(9600);
}
 
void loop(){
//tone(speaker, 500);
// HIGH -> THE WAY THAT ARDUINO DISCRIBE STATE ON
val = digitalRead(inputPin);
  if(val == HIGH){
    digitalWrite(ledPin, HIGH);
    digitalWrite(speaker, HIGH);
    Serial.println(val);
    delay(500);
  }else{
   digitalWrite(ledPin, LOW);
   digitalWrite(speaker, LOW);
    Serial.println(val);
    delay(500); 
  }
}
