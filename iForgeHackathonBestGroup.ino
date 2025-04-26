#define X_STEP_PIN         54
#define X_DIR_PIN          55
#define X_ENABLE_PIN       38

void setup() {
  pinMode(X_STEP_PIN, OUTPUT);
  pinMode(X_DIR_PIN, OUTPUT);
  pinMode(X_ENABLE_PIN, OUTPUT);

  // Enable the motor (LOW signal)
  digitalWrite(X_ENABLE_PIN, LOW);
}

void loop() {
  // Rotate 360 degrees (assuming 200 steps per revolution)
  for (int i = 0; i < 200; i++) {
    digitalWrite(X_STEP_PIN, HIGH);
    delayMicroseconds(1000); // Adjust delay for desired speed
    digitalWrite(X_STEP_PIN, LOW);
    delayMicroseconds(1000); // Adjust delay for desired speed
  }

  // Stop after one revolution
  while(1);
}