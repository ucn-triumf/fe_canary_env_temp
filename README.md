# Canary Frontend

See also [this student work report](https://ucn.triumf.ca/edm/environmental-control/Kelton_Whiteaker_TRIUMF_2021_Work_Term_Report.pdf/view?searchterm=Kelton%20Whiteaker) for setup and details.

## Running

* Note that the mosquitto webserver needs to be running to receive any signals from the Canaries. This was added to the startup frontend script in May 2026


# Compilation notes

## Libraries

* You need to install the [arduino IDE](https://www.arduino.cc/en/software/)
  * On ubuntu you can install with `sudo apt install arduino`
  * I installed version 1.8.19
* Install needed libraries
  * [ESP8266 board libraries](https://github.com/esp8266/Arduino/tree/master) (see also [here](https://learn.adafruit.com/adafruit-feather-huzzah-esp8266/using-arduino-ide))
    * Files->Preferences. Enter `https://arduino.esp8266.com/stable/package_esp8266com_index.json` into the field for "Additional Boards Manager URLs"
    * Tools->Board: "Board model"->Board Manager. Search and install "ESP8266". I installed version 3.1.2
    * Tools->Board: "Board model"->ESP8266 Boards->Adafruit Feather HUZZAH ESP8266
  * [TriumfWiFi and TriumfMQTT libraries](https://docs.arduino.cc/software/ide-v1/tutorials/installing-libraries/)
    * Sketch->Include Library->Add .ZIP Library. Select the TriumfMQTT.zip and TriumfWiFi.zip files. 
    * Sketch->Include Library->TriumfMQTT
    * Sketch->Include Library->TriumfWiFi
  * Arduino standard libraries
    * Tools->Library Manager. Search and install the following:
      * [PubSubClient](https://docs.arduino.cc/libraries/pubsubclient/) (2.8.0)
      * [Adafruit SHT31](https://docs.arduino.cc/libraries/adafruit-sht31-library/) (2.2.2)
        * It will prompt to install dependencies, install all

## Other Settings

* Before uploading any code you need to disconnect the jumper cable connecting pin 16 to RST. 
* Arduino settings:
  * CPU Frequency: 80 MHz
  * Flash Size: 4M (3M SPIFFS)
  * Upload Speed: 115200
  * Port: varies by computer
* You may need to install the [CP2104 USB Driver](https://www.silabs.com/software-and-tools/usb-to-uart-bridge-vcp-drivers?tab=overview)