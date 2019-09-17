import logging
import threading
import time
from queue import Queue
from typing import List

import flask
import waitress

from vcm.downloader.links import BaseLink
from vcm.downloader.subject import Subject
from ._threading import Worker, ThreadStates
from .time_operations import seconds_to_str

logger = logging.getLogger(__name__)


def runserver(queue: Queue, threadlist: List[Worker]):
    t0 = time.time()
    logger.info('STARTED STATUS SERVER')

    app = flask.Flask(__name__)

    @app.errorhandler(404)
    def back_to_index(error):
        return flask.redirect(flask.url_for('index'))

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
                        //alert("VCM ha terminado la ejecución");
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

            colors = {'orange': 0, 'red': 0, 'green': 0, 'magenta': 0}

            for thread in threadlist:
                temp_status, status_code = thread.to_log(integer=True)

                if status_code == 4:
                    colors['magenta'] += 1
                if status_code == 3:
                    colors['red'] += 1
                elif status_code == 2:
                    colors['orange'] += 1
                elif status_code == 1:
                    colors['green'] += 1
                thread_status += f'\t-{temp_status}<br>'

                try:
                    if thread.state == ThreadStates.working:
                        working += 1
                    if thread.state == ThreadStates.idle:
                        idle += 1
                except AttributeError:
                    pass

            colors = list(colors.items())
            colors.sort(key=lambda x: x[-1], reverse=True)

            status += f'Threads working: {working}<br>'
            status += f'Threads idle: {idle}<br><br>'
            status += f'Codes:<br>'
            status += '<br>'.join(
                [f'<font color="{x[0]}">-{x[0]}: {x[1]}</font>' for x in colors]) + '<br><br>'
            status += thread_status

            yield status

        return flask.Response(feed(), mimetype='text')

    # noinspection PyUnresolvedReferences
    @app.route('/queue')
    def view_queue():
        output = f'<title>Queue content ({len(queue.queue)} remaining)</title>'
        output += f'<h1>Queue content ({len(queue.queue)} remaining)</h1>'
        for i, elem in enumerate(list(queue.queue)):
            if isinstance(elem, BaseLink):
                status = f'{elem.subject.name} → {elem.name}'
            elif isinstance(elem, Subject):
                status = f'{elem.name}'
            else:
                status = 'None'

            output += f'{i + 1:03d} → {status}<br>'

        return output

    t = threading.Thread(name='vcd-state', target=waitress.serve, daemon=True, args=(app,),
                         kwargs={'port': 80, 'host': '0.0.0.0', '_quiet': True,
                                 'clear_untrusted_proxy_headers': True})
    t.start()
    return t
