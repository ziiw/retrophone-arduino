#include <RotoPhone.h>
#include <Servo.h>

// INIT VARIABLES
// ###########
// ###########

// Rotophone
int number ;
RotoPhone roto(4,5);

// Hang
const int inPin = 3;
int valHang;
bool pick_up;
bool prevState;
int states[] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
int i;

// Raspberry
const int ledPin = 8;

// Ring
Servo myservo;
int ringTime;
int hangValue;


// SETUP
// ###########
// ###########
void setup() {
    // if you use debug don't forget to init Serial
    Serial.begin(9600);

    setupRoto();
    setupHang();
    setupServo();
}

// Setup Rotophone
void setupRoto() {
  number = 0;  
}


// Setup Hang
void setupHang() {
  valHang = 0;
  pick_up = false;
  prevState = false;
  i = 0;
  pinMode(inPin, INPUT);
}

// Setup Servo
void setupServo() {
  myservo.attach(2);
}



// MAIN LOOP
// ###########
// ###########
void loop() {
  loopRoto();
  loopHang();
  loopRaspberry();
//  Serial.println(digitalRead(inPin));
}

// Loop Raspberry
void loopRaspberry() {
  if (Serial.available()) {
    ring(Serial.readStringUntil('$').toInt());
  }
}

void ring(int n) {
  if(n == 10){
    
    ringTime = 0;
    
    hangValue = 0;
    
    while(ringTime < 70 && hangValue == 0){
      myservo.write(95);
      delay(70);
      myservo.write(115);
      delay(70);  

      ringTime ++;

      hangValue = digitalRead(inPin);
    }

    if(ringTime == 70 && hangValue == 0){
      Serial.println("tweet");
    }
  }
}

// Loop Rotophone
void loopRoto() {
  number = roto.number();
  
  if(number >= 0){
    // Send to Raspberry
    Serial.println(number);
  }

  // print value on each loop
  //roto.debug();
  //Serial.println(roto.isNum());
  delay(20);
}

// Loop Hang
void loopHang() {
  valHang = digitalRead(inPin);
  
  if(i == 25){
    // check if is hang or not
    int resultat = 0;
    for (int j=0; j <= 24; j++){
      resultat = resultat + states[j];
    } 
  
    if(resultat < 25){
      pick_up = true;
    }else{
      pick_up = false;
    }
    
    i = 0;
    resultat = 0;
  }

  if(pick_up){
    if(!prevState){
      Serial.println("pick_down"); 
      prevState = true;
    }
  }else{
    if(prevState){
      Serial.println("pick_up");
      prevState = false; 
    }
  }

  states[i] = valHang;
  i = i + 1;
}

void checkHang() {
  int resultat = 0;
  for (int j=0; j <= 24; j++){
    resultat = resultat + states[j];
//      Serial.println("Resultat:");
//      Serial.println(states[j]);
  } 

//  Serial.println(resultat);

  if(resultat < 25){
    pick_up = true;
  }else{
    pick_up = false;
  }
  
  i = 0;
  resultat = 0;
}
