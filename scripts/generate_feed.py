#!/usr/bin/env python3
"""
Genera feed.xml (RSS para podcasts) a partir de los MP3 en la carpeta /episodes.
Se ejecuta automáticamente via GitHub Actions cada vez que hay un push con MP3 nuevos.
"""

import os
import glob
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from mutagen.mp3 import MP3
from xml.sax.saxutils import escape
from urllib.parse import quote
# ============ CONFIGURA ESTOS DATOS ============
GITHUB_USER = "b62urmaj"
REPO_NAME = "mi-podcats-"
PODCAST_TITLE = "Mi Podcast"
PODCAST_DESCRIPTION = "curso de inglés"
PODCAST_AUTHOR = "Juan Carlos"
PODCAST_EMAIL = "juancarlos.urbanomarmol@gmail.com"
PODCAST_IMAGE = f"https://{GITHUB_USER}.github.io/{REPO_NAME}/cover.jpg"
PODCAST_LANGUAGE = "es-es"
PODCAST_CATEGORY = "Technology"
# =================================================

RAW_BASE = f"https://{GITHUB_USER}.github.io/{REPO_NAME}/episodes"
EPISODES_DIR = os.path.join(os.path.dirname(__file__), "..", "episodes")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "feed.xml")


def get_mp3_duration_seconds(path):
    try:
        audio = MP3(path)
        return int(audio.info.length)
    except Exception:
        return 0


def seconds_to_hms(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:02}"


def build_items(mp3_files):
    items = []
    base_date = datetime.now(timezone.utc)
    for i, filepath in enumerate(sorted(mp3_files)):
        filename = os.path.basename(filepath)
        title = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ")
        filesize = os.path.getsize(filepath)
        duration = get_mp3_duration_seconds(filepath)
        pub_date = base_date - timedelta(days=i)
        url = f"{RAW_BASE}/{quote(filename)}"

        item = f"""    <item>
      <title>{escape(title)}</title>
      <description>{escape(title)}</description>
      <enclosure url="{escape(url)}" length="{filesize}" type="audio/mpeg" />
      <guid isPermaLink="false">{escape(filename)}</guid>
      <pubDate>{format_datetime(pub_date)}</pubDate>
      <itunes:duration>{seconds_to_hms(duration)}</itunes:duration>
      <itunes:explicit>false</itunes:explicit>
    </item>"""
        items.append(item)
    return "\n".join(items)


def build_feed():
    mp3_files = glob.glob(os.path.join(EPISODES_DIR, "*.mp3"))
    if not mp3_files:
        print("No se encontraron MP3 en /episodes")

    items_xml = build_items(mp3_files)
    now = format_datetime(datetime.now(timezone.utc))

    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>{escape(PODCAST_TITLE)}</title>
    <description>{escape(PODCAST_DESCRIPTION)}</description>
    <language>{PODCAST_LANGUAGE}</language>
    <link>{RAW_BASE}</link>
    <lastBuildDate>{now}</lastBuildDate>
    <itunes:author>{escape(PODCAST_AUTHOR)}</itunes:author>
    <itunes:owner>
      <itunes:name>{escape(PODCAST_AUTHOR)}</itunes:name>
      <itunes:email>{escape(PODCAST_EMAIL)}</itunes:email>
    </itunes:owner>
    <itunes:image href="{escape(PODCAST_IMAGE)}" />
    <itunes:category text="{escape(PODCAST_CATEGORY)}" />
    <itunes:explicit>false</itunes:explicit>
    <image>
      <url>{escape(PODCAST_IMAGE)}</url>
      <title>{escape(PODCAST_TITLE)}</title>
      <link>{RAW_BASE}</link>
    </image>
{items_xml}
  </channel>
</rss>
"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(feed)
    print(f"feed.xml generado con {len(mp3_files)} episodio(s)")


if __name__ == "__main__":
    build_feed()
