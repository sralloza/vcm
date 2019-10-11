import logging
import platform
from typing import List, Union

from vcm import Options
from vcm.downloader.subject import Subject
from vcm.notifier.subject import NotifierSubject

from .email_backup import send_email

logger = logging.getLogger(__name__)

A = Union[List[str], str]
S = List[Subject]


def send_report(subjects: S, use_icons: bool, send_to: A):
    logger.info("Creating report")

    nlinks = 0
    new_subjects = [NotifierSubject.from_subject(subject) for subject in subjects]

    for subject in new_subjects:
        nlinks += len(subject.new_links)

    if not nlinks:
        logger.info("No new links, cancelling report")
        return

    logger.info("%d new links detected", nlinks)

    # Detect if plural should be used
    s = nlinks != 1
    info = f'enlace{"s" if s else ""} nuevo{"s" if s else ""}'

    message = (
        '<h2><span style="color: #339966; font-family: cambria; font-size: 35px;">'
        f'Se han encontrado {nlinks} {info}{":" if nlinks else "."}'
        "</span></h2><p>&nbsp;</p>"
    )

    for subject in new_subjects:
        if len(subject.new_links) == 0:
            continue
        message += (
            '<h2><span style="color: #000000; font-family: cambria; font-size: 20px;">'
            f'<a href="{subject.url}"  style="color:black'
            f';text-decoration: none">{subject.name.title()}</a></span></h2>'
        )

        for link in subject.new_links:
            message += "<ul>"
            if use_icons:
                message += '<li style="list-style: none;">'

                if Options.USE_BASE64_ICONS:
                    message += f"<img src='data:image/png;base64,{link.icon_data_64}' width='24' "
                else:
                    message += f'<img src="{link.icon_url}" width="24" '

                message += 'height="24" style="margin-bottom: -0.5em;">'

                # if link.is_teluva:
                #     message += (
                #         f'<img src="{link.icon_url}" width="24" '
                #         'height="24" style="margin-bottom: -0.5em;">'
                #     )

                message += "&nbsp;"
            else:
                message += "<li>"

            message += (
                '<span style="color: #000000; font-family: cambria; font-size: 15px;"><a href='
                f'"{link.url}">{link.name}</a></span></li></ul>'
            )

        message += "<p>&nbsp;</p>"

    message += "\n\nEjecutado en " + platform.system() + "."
    subject = "Se han encontrado %d enlaces nuevos" % nlinks

    return send_email(send_to, subject, message, origin="Rpi-VCM")
