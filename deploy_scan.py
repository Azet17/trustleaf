#!/usr/bin/env python3
"""Find ALL buttons with zero-size (hidden tooltips) + all visible buttons
in the whole page with their rects. Deploy btn may be outside viewport top
(screen 800x600 too small) — set 1600x1000 first, then scan whole page."""
import json, time, base64
from cdp_driver import ws_connect, cdp, eval_js
import urllib.request

def get_sock():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read())
    page = [t for t in tabs if t['type'] == 'page'][0]
    sock = ws_connect('/devtools/page/' + page['id'])
    cdp(sock, 'Runtime.enable')
    return sock

def main():
    sock = get_sock()

    # Scan ALL buttons incl. icon-only, with rect
    btns = eval_js(sock, '''
    (() => {
      const els = document.querySelectorAll('button, [role=button]');
      const out = [];
      for (const e of els) {
        const r = e.getBoundingClientRect();
        if (r.width === 0) continue;
        const svg = e.querySelector('svg');
        out.push({
          text: (e.innerText || '').trim().slice(0, 25),
          icon: !!svg,
          x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width),
          title: (e.getAttribute('title') || '').slice(0, 30)
        });
      }
      return out;
    })()
    ''')
    # tampilkan yang dekat top editor area (y < 120) atau teks menarik
    interesting = [b for b in btns if b['y'] < 140 or any(k in b['text'].lower() for k in ['deploy', 'run', 'save', 'compile'])]
    print('top-area / action buttons ::')
    print(json.dumps(interesting, indent=1))

if __name__ == '__main__':
    main()
