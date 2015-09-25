#! /bin/bash

start() {
    echo "start uwsgi..."
    cd /usr/local/cdn
    uwsgi -x djangochina_socket.xml

}

stop() {
    echo "kill process of uwsgi..."
    echo `/sbin/pidof -s uwsgi`
    kill -9 `/sbin/pidof uwsgi`
}

restart() {
    echo -n "uwsgi restart..."
    echo
    stop
    echo '---------------------------------------------'
    start
}

case "$1" in
 start)
     start;;
 stop)
     stop;;
 restart)
     restart;;
 *)
     echo "Usage: $0 {start|stop|restart}"
     exit 1
esac