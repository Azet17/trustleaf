#!/usr/bin/env python3
"""The button at (356,55) w=48 h=32 with svg 'fill-primary' IS the Run/Deploy
button (it's left of the tabs, styled with primary fill). Earlier click
navigated home probably because I clicked while tab wasn't active.
Now: trustleaf tab is active. Click it with trusted mouse event."""
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
    cdp(sock, 'Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': x, 'y': y})
    cdp(sock, 'Input.dispatchMouseEvent', {'type': 'mousePressed', 'x': x, 'y': y,
        'button': 'left', 'clickCount': 1})
    time.sleep(0.1)
    cdp(sock, 'Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': x, 'y': y,
        'button': 'left', 'clickCount': 1})

def main():
    sock = get_sock()

    # confirm trustleaf tab still active
    active = eval_js(sock, '''
    (() => {
      const els = document.querySelectorAll('button');
      for (const e of els) {
        if ((e.innerText || '').trim() === 'trustleaf.py') {
          const r = e.getBoundingClientRect();
          return {x: Math.round(r.x), y: Math.round(r.y), active: e.className.includes('primary') || true};
        }
      }
      return null;
    })()
    ''')
    print('trustleaf tab ::', active)

    # Click the deploy button (380, 71)
    click_xy(sock, 380, 71)
    time.sleep(8)

    # Check for deploy modal / tx
    state = eval_js(sock, '''
    (() => {
      const el = document.querySelector('#app, [data-v-app]');
      const ts = el.__vue_app__.config.globalProperties.$pinia._s.get('transactionsStore');
      const dlg = document.querySelector('[role=dialog], .modal');
      return {
        txs: ts ? ts.$state.allTransactions.length : -1,
        dialog: dlg ? (dlg.innerText || '').slice(0, 200) : null
      };
    })()
    ''')
    print('state ::', json.dumps(state, indent=1))

    r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r.get('result', {}):
        open('/tmp/studio_deploy_click.png', 'wb').write(base64.b64decode(r['result']['data']))
        print('shot :: /tmp/studio_deploy_click.png')

if __name__ == '__main__':
    main()
