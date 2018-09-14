#include "serial-com/serial_com.h"
#include "com_protocol.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

const char *COMMAND_SENT_MSG = "DEBUG: Microcontroller command sent.";

const char *CONNECTED_MSG = "DEBUG: Microcontrollers connected.";
const char *DISCONNECTED_MSG = "DEBUG: Microcontrollers disconnected.";

const char *ERROR_NOT_CONNECTED_MSG = "ERROR: A microcontroller could not connect.";
const char *ERROR_DISCONNECTING_MSG = "ERROR: A microcontroller did not disconnect properly.";
const char *ERROR_SEND_MSG = "ERROR: Could not send to a microcontroller.";
const char *ERROR_RECEIVE_MSG = "ERROR: Could not receive from a microcontroller.";

const char *END_STRING = "END";

static char result[256];

const char* init() {
    if (serial_init() != 0) return ERROR_NOT_CONNECTED_MSG;
    return CONNECTED_MSG;
}

const char* end() {
    if (serial_end() != 0) return ERROR_DISCONNECTING_MSG;
    return DISCONNECTED_MSG;
}

int get_ucontroller_count() {
    return serial_port_count;
}

const char* send_cmd(unsigned ucontroller, Command cmd) {
    if (serial_send(ucontroller, cmd) != 0) return ERROR_SEND_MSG;
    strcpy(result, COMMAND_SENT_MSG);

    unsigned i;
    uint32_t msg;
    char *current_char = ((char*)result) + strlen(COMMAND_SENT_MSG);
    *(current_char++) = '\n';
    for (;;) {
        if (serial_receive(ucontroller, &msg) != 0) return ERROR_RECEIVE_MSG;
        if (strncmp((char*)&msg, "END", sizeof(msg)) == 0) break;

        for (i = 0; i < sizeof(msg); i++) {
            if (((uint8_t*)&msg)[i] == 0) {
                *(current_char++) = '\n';
                break;
            }
            *(current_char++) = ((uint8_t*)&msg)[i];
        }
    }
    *(--current_char) = 0;

    return result;
}
