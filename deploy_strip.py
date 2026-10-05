#!/usr/bin/env python3
"""The click navigated to home. Open trustleaf.py tab again, THEN look at
the tab area. In first screenshot of storage.py, blue Run button was at
editor top-right. Deploy in Studio = 'Deploy' button that appears when a
contract tab is active. Reopen tab and scan its immediate container."""
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

    # open trustleaf.py again
    eval_js(sock, '''
    (() => {
      const els = document.querySelectorAll('div, span, button, li, a');
      for (const e of els) {
        if ((e.innerText || '').trim() === 'trustleaf.py') { e.click(); return 1; }
      }
      return 0;
    })()
    ''')
    time.sleep(4)

    # Now scan EVERYTHING in the top editor strip: get all buttons+svg with
    # y between tabs (~55) and editor content (~120), across full width
    strip = eval_js(sock, '''
    (() => {
      const els = document.querySelectorAll('button, svg, [role=button]');
      const out = [];
      for (const e of els) {
        const r = e.getBoundingClientRect();
        if (r.y > 40 && r.y < 130 && r.width > 0 && r.x > 350) {
          out.push({
            tag: e.tagName, x: Math.round(r.x), y: Math.round(r.y),
            w: Math.round(r.width), h: Math.round(r.height),
            cls: (typeof e.className === 'string' ? e.className : e.className.baseVal || '').slice(0, 70),
            text: (e.innerText || '').trim().slice(0, 20)
          });
        }
      }
      return out;
    })()
    ''')
    print('editor strip elements ::')
    print(json.dumps(strip, indent=1)[:2500])

if __name__ == '__main__':
    main()
