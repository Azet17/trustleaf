#!/usr/bin/env python3
"""Icon buttons at y=61/62 near tabs (copy, upload, new-file + one at 356,55
w=48 could be RUN). Click the 48px-wide one at (356,55) — likely Deploy/Run.
Use real mouse click via Input.dispatchMouseEvent (trusted)."""
import json, time, base64
from cdp_driver import ws_connect, cdp, eval_js
import urllib.request

def get_sock():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read())
    page = [t for t in tabs if t['type'] == 'page'][0]
    sock = ws_connect('/devtools/page/' + page['id'])
    cdp(sock, 'Runtime.enable')
    return sock

def click_xy(sock, x, y):
    cdp(sock, 'Input.dispatchMouseEvent', {'type': 'mousePressed', 'x': x, 'y': y,
        'button': 'left', 'clickCount': 1})
    cdp(sock, 'Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': x, 'y': y,
        'button': 'left', 'clickCount': 1})

def main():
    sock = get_sock()

    # Screenshot BEFORE
    r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    before = base64.b64decode(r['result']['data']) if 'data' in r.get('result', {}) else b''

    # Click the wide button at (380, 79) center of (356,55,48)
    click_xy(sock, 380, 79)
    time.sleep(5)

    # Check logs for deployment activity
    logs = eval_js(sock, '''
    (() => {
      const el = document.querySelector('#app, [data-v-app]');
      const ts = el.__vue_app__.config.globalProperties.$pinia._s.get('transactionsStore');
      return ts ? JSON.stringify(ts.$state).slice(0, 600) : 'no tx store';
    })()
    ''')
    print('tx store ::', logs)

    # Screenshot AFTER
    r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r.get('result', {}):
        after = base64.b64decode(r['result']['data'])
        open('/tmp/studio_after_click.png', 'wb').write(after)
        print('changed ::', before != after)
        print('shot :: /tmp/studio_after_click.png')

if __name__ == '__main__':
    main()
