/*
 * serial_com.h
 *
 * Copyleft 2018 Vladimir Nikolić
 */

#ifndef SERIAL_COM_H
#define SERIAL_COM_H

#include <stdint.h>

/*
 * All routines return 0 on success, and non-0 on failure.
 */

int serial_init();
int serial_end();
int serial_send(const uint32_t msg);
int serial_receive(uint32_t *msg);

#endif /* SERIAL_COM_H */
