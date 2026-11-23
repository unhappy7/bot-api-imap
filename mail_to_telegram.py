import email
import imaplib
import json
import os
import re
import sys
import time
from email.header import decode_header, make_header
from email.utils import parseaddr
from html import unescape

import requests

try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass


def require(name):
    value = os.environ.get(name, "").strip()
    if not value:
        sys.exit(f"Error: environment variable {name} is not set (check your .env file).")
    return value


IMAP_HOST = os.getenv("IMAP_HOST", "imap.gmail.com")
IMAP_USER = require("IMAP_USER")
IMAP_PASSWORD = require("IMAP_PASSWORD")
BOT_TOKEN = require("BOT_TOKEN")
CHAT_IDS = [c.strip() for c in require("CHAT_ID").split(",") if c.strip()]
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))
MAX_BODY_CHARS = int(os.getenv("MAX_BODY_CHARS", "1000"))
ALLOWED_SENDERS = [
    s.strip().lower() for s in os.getenv("ALLOWED_SENDERS", "").split(",") if s.strip()
]
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")


def log(message):
    print(message, flush=True)


def redact(text):
    """Never let the bot token end up in logs."""
    return str(text).replace(BOT_TOKEN, "***")


def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_state(last_uid, uidvalidity):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_uid": last_uid, "uidvalidity": uidvalidity}, f)


def decode_str(value):
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value)))
    except Exception:
        return value


def html_to_text(raw_html):
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", "", raw_html)
    text = re.sub(r"(?i)<br\s*/?>|</p>|</div>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    return re.sub(r"\n\s*\n+", "\n\n", text).strip()


def get_body(msg):
    plain, html_part = None, None
    parts = msg.walk() if msg.is_multipart() else [msg]
    for part in parts:
        if part.get_content_disposition() == "attachment":
            continue
        ctype = part.get_content_type()
        if ctype not in ("text/plain", "text/html"):
            continue
        payload = part.get_payload(decode=True)
        if payload is None:
            continue
        charset = part.get_content_charset() or "utf-8"
        try:
            text = payload.decode(charset, errors="replace")
        except LookupError:
            text = payload.decode("utf-8", errors="replace")
        if ctype == "text/plain" and plain is None:
            plain = text
        elif ctype == "text/html" and html_part is None:
            html_part = text
    if plain:
        return plain.strip()
    if html_part:
        return html_to_text(html_part)
    return ""


def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    delivered = 0
    for chat_id in CHAT_IDS:
        try:
            resp = requests.post(
                url,
                json={
                    "chat_id": chat_id,
                    "text": text[:4096],
                    "disable_web_page_preview": True,
                },
                timeout=20,
            )
            resp.raise_for_status()
            delivered += 1
        except Exception as e:
            log(f"Couldn't send to {chat_id}: {redact(e)}")
    if delivered == 0:
        raise RuntimeError("The message was not delivered to any recipient.")


def get_uidvalidity(imap):
    _, data = imap.response("UIDVALIDITY")
    try:
        return int(data[0])
    except (TypeError, ValueError, IndexError):
        return None


def process_mailbox():
    state = load_state()
    last_uid = state.get("last_uid")

    with imaplib.IMAP4_SSL(IMAP_HOST) as imap:
        imap.login(IMAP_USER, IMAP_PASSWORD)
        status, _ = imap.select("INBOX", readonly=True)
        if status != "OK":
            raise RuntimeError("Could not open INBOX.")
        uidvalidity = get_uidvalidity(imap)

        if last_uid is not None and state.get("uidvalidity") not in (None, uidvalidity):
            log("UIDVALIDITY changed: resetting state, old emails are skipped.")
            last_uid = None

        if last_uid is None:
            status, data = imap.uid("SEARCH", None, "ALL")
            uids = [int(u) for u in data[0].split()] if status == "OK" and data[0] else []
            save_state(max(uids) if uids else 0, uidvalidity)
            log("First launch: old emails are skipped.")
            return

        status, data = imap.uid("SEARCH", None, f"UID {last_uid + 1}:*")
        if status != "OK" or not data[0]:
            return

        new_uids = sorted(int(u) for u in data[0].split() if int(u) > last_uid)

        for uid in new_uids:
            status, msg_data = imap.uid("FETCH", str(uid), "(BODY.PEEK[])")
            if status != "OK" or not msg_data or not msg_data[0]:
             
                log(f"Could not fetch UID {uid}, will retry.")
                break

            msg = email.message_from_bytes(msg_data[0][1])
            name, addr = parseaddr(msg.get("From", ""))
            name = decode_str(name)
            subject = decode_str(msg.get("Subject", "")) or "(no subject)"

            if ALLOWED_SENDERS and addr.lower() not in ALLOWED_SENDERS:
                save_state(uid, uidvalidity)
                continue

            body = get_body(msg)
            if len(body) > MAX_BODY_CHARS:
                body = body[:MAX_BODY_CHARS] + "…"

            sender = f"{name} <{addr}>" if name else addr
            send_to_telegram(f"📧 {sender}\nТема: {subject}\n\n{body}")

            save_state(uid, uidvalidity)
            log(f"Forwarded UID {uid}: {subject}")


def main():
    log(
        f"Watching {IMAP_USER} on {IMAP_HOST}, interval {CHECK_INTERVAL}s, "
        f"recipients: {len(CHAT_IDS)}"
    )
    while True:
        try:
            process_mailbox()
        except Exception as e:
            log(f"Error: {redact(e)}")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
