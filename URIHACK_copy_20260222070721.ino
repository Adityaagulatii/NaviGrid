#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>

#define SEALEVELPRESSURE_HPA (1013.25)

Adafruit_BMP280 bmp;

void setup() {
  Serial.begin(9600);
  while(!Serial); 
  
  if (!bmp.begin(0x76)) {
    Serial.println(F("Could not find BMP280 sensor!"));
    while (1);
  }

  // Set sampling to "Fast" mode for more frequent updates
  bmp.setSampling(Adafruit_BMP280::MODE_NORMAL,
                  Adafruit_BMP280::SAMPLING_X1,     // Lower oversampling = faster
                  Adafruit_BMP280::SAMPLING_X4,      
                  Adafruit_BMP280::FILTER_X4,       // Light filtering for speed
                  Adafruit_BMP280::STANDBY_MS_1);   // Minimum standby time
}

void loop() {
  float currentAlt = bmp.readAltitude(SEALEVELPRESSURE_HPA);
  
  // Outputting values rapidly
  Serial.print(F("Alt: "));
  Serial.print(currentAlt, 1); // 1 decimal place for speed
  Serial.print(F("m | "));

  if (currentAlt >= 40.0 && currentAlt <= 42.0) {
    Serial.println(F("[ FLOOR 1 ]"));
  } th
  else if (currentAlt >= 44.0 && currentAlt <= 46.0) {
    Serial.println(F("[ FLOOR 2 ]"));
  } 
  else {
    Serial.println(F("...Moving..."));
  }

  // Changed to 200ms for 5 checks per second
  delay(200); 
}