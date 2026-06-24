"""Generates a small SVG status badge for a certificate, safe to embed
publicly (e.g. <img src=".../api/badge/AUTH-XXXX.svg">) with no auth
required -- it only reveals AUTHENTIC/TAMPERED/UNKNOWN, not the file itself."""

COLORS = {
    "AUTHENTIC": "#166534",
    "TAMPERED": "#a02323",
    "UNTRUSTED": "#8a5a12",
    "UNKNOWN": "#726f68",
}


def _text_width(text, char_width=6.4):
    return max(int(len(text) * char_width) + 14, 40)


def build_badge_svg(status_label):
    color = COLORS.get(status_label, COLORS["UNKNOWN"])
    left_text = "aqtify"
    right_text = status_label.lower()

    left_w = _text_width(left_text)
    right_w = _text_width(right_text)
    total_w = left_w + right_w
    h = 20

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="{h}" role="img" aria-label="{left_text}: {right_text}">
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#fff" stop-opacity=".08"/>
    <stop offset="1" stop-opacity=".08"/>
  </linearGradient>
  <clipPath id="r"><rect width="{total_w}" height="{h}" rx="3" fill="#fff"/></clipPath>
  <g clip-path="url(#r)">
    <rect width="{left_w}" height="{h}" fill="#2b2a26"/>
    <rect x="{left_w}" width="{right_w}" height="{h}" fill="{color}"/>
    <rect width="{total_w}" height="{h}" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,sans-serif" font-size="11">
    <text x="{left_w / 2}" y="14">{left_text}</text>
    <text x="{left_w + right_w / 2}" y="14">{right_text}</text>
  </g>
</svg>'''


def build_embed_html(certificate_id, status_label, public_base_url):
    badge_url = f"{public_base_url}/api/badge/{certificate_id}.svg"
    return f'''<!doctype html>
<html><head><meta charset="utf-8"><title>Aqtify verification — {certificate_id}</title></head>
<body style="font-family:sans-serif;padding:24px;">
  <img src="{badge_url}" alt="Aqtify status: {status_label}">
  <p>Certificate <code>{certificate_id}</code> — status: <b>{status_label}</b></p>
  <p style="color:#726f68;font-size:12px;">Embed this badge anywhere with:</p>
  <pre style="background:#f0efec;padding:10px;border-radius:6px;">&lt;img src="{badge_url}"&gt;</pre>
</body></html>'''
