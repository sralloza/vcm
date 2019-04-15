import logging
import threading
import time
from queue import Queue
from typing import List

import flask
import waitress

from ._threading import Worker
from .links import BaseLink
from .subject import Subject
from .time_operations import seconds_to_str

logger = logging.getLogger(__name__)


def runserver(queue: Queue, threadlist: List[Worker]):
    t0 = time.time()
    logger.info('STARTED STATUS SERVER')

    app = flask.Flask(__name__)

    @app.route('/')
    def index():
        return """<p id="content">Here will be content</p>
    
    <script>
        var clock = document.getElementById("content");
        var alerted = false;

        var interval = setInterval(() => {
            fetch("/feed")
            .then(response => {
                    response.text().then(t => {clock.innerHTML = t})
                }).catch(function(){
                    document.title = "Ejecución terminada";
                    clearInterval(interval);
                    if (alerted == false) {
                        alerted = true;
                        alert("VCD ha terminado la ejecución");
                        }
                    }
                );
            }, 1000);
    </script>
    """

    @app.route('/feed')
    def info_feed():
        def feed():
            status = '<title>VCD STATUS</title>'
            status += f'Execution time: {seconds_to_str(time.time() - t0, integer=True)}<br>'

            status += 'Unfinished <a href="/queue" target="blank" style="text-decoration:none">'
            # noinspection PyUnresolvedReferences
            status += f'tasks</a>: {queue.unfinished_tasks}<br>'
            status += f'Items left: {queue.qsize()}<br><br>'
            thread_status = 'Threads:<br>'
            idle = 0
            working = 0
            for thread in threadlist:
                thread_status += f'\t-{thread.to_log(integer=True)}<br>'

                if thread.status == 'working':
                    working += 1
                if thread.status == 'idle':
                    idle += 1

            status += f'Threads working: {working}<br>'
            status += f'Threads idle: {idle}<br><br>'
            status += thread_status

            yield status

        return flask.Response(feed(), mimetype='text')

    @app.route('/queue')
    def view_queue():
        output = '<title>Queue content</title><h1>Queue</h1>'
        # noinspection PyUnresolvedReferences
        for i, elem in enumerate(list(queue.queue)):
            if isinstance(elem, BaseLink):
                status = f'{elem.subject.name} → {elem.name}'
            elif isinstance(elem, Subject):
                status = f'{elem.name}'
            else:
                status = 'None'

            output += str(i + 1) + ' → ' + status + '<br>'

        return output

    t = threading.Thread(name='vcd-status', target=waitress.serve, daemon=True, args=(app,),
                         kwargs={'port': 80, 'host': '0.0.0.0', '_quiet': True,
                                 'clear_untrusted_proxy_headers': True})
    t.start()
    return t
