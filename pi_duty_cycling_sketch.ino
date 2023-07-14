#include <Wire.h>
#include <RTClib.h>

RTC_DS3231 rtc;
const int relaypin = 13; // Pin connected to the relay module

void setup() {
  Serial.begin(9600);

  if (rtc.begin()) {
    Serial.println("RTC initialized successfully!");
  } else {
    Serial.println("Failed to initialize RTC!");
  }
  
  DateTime setTime(2023, 6, 29, 7, 59, 55);  // Modify this line with your desired time
  rtc.adjust(setTime);

  Serial.println("Time has been set!");

  if (!(rtc.readSqwPinMode() & 0x80)) {
    Serial.println("RTC is NOT running!");
  } else {
    Serial.println("RTC is running!");
  }
  
  pinMode(relaypin, OUTPUT); // Set the power pin as an output
}

void loop() {
  DateTime now = rtc.now();

  // TIME DISPLAY
  Serial.print(now.year());
  Serial.print('/');
  Serial.print(now.month());
  Serial.print('/');
  Serial.print(now.day());
  Serial.print('\n');
  Serial.print(now.hour());
  Serial.print(':');
  Serial.print(now.minute());
  Serial.print(':');
  Serial.print(now.second());
  Serial.println();

    if (now.minute() < 5) {
      digitalWrite(relaypin, LOW); // Turn on the relay
      Serial.println("Relay turned on!");
    } else {
      digitalWrite(relaypin, HIGH); // Turn off the relay
      Serial.println("Relay turned off!");
    }
  
  delay(1000); // Wait for 1 second
}
