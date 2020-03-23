import logging
import platform
from typing import List, Union

from vcm.core.settings import NotifySettings
from vcm.downloader.subject import Subject
from vcm.notifier.subject import NotifierSubject

from .email_backup import send_email

logger = logging.getLogger(__name__)

A = Union[List[str], str]
S = List[Subject]


# FORM_LIKE_A_STYLE = """<style>
#     .btn-link {
#     border: none;
#     outline: none;
#     background: none;
#     cursor: pointer;
#     color: #0000EE;
#     padding: 0;
#     text-decoration: underline;
#     font-family: inherit;
#     font-size: inherit;
# }
#     </style>"""


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
    s = "s" if nlinks != 1 else ""
    info = f"enlace{s} nuevo{s}"

    # message = f"<html><head>{FORM_LIKE_A_STYLE}</head><body>"
    message = '<!DOCTYPE html><html lang="es"><head><title>Virtual Campus Notifier</title></head><body>'
    message += (
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

        message += "<table>"
        for link in subject.new_links:
            message += '<tr style="height: 3em">'
            message += "<td>"
            if use_icons:
                message += f'<img src="{link.generated_icon_url}" width="24" alt="{link.icon_type.name}" '

                message += 'height="24" style="margin-bottom: -0.5em;">'

            message += f"</td><td>{link.to_html()}</td>"
            message += "</tr>"

        message += "</table>"

        message += "<p>&nbsp;</p>"

    message += "\n\nEjecutado en " + platform.system() + "."
    message += "</body></html>"
    subject = "Se han encontrado %d enlaces nuevos" % nlinks

    result = send_email(send_to, subject, message, origin="Rpi-VCM")

    if not result:
        logger.error("Error in email, removing new links")
        for subject in new_subjects:
            for link in subject.new_links:
                logger.info("Removing %s", link.name)
                link.delete()

    return result
