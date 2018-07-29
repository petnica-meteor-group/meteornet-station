/*
 * linux.c
 *
 * Copyleft 2018 Vladimir Nikolić
 */

#ifdef __linux__

#include "serial.h"

#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <arpa/inet.h>

static const char* TTY_PATH = "/dev/ttyACM0";
static const int TIMEOUT_WINDOW = 20; // Tenths of a second
static const int INIT_WAIT_SECONDS = 2;

static int tty;

int baud2constant(const int baud)
{
    switch (baud)
    {
        case 4800: return B4800;
        case 9600: return B9600;
        case 19200: return B19200;
        case 38400: return B38400;
        case 57600: return B57600;
        default: return -1;
    }
}

int port_init() {
	tty = open(TTY_PATH, O_RDWR | O_NOCTTY);
    if (tty == -1) {
        return -1;
    } else {
        fcntl(tty, F_SETFL, 0);
    }

    struct termios options;
    tcgetattr(tty, &options);

    // Set baud rate
    cfsetispeed(&options, baud2constant(BAUD_RATE));
    cfsetospeed(&options, baud2constant(BAUD_RATE));

    // Necessary flags
    options.c_cflag |= (CLOCAL | CREAD);

    // Set character size and disable parity
    options.c_cflag &= ~PARENB;
    options.c_cflag &= ~CSTOPB;
    options.c_cflag &= ~CSIZE;
    options.c_cflag |= CS8;

    // Enable the following line if parity is turned on
    // options.c_iflag |= (INPCK | ISTRIP); //Enable parity check and strip

    // Disable hardware and software flow control respectively
    options.c_cflag &= ~CRTSCTS;
    options.c_iflag &= ~(IXON | IXOFF | IXANY);

    options.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG); // Enable raw input

    options.c_oflag &= ~OPOST; // Enable raw output

    options.c_cc[VMIN] = 0;
    options.c_cc[VTIME] = TIMEOUT_WINDOW;

    tcsetattr(tty, TCSANOW, &options);

	sleep(INIT_WAIT_SECONDS);

	return 0;
}

int port_end() {
	return close(tty);
}

unsigned bytes_write(const uint8_t *buffer, const unsigned n) {
	return write(tty, buffer, n);
}

unsigned bytes_read(uint8_t *buffer, const unsigned n) {
	return read(tty, buffer, n);
}

#endif /* __linux__ */
