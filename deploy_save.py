#!/usr/bin/env python3
"""Entry exists but without id (addContractFile assigns id via async
persistence?). Click the SAVE icon in panel header to persist, then
re-check id. Save icon = one of the 3 header icons in Your Contracts."""
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

    # find header icons of "Your Contracts" panel (near its title)
    icons = eval_js(sock, '''
    (() => {
      const els = document.querySelectorAll('button');
      const out = [];
      for (const e of els) {
        const r = e.getBoundingClientRect();
        // header icons: y around 100-140, x between 70-400
        if (r.width > 0 && r.y > 90 && r.y < 150 && r.x > 60 && r.x < 420) {
          out.push({x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2),
                    title: e.getAttribute('title') || e.getAttribute('aria-label') || '',
                    svg: !!e.querySelector('svg')});
        }
      }
      return out;
    })()
    ''')
    print('panel header icons ::', json.dumps(icons))

    # click each icon; after each check if trustleaf gets an id
    for ic in icons:
        click_xy(sock, ic['x'], ic['y'])
        time.sleep(2)
        r = eval_js(sock, '''
        (() => {
          const el = document.querySelector('#app, [data-v-app]');
          const store = el.__vue_app__.config.globalProperties.$pinia._s.get('contractsStore');
          const c = store.contracts.find(c => c.name === 'trustleaf.py');
          return c && c.id ? 'ID=' + c.id : null;
        })()
        ''')
        print(f"icon ({ic['x']},{ic['y']}) :: {r}")
        if r and 'ID=' in str(r):
            print('PERSISTED!')
            break

    # dialog may have opened (save as prompt?) — check
    dlg = eval_js(sock, '''
    (() => {
      const d = document.querySelector('[role=dialog], .modal, input[placeholder]');
      return d ? (d.tagName + '|' + (d.placeholder || d.innerText || '').slice(0, 80)) : null;
    })()
    ''')
    print('dialog/input ::', dlg)

    r2 = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r2.get('result', {}):
        open('/tmp/studio_save.png', 'wb').write(base64.b64decode(r2['result']['data']))
        print('shot :: /tmp/studio_save.png')

if __name__ == '__main__':
    main()
