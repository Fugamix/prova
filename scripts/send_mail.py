#!/usr/bin/env python3
import argparse
import os
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path


def load_env_file(path: str):
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        print(f"Falta la variable requerida: {name}", file=sys.stderr)
        sys.exit(2)
    return value


def main():
    parser = argparse.ArgumentParser(description='Envia un correu en text o HTML via SMTP.')
    parser.add_argument('--env-file', default='/home/node/.openclaw/workspace/secrets/mail.env', help='Fitxer amb variables SMTP')
    parser.add_argument('--to', required=True, help='Destinatari')
    parser.add_argument('--subject', required=True, help='Assumpte')
    parser.add_argument('--text', help='Text pla del correu')
    parser.add_argument('--text-file', help='Fitxer de text pla')
    parser.add_argument('--html-file', help='Fitxer HTML')
    parser.add_argument('--from-name', help='Nom visible del remitent')
    args = parser.parse_args()

    load_env_file(args.env_file)

    host = require('SMTP_HOST')
    port = int(require('SMTP_PORT'))
    user = require('SMTP_USER')
    password = require('SMTP_PASS')
    mail_from = require('MAIL_FROM')

    text = args.text
    if args.text_file:
        text = Path(args.text_file).read_text(encoding='utf-8')
    html = None
    if args.html_file:
        html = Path(args.html_file).read_text(encoding='utf-8')

    if not text and not html:
        print('Has de passar --text, --text-file o --html-file', file=sys.stderr)
        sys.exit(2)

    msg = EmailMessage()
    msg['Subject'] = args.subject
    msg['From'] = f"{args.from_name} <{mail_from}>" if args.from_name else mail_from
    msg['To'] = args.to

    if text:
        msg.set_content(text)
    else:
        msg.set_content('Aquest correu conté una versió HTML.')

    if html:
        msg.add_alternative(html, subtype='html')

    with smtplib.SMTP(host, port) as smtp:
        smtp.starttls()
        smtp.login(user, password)
        smtp.send_message(msg)

    print(f"OK: correu enviat a {args.to}")


if __name__ == '__main__':
    main()
