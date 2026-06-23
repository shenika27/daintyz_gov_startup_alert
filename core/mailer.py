"""네이버 SMTP 메일 발송."""
from __future__ import annotations

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

from . import config

NAVER_HOST = "smtp.naver.com"
NAVER_PORT = 465  # SSL


def send(subject: str, html_body: str) -> None:
    if not (config.NAVER_USER and config.NAVER_PASS):
        raise RuntimeError("NAVER_USER / NAVER_PASS 시크릿이 비어 있습니다.")

    msg = MIMEText(html_body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = formataddr(("창업지원 알리미", config.MAIL_FROM))
    recipients = [a.strip() for a in config.MAIL_TO.split(",") if a.strip()]
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP_SSL(NAVER_HOST, NAVER_PORT, timeout=config.HTTP_TIMEOUT) as smtp:
        smtp.login(config.NAVER_USER, config.NAVER_PASS)
        smtp.sendmail(config.MAIL_FROM, recipients, msg.as_string())
