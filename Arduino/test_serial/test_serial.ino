int count = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  while(true){
    Serial.println(count);
    count++;
    delay(1000);
  }
}
