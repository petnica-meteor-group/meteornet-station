#include "serial-com/serial_com.h"
#include "com_protocol.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define RESULT_BUFFER_SIZE 128

const char *COMMAND_SENT_MSG = "Command sent.\n";

const char *CONNECTED_MSG = "Connected.\n";
const char *DISCONNECTED_MSG = "Disconnected.\n";

const char *ERROR_MISSING_ARGUMENT_MSG = "ERROR: Missing argument.\n";
const char *ERROR_NOT_CONNECTED_MSG = "ERROR: Not connected.\n";
const char *ERROR_DISCONNECTING_MSG = "ERROR: Did not properly disconnect.\n";
const char *ERROR_SEND_MSG = "ERROR: Could not send.\n";
const char *ERROR_RECEIVE_MSG = "ERROR: Could not receive.\n";

const char* init() {
    if (serial_init() != 0) {
        return ERROR_NOT_CONNECTED_MSG;
    }
    return CONNECTED_MSG;
}

const char* end() {
    if (serial_end() != 0) {
        return ERROR_DISCONNECTING_MSG;
    }
    return DISCONNECTED_MSG;
}

static char result[RESULT_BUFFER_SIZE];

const char* send_cmd(int cmd) {
    if (serial_send(cmd) != 0) {
        return ERROR_SEND_MSG;
    }
    strcpy(result, COMMAND_SENT_MSG);

    if (cmd == DHT_INFO_GET) {
        float hum;
        float temp;
        if ((serial_receive((uint32_t*)&hum) != 0) || (serial_receive((uint32_t*)&temp) != 0)) {
            return ERROR_RECEIVE_MSG;
        } else {
            sprintf(result + strlen(COMMAND_SENT_MSG), "%f %f\n", hum, temp);
        }
    }

    return result;
}
