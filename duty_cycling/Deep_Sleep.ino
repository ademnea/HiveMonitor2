#include <config.h>
#include <ds3231.h>

#include <Wire.h>
#include <RTClib.h>

// Do not remove the include below
#include "Arduino_Sleep_DS3231_Wakeup.h"

RTC_DS3231 rtc;

/*
 Low Power SLEEP modes for Arduino UNO/Nano
 using Atmel328P microcontroller chip.

 For full details see my video #115
 at https://www.youtube.com/ralphbacon
 (Direct link to video: https://TBA)

This sketch will wake up out of Deep Sleep when the RTC alarm goes off

 All details can be found at https://github.com/ralphbacon

 */
#include "Arduino.h"
#include <avr/sleep.h>
#include <wire.h>
#include <DS3231.h>


const int relaypin = 12; // Pin connected to the relay module
#define sleepPin 9  // When low, makes 328P go to sleep
#define wakePin 2   // when low, makes 328P wake up, must be an interrupt pin (2 or 3 on ATMEGA328P)
#define ledPin 13    // output pin for the LED (to show it is awake)
const int pi_uptime_minutes = 3;
// double uptime_millis = pi_uptime_minutes * 60 * 1000;
int count = 1;

// DS3231 alarm time
uint8_t wake_HOUR;
uint8_t wake_MINUTE;
uint8_t wake_SECOND;
#define BUFF_MAX 256

///* A struct is a structure of logical variables used as a complete unit
// struct ts {
//    uint8_t sec;         /* seconds */
//    uint8_t min;         /* minutes */
//    uint8_t hour;        /* hours */
//    uint8_t mday;        /* day of the month */
//    uint8_t mon;         /* month */
//    int16_t year;        /* year */
//    uint8_t wday;        /* day of the week */
//    uint8_t yday;        /* day in the year */
//    uint8_t isdst;       /* daylight saving time */
//    uint8_t year_s;      /* year in short notation*/
// #ifdef CONFIG_UNIXTIME
//    uint32_t unixtime;   /* seconds since 01.01.1970 00:00:00 UTC*/
// #endif
// };
struct ts t;

// Standard setup( ) function
void setup() {
	Serial.begin(9600);
  Serial.println();

	// Keep pins high until we ground them
	pinMode(sleepPin, INPUT_PULLUP);
	pinMode(wakePin, INPUT_PULLUP);

	// Flashing LED just to show the �Controller is running
	digitalWrite(ledPin, LOW);
	pinMode(ledPin, OUTPUT);

	// Clear the current alarm (puts DS3231 INT high)
	Wire.begin();
	DS3231_init(DS3231_CONTROL_INTCN);
	DS3231_clear_a1f();

  //RTC setup
  if (rtc.begin()) {
    // Serial.println("RTC initialized successfully!");
  } else {
    // Serial.println("Failed to initialize RTC!");
  }
  
  DateTime setTime(2023, 7, 27, 00, 00, 0);  // Modify this line with your desired time
  rtc.adjust(setTime);

  // Serial.println("Time has been set!");

  if (!(rtc.readSqwPinMode() & 0x80)) {
    // Serial.println("RTC is running!");
  } else {
    // Serial.println("RTC is NOT running!");
  }
  
  pinMode(relaypin, OUTPUT); // Set the power pin as an output

  //Turn off relay initially
  // digitalWrite(relaypin, HIGH); 
	// Serial.println("Setup completed.");

   digitalWrite(relaypin, LOW); 
    // Serial.println("Pi turned on!");
    
    //leave relay on for some time (180000 ms = 3 minutes)
    delay(180000);
    
    // Turn off relay
    digitalWrite(relaypin, HIGH); 
    // Serial.println("Pi turned off!");
}

// The loop turn relay on while not in sleep mode
// The loop turn relay on while not in sleep mode
void loop() {
  static uint8_t oldSec = 99;
  char buff[BUFF_MAX];

  // Serial.print("\n");
  // Serial.print("\n");
  // Serial.print("Count: ");
  // Serial.println(count);
  // Serial.print("Arduino awake: ");
  
  //get time from RTC
  DateTime now = rtc.now();

  // TIME DISPLAY
  Serial.print(now.year());
  Serial.print('/');
  Serial.print(now.month());
  Serial.print('/');
  Serial.print(now.day());
  Serial.print('\t');
  Serial.print(now.hour());
  Serial.print(':');
  Serial.print(now.minute());
  Serial.print(':');
  Serial.print(now.second());
  Serial.println();

  // Serial.println("Initializing...");
  // delay(120000); //sleep for 2 minutes to allow pi initialization

  // Turn on the relay only if count is an odd number
  if (count % 2 == 0) {
    digitalWrite(relaypin, LOW); 
    // Serial.println("Pi turned on!");
    
    //leave relay on for some time (180000 ms = 3 minutes)
    delay(180000);
    
    // Turn off relay
    digitalWrite(relaypin, HIGH); 
    // Serial.println("Pi turned off!");
  }

  // Increment the count at every iteration
  count++;

  // Set the DS3231 alarm to wake up in X seconds
  // Serial.println("Setting next alarm...");
  setNextAlarm();

  // Disable the ADC (Analog to digital converter, pins A0 [14] to A5 [19])
  static byte prevADCSRA = ADCSRA;
  ADCSRA = 0;

  /* Set the type of sleep mode we want. Can be one of (in order of power saving):

    SLEEP_MODE_IDLE (Timer 0 will wake up every millisecond to keep millis running)
    SLEEP_MODE_ADC
    SLEEP_MODE_PWR_SAVE (TIMER 2 keeps running)
    SLEEP_MODE_EXT_STANDBY
    SLEEP_MODE_STANDBY (Oscillator keeps running, makes for faster wake-up)
    SLEEP_MODE_PWR_DOWN (Deep sleep)
    */
  set_sleep_mode(SLEEP_MODE_PWR_DOWN);
  sleep_enable();

  // Turn of Brown Out Detection (low voltage)
  // Thanks to Nick Gammon for how to do this (temporarily) in software rather than
  // permanently using an avrdude command line.
  //
  // Note: Microchip state: BODS and BODSE only available for picoPower devices ATmega48PA/88PA/168PA/328P
  //
  // BODS must be set to one and BODSE must be set to zero within four clock cycles. This sets
  // the MCU Control Register (MCUCR)
  MCUCR = bit (BODS) | bit(BODSE);

  // The BODS bit is automatically cleared after three clock cycles so we better get on with it
  MCUCR = bit(BODS);

  // Ensure we can wake up again by first disabling interrupts (temporarily) so
  // the wakeISR does not run before we are asleep and then prevent interrupts,
  // and then defining the ISR (Interrupt Service Routine) to run when poked awake
  noInterrupts();
  attachInterrupt(digitalPinToInterrupt(wakePin), sleepISR, LOW);

  // Send a message just to show we are about to sleep
  // Serial.println("Bye !");
  // Serial.flush();

  // Allow interrupts now
  interrupts();

  // delay(120000); //sleep for 2 minutes to allow pi initialization

  // And enter sleep mode as set above
  sleep_cpu();

  // --------------------------------------------------------
  // �Controller is now asleep until woken up by an interrupt
  // --------------------------------------------------------

  // Wakes up at this point when wakePin is brought LOW - interrupt routine is run first
  // Serial.println("Arduino awake");

  // Clear existing alarm so int pin goes high again
  DS3231_clear_a1f();

  // Re-enable ADC if it was previously running
  ADCSRA = prevADCSRA;

  /* THIS IS THE ORIGINAL ELSE */
  // // Get the time
  // DS3231_get(&t);

  // // If the seconds has changed, display the (new) time
  // if (t.sec != oldSec)
  // {
  // 	// display current time
  // 	snprintf(buff, BUFF_MAX, "%d.%02d.%02d %02d:%02d:%02d\n", t.year,
  // 			t.mon, t.mday, t.hour, t.min, t.sec);
  // 	Serial.print(buff);
  // 	oldSec = t.sec;
  // }
}


// When wakePin is brought LOW this interrupt is triggered FIRST (even in PWR_DOWN sleep)
void sleepISR() {
	// Prevent sleep mode, so we don't enter it again, except deliberately, by code
	sleep_disable();

	// Detach the interrupt that brought us out of sleep
	detachInterrupt(digitalPinToInterrupt(wakePin));

	// Now we continue running the main Loop() just after we went to sleep

}

// Double blink just to show we are running. Note that we do NOT
// use the delay for the final delay here, this is done by checking
// millis instead (non-blocking)
// void doBlink() {
// 	static unsigned long lastMillis = 0;

// 	if (millis() > lastMillis + 1000)
// 	{  
// 		digitalWrite(ledPin, HIGH);
// 		delay(10);
// 		digitalWrite(ledPin, LOW);
// 		delay(200);
// 		digitalWrite(ledPin, HIGH);
// 		delay(10);
// 		digitalWrite(ledPin, LOW);
// 		lastMillis = millis();
// 	}
// }

// Set the next alarm
void setNextAlarm(void)
		{
	// flags define what calendar component to be checked against the current time in order
	// to trigger the alarm - see datasheet
	// A1M1 (seconds) (0 to enable, 1 to disable)
	// A1M2 (minutes) (0 to enable, 1 to disable)
	// A1M3 (hour)    (0 to enable, 1 to disable)
	// A1M4 (day)     (0 to enable, 1 to disable)
	// DY/DT          (dayofweek == 1/dayofmonth == 0)
	uint8_t flags[5] = { 0, 0, 0, 1, 1 };

	// get current time so we can calc the next alarm
	DS3231_get(&t);

	wake_SECOND = t.sec;
	wake_MINUTE = t.min;
	wake_HOUR = t.hour;

  // Add 1 hour to the current time 
  wake_HOUR = (wake_HOUR + 6) % 24;


	// Add a some seconds to current time. If overflow increment minutes etc.
	// wake_SECOND = wake_SECOND + 20;
	// if (wake_SECOND > 59)
	// {
	// 	wake_MINUTE++;
	// 	wake_SECOND = wake_SECOND - 60;

	// 	if (wake_MINUTE > 59)
	// 	{
	// 		wake_HOUR++;
	// 		wake_MINUTE -= 60;
	// 	}

  //   if (wake_HOUR > 23)
  //   {
  //     wake_HOUR = 0;
  //   }
	// }

  
  // Serial.print("Entering deep sleep , wake up time-> ");
  // Serial.print(wake_HOUR);
  // Serial.print(":");
  // Serial.print(wake_MINUTE);
  // Serial.print(":");
  // Serial.print(wake_SECOND);
  // Serial.println();

	// Set the alarm time (but not yet activated)
	DS3231_set_a1(wake_SECOND, wake_MINUTE, wake_HOUR, 0, flags);

	// Turn the alarm on
	DS3231_set_creg(DS3231_CONTROL_INTCN | DS3231_CONTROL_A1IE);
}
