#!/usr/bin/env python3
"""Import Contract dialog opened by accident — close it. Then find the
blue Run button. Editor toolbar may show it only after clicking INTO the
editor area. Plan: close dialog, click editor code area, screenshot, find
blue circular button (bg-primary class)."""
import json, time, base64, sys
from cdp_driver import ws_connect, cdp, eval_js
import urllib.request

def get_sock():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read())
    page = [t for t in tabs if t['type'] == 'page'][0]
    sock = ws_connect('/devtools/page/' + page['id'])
    cdp(sock, 'Runtime.enable')
    return sock

def click_xy(sock, x, y):
    cdp(sock, 'Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': x, 'y': y})
    cdp(sock, 'Input.dispatchMouseEvent', {'type': 'mousePressed', 'x': x, 'y': y,
        'button': 'left', 'clickCount': 1})
    time.sleep(0.12)
    cdp(sock, 'Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': x, 'y': y,
        'button': 'left', 'clickCount': 1})

def main():
    sock = get_sock()

    # 1. close dialog via Cancel button
    r = eval_js(sock, '''
    (() => {
      const btns = document.querySelectorAll('[role=dialog] button, .modal button');
      for (const b of btns) {
        if ((b.innerText||'').trim() === 'Cancel') { b.click(); return 'cancelled'; }
      }
      // fallback: X button
      const x = document.querySelector('[role=dialog] .lucide-x, .modal .lucide-x');
      if (x) { x.closest('button').click(); return 'x-closed'; }
      return 'no dialog';
    })()
    ''')
    print('close dialog ::', r)
    time.sleep(2)

    # 2. click into editor area (code region)
    click_xy(sock, 700, 300)
    time.sleep(2)

    # 3. scan ALL buttons with class containing 'primary' or bg-blue / svg fill-primary
    blue = eval_js(sock, '''
    (() => {
      const els = document.querySelectorAll('button');
      const out = [];
      for (const e of els) {
        const cls = (e.className||'').toString();
        const r = e.getBoundingClientRect();
        if (r.width > 0 && (cls.includes('primary') || cls.includes('blue'))) {
          out.push({x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2),
                    w: Math.round(r.width), cls: cls.slice(0, 100),
                    text: (e.innerText||'').trim().slice(0, 20)});
        }
      }
      return out;
    })()
    ''')
    print('primary/blue buttons ::', json.dumps(blue, indent=1)[:1500])

    r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r.get('result', {}):
        open('/tmp/studio_nodialog.png', 'wb').write(base64.b64decode(r['result']['data']))
        print('shot :: /tmp/studio_nodialog.png')

if __name__ == '__main__':
    main()
