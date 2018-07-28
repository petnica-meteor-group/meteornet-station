/*
 * avr.cpp
 *
 * Copyleft 2018 Vladimir Nikolić
 */

#ifdef __AVR

#include <HardwareSerial.h>
extern "C" {
#include "serial.h"
}

extern HardwareSerial Serial;

int port_init() {
    Serial.begin(BAUD_RATE);
	return 0;
}

int port_end() {
    return 0;
}

unsigned bytes_write(const uint8_t *buffer, const unsigned n) {
    return Serial.write(buffer, n);
}

unsigned bytes_read(uint8_t *buffer, const unsigned n) {
    unsigned bytes = 0;
    while (Serial.available() > 0 && bytes < n) {
        *(buffer + bytes) = Serial.read();
        bytes++;
    }
    return bytes;
}

#endif /* __AVR */
