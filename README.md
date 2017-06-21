# Multicast service discovery in Python

An application written in [python 2.7](https://www.python.org/) and [PythonCard](http://pythoncard.sourceforge.net/) - [blog announcement](http://rainbowheart.ro/557).

I have discovered that after 11 years since latest update (2006) of [PythonCard](http://pythoncard.sourceforge.net/), the solution still works in Windows and Linux, even with latest [wx Python](https://wxpython.org/), 3.0.2.0.

I have many projects based on [PythonCard](http://pythoncard.sourceforge.net/) which works both on Windows and Linux.

The program register itself as an UDP server and, in a dedicated thread, send UDP multicast message and record the response.

It is possibile to run multiple instances of same program on Windows and Linux.

Two instances running each in Windows 10 and Linux mint, total 4 nodes on network:

![On Windows 10](http://rainbowheart.ro/static/uploads/1/2017/6/observer_windows10.jpg)

![On Linux Mint](http://rainbowheart.ro/static/uploads/1/2017/6/observer_linux.jpg)

The program require an ini file, config.ini, created like that:

```ini
;
; comments starts with ; or #
;

TITLE = UDP Multicast Observer

;if not defined nodename => random generated
;nodename = node1

remove_timeout = 5	  ;after how many seconds inactive node is removed

multicast_addr = 224.3.4.5

multicast_port = 45566

```

I use this program to test the network and to debug the cluster solutions I am building.

License-free software.

Feel free to use this software for both personal and commercial.
