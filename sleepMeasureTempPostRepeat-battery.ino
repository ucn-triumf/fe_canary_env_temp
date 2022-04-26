/*
 * Copied from Kelton Whiteaker 2021 Work Term Report, with small edits
 * For use with canaries temperature monitor
 * 
 * Derek Fujimoto
 * Dec 2021
 */

#include "ESP8266WiFi.h"
#include "TriumfWiFi.h"
#include "TriumfMQTT.h"
#include "Wire.h"
#include "Adafruit_SHT31.h"
#include <EEPROM.h> // saves data after reset

#define SLEEP_TIME 300 // seconds
#define BATTERY_INTERVAL 5 // minutes

Adafruit_SHT31 sht31 = Adafruit_SHT31();

void setup() 
{
    Serial.begin(115200); // Sets the data rate in baud for serial data transmission
    Serial.println(); // Prints data to the serial port followed by a carriage return
    Serial.println("Welcome to Triumf T - dP - %RH canary readout");
    Wire.begin();   // Initiate Wire library, join I2C bus as a master (default)
    Wire.setClockStretchLimit(1e4); // unclear what this does. Nigel’s comment: "us"
    
    // Read temperature before things warm up:
    sht31.begin(0x45);
    int status = sht31.readStatus();
    if (status == 0xFFFF) 
    {
        Serial.println("Bad SHT35 status, no T and RH readings.");
    }
    
    float t = sht31.readTemperature();
    float rh = sht31.readHumidity();
    
    // float dewp = getDewPoint(t, rh);
    int batt = 100; // only used the first time this runs
    Serial.println(t);
    Serial.println(rh);
    EEPROM.begin(512);
    
    // get the current count from eeprom
    byte battery_count = EEPROM.read(0);
    // we only need this to happen once every BATTERY_INTERVAL minutes,
    // so we use eeprom to track the count between resets.
    // We check count >= BATTERY_INTERVAL * 60) / SLEEP_TIME because
    
    // it counts about 1x per SLEEP_LENGTH, so we want the total number of
    // SLEEP_LENGTHs to add up to (BATTERY_INTERVAL * 60)
    if(battery_count >= ((BATTERY_INTERVAL * 60) / SLEEP_TIME)) 
    {
        battery_count = 0; // reset counter
        batt = getBatteryLevel();
        EEPROM.write(1, batt); // keep battery level after reset
    }
    else 
    {
        battery_count++; // increment counter
        // if it’s not time to update, use the previous value
        batt = EEPROM.read(1);
    }

    // save the current count
    EEPROM.write(0, battery_count);
    EEPROM.commit();
    connectWiFi();
    WiFiClient wiFiClient; // make a client that can connect to a specified internet IP address and
    PubSubClient mqtt(DEFAULT_MQTT_SERVER, DEFAULT_MQTT_PORT, wiFiClient); // PubSubClient(IPAddress
    std::string topic = std::string(DEFAULT_MQTT_TOPIC) + "/" + macAddress(); // MAC address unique
    
    // Build up json string to post:
    std::string toPost = "";
    addItem(toPost, "temperature", t, 2);
    addItem(toPost, "relativehumidity", rh, 3);
    addItem(toPost, "battery", batt, 1);
    // addItem(toPost, "dewpoint", dewp, 1);
    addItem(toPost, ""); // Blank name terminates string
    post2MQTT(mqtt, topic, toPost); // Connects to Falkor, sends json string, disconnects
    ESP.deepSleep(SLEEP_TIME*1e6,WAKE_RF_DISABLED); // µs sleep time. Connect GPIO16 to RST for this to work.
    LowPower.powerDown()
}
    
void loop() {} // In Measure-Post-Sl  eep-Repeat mode, it never reaches loop: it sleeps then starts

float getDewPoint(float t, float rh)
{
    if (!isnan(t) and !isnan(rh))
    {
        float h = (log10(rh) - 2) / 0.4343 + (17.62 * t) / (243.12 + t);
        return 243.12*h/(17.62-h);
    }
    else
    {
        return std::numeric_limits<double>::quiet_NaN();
    }
}

int getBatteryLevel() 
{
    // read the battery level from the ESP8266 analog in pin.
    // analog read level is 10 bit 0-1023 (0V-1V).
    // our 1M & 220K voltage divider takes the max
    // lipo value of 4.2V and drops it to 0.758V max.
    // this means our min analog read value should be 580 (3.14V)
    // and the max analog read value should be 774 (4.2V).
    int level = analogRead(A0);

    // convert battery level to percent
    level = map(level, 580, 774, 0, 100);
    Serial.print("Battery level: "); Serial.print(level); Serial.println("%");
    return level;
}
