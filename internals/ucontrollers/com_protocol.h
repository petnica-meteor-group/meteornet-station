/*
 * com_protocol.h
 *
 *  Copyright 2018 Vladimir Nikolić
 */

#ifndef COMM_PROTOCOL_H
#define COMM_PROTOCOL_H

typedef enum Commands {
    NIGHT = 0,
    DAY,
    NAME_GET,
    MEASUREMENTS_GET
} Command;

#endif /* COM_PROTOCOL_H */
