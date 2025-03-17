#define TRIG_PIN 9
#define ECHO_PIN 10

// Variables for ultrasonic sensor
long duration;
int distance_cm;

void setup_ultrasonic() {
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
}

int measure_distance() {
  // Clear the TRIG_PIN
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  
  // Generate a 10μs pulse to TRIG_PIN
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  // Read the ECHO_PIN, return sound wave travel time in microseconds
  duration = pulseIn(ECHO_PIN, HIGH);
  
  // Calculate the distance
  distance_cm = duration * 0.034 / 2;
  
  return distance_cm;
}
