// Motor A connections
#define PWMA 3
#define AIN1 4
#define AIN2 5
// Motor B connections
#define PWMB 6
#define BIN1 7
#define BIN2 8
// Standby pin
#define STBY 2

void setup_motors() {
  pinMode(PWMA, OUTPUT);
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(PWMB, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);
  pinMode(STBY, OUTPUT);
  
  // Activate the driver
  digitalWrite(STBY, HIGH);
}

void move_forward(int speed) {
  // Motor A forward
  digitalWrite(AIN1, HIGH);
  digitalWrite(AIN2, LOW);
  analogWrite(PWMA, speed);
  
  // Motor B forward
  digitalWrite(BIN1, HIGH);
  digitalWrite(BIN2, LOW);
  analogWrite(PWMB, speed);
}

void move_backward(int speed) {
  // Motor A backward
  digitalWrite(AIN1, LOW);
  digitalWrite(AIN2, HIGH);
  analogWrite(PWMA, speed);
  
  // Motor B backward
  digitalWrite(BIN1, LOW);
  digitalWrite(BIN2, HIGH);
  analogWrite(PWMB, speed);
}

void turn_left(int speed) {
  // Motor A backward
  digitalWrite(AIN1, LOW);
  digitalWrite(AIN2, HIGH);
  analogWrite(PWMA, speed);
  
  // Motor B forward
  digitalWrite(BIN1, HIGH);
  digitalWrite(BIN2, LOW);
  analogWrite(PWMB, speed);
}

void turn_right(int speed) {
  // Motor A forward
  digitalWrite(AIN1, HIGH);
  digitalWrite(AIN2, LOW);
  analogWrite(PWMA, speed);
  
  // Motor B backward
  digitalWrite(BIN1, LOW);
  digitalWrite(BIN2, HIGH);
  analogWrite(PWMB, speed);
}

void stop_motors() {
  analogWrite(PWMA, 0);
  analogWrite(PWMB, 0);
}
