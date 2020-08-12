from collections import defaultdict
from logging import getLogger
from pathlib import Path
from queue import Queue
from threading import Thread
from threading import enumerate as enumerate_threads
from time import time
from traceback import format_exc
from typing import List

import flask
import waitress

from vcm.core.utils import ErrorCounter

from .settings import settings
from .time_operations import seconds_to_str
from .workers import Killer, ThreadStates, Worker, running, state_to_color

logger = getLogger(__name__)


def runserver(queue: Queue, threadlist: List[Worker]):
    from vcm.downloader.subject import Subject
    from vcm.downloader.link import BaseLink

    t0 = time()

    app = flask.Flask(__name__)

    @app.errorhandler(404)
    def back_to_index(error):
        return flask.redirect(flask.url_for("index"))

    @app.errorhandler(500)
    def server_error(error):
        err = format_exc()
        err = err.replace("\n", "<br>").replace(" ", "&nbsp;" * 2)
        return flask.Response("server error: " + err, mimetype="text/html"), 500

    @app.route("/backend.js")
    def backend_js():
        data = Path(__file__).with_name("http-status-server.js").read_bytes()
        return flask.Response(data, mimetype="application/javascript")

    @app.route("/")
    def index():
        updates_in_one_second = 1 / settings.http_status_tickrate * 1000
        a = f"<script>const updatesInOneSecond = {updates_in_one_second}</script>\n"
        a += '<script src="/backend.js"></script>'
        return a + '<p id="content">Here will be content</p>'

    @app.route("/feed")
    def info_feed():
        def feed():
            status = "<title>VCM STATUS</title>"
            execution_time = seconds_to_str(time() - t0, integer=False)
            status += f"Execution time: {execution_time}<br>"

            status += 'Unfinished <a href="/queue" target="blank" style="text-decoration:none">'
            status += f"tasks</a>: {queue.unfinished_tasks}"

            if not running.is_set():
                status += '<font color="red"> [Shutting down]</font>'
            status += f"<br>Items left: {queue.qsize()}<br><br>"
            thread_status = "Threads (%d):" % count_threads()

            if ErrorCounter.has_errors():
                report = f'<font color="red">\t<b>[{ErrorCounter.report()}]</b></font>'
                thread_status += report

            thread_status += "<br>"

            colors, working, idle = get_thread_state_info()
            for thread in enumerate_threads():
                if not isinstance(thread, Worker):
                    continue

                temp_status = thread.to_log(integer=True)
                thread_status += f"\t-{temp_status}<br>"

            colors = list(colors.items())
            colors.sort(key=lambda x: x[-1], reverse=True)

            # status += f"Threads working: {working}<br>"
            # status += f"Threads idle: {idle}<br><br>"
            status += f"Codes:<br>"
            status += "<br>".join(
                [f'<font color="{x[0]}">-{x[0]}: {x[1]}</font>' for x in colors]
            )
            status += "<br><br>"
            status += thread_status

            return status

        return flask.Response(feed(), mimetype="text/html")

    @app.route("/queue")
    def view_queue():
        output = f"<title>Queue content ({len(queue.queue)} remaining)</title>"
        output += f"<h1>Queue content ({len(queue.queue)} remaining)</h1>"
        for i, elem in enumerate(list(queue.queue)):
            if isinstance(elem, BaseLink):
                status = f"{elem.subject.name} → {elem.name}"
            elif isinstance(elem, Subject):
                status = f"{elem.name}"
            else:
                status = "None"

            output += f"{i + 1:03d} → {status}<br>"

        return output

    t = HttpStatusServer(app)
    t.start()
    return t


class HttpStatusServer(Thread):
    def __init__(self, app):
        super().__init__()
        self.name = "http-status-server"
        self.app = app
        self.daemon = True
        self.port = settings.http_status_port
        self.logger = getLogger(__name__)

    def real_run(self):
        """Executes the status http web server using the waitress module."""

        self.logger.info("Starting status server on port %d", self.port)
        return waitress.serve(
            self.app,
            port=self.port,
            host="0.0.0.0",
            clear_untrusted_proxy_headers=True,
            _quiet=True,
        )

    def run(self):
        """Main execution of the thread.

        It is sepparated from real_run() to catch some exceptions (port associated)
        and re-run it. Currently no known exceptions are raised.
        """

        return self.real_run()


def get_thread_state_info():
    colors = defaultdict(int, {"green": 0, "orange": 0, "red": 0, "magenta": 0})
    working = 0
    idle = 0

    for thread in enumerate_threads():
        if not isinstance(thread, Worker):
            continue
        if isinstance(thread, Killer):
            continue
        state = thread.state
        color = state_to_color[state]
        colors[color.name] += 1

        if state == ThreadStates.idle:
            idle += 1

        if state.alias == "working":
            working += 1

    colors.pop("blue", None)
    return dict(colors), working, idle


def count_threads() -> int:
    nthreads = 0
    for thread in enumerate_threads():
        if isinstance(thread, Worker):
            nthreads += 1
    return nthreads
