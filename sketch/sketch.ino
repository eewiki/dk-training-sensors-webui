#include <Arduino.h>
#include <Arduino_RouterBridge.h>
#include <Arduino_Modulino.h>

ModulinoThermo thermo;
ModulinoDistance distance;

const int SEUIL_MM = 800;
const unsigned long COOLDOWN_MS = 10000;  // 1 Max notifications every 10 s
unsigned long lastSendMs = 0;

void setup() {
  Bridge.begin();
  Monitor.begin();
  Modulino.begin();

  thermo.begin();
  distance.begin();
}

void loop() {
  // 1) Periodic Sensors (1 Hz)
  static unsigned long lastSensorsMs = 0;
  unsigned long now = millis();

  if (now - lastSensorsMs >= 1000) {
    lastSensorsMs = now;

    float tempC = thermo.getTemperature();

    // We have to force float everywhere here to convert
    float tempF = ((float)tempC * 9.0f / 5.0f) + 32.0f;

    float hum  = thermo.getHumidity();

    Bridge.call("update_sensors", tempC, tempF, hum);

    Monitor.print("tempC="); Monitor.print(tempC, 2);
    Monitor.print(" tempF="); Monitor.print(tempF, 2);
    Monitor.print(" hum="); Monitor.println(hum, 2);
  }

  // 2) Detection presence via distance (20 ms)
  if (distance.available()) {
    int mm = (int)distance.get();
    bool presence = (mm > 0 && mm < SEUIL_MM);

    if (presence && (now - lastSendMs >= COOLDOWN_MS)) {
      lastSendMs = now;
      Bridge.call("presence_mm", mm);

      Monitor.print("PRESENCE mm="); Monitor.println(mm);
    }
  }

  delay(20);

}
