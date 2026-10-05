#!/usr/bin/env python3
"""trustleaf.py in list, save icon at (226,80). Click trustleaf.py first
(to open it), then save icon to persist. Then click blue Run button."""
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

    # 1. click trustleaf.py in sidebar
    item = eval_js(sock, '''
    (() => {
      const els = document.querySelectorAll('*');
      for (const e of els) {
        if (e.children.length === 0 && (e.innerText || '').trim() === 'trustleaf.py') {
          const r = e.getBoundingClientRect();
          return {x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)};
        }
      }
      return null;
    })()
    ''')
    print('item ::', item)
    click_xy(sock, item['x'], item['y'])
    time.sleep(4)
    print('code visible ::', eval_js(sock, 'document.body.innerText.includes("SupplierTrustScore")'))

    # 2. click SAVE icon (226, 80)
    click_xy(sock, 226, 80)
    time.sleep(3)
    # any dialog? handle save-as input if present
    inp = eval_js(sock, '''
    (() => {
      const d = document.querySelector('[role=dialog] input, .modal input, input[type=text]:not([placeholder*="Filter"])');
      return d ? {ph: d.placeholder, val: d.value} : null;
    })()
    ''')
    print('save dialog input ::', inp)
    if inp and 'name' in str(inp.get('ph', '')).lower():
        # type name + confirm
        cdp(sock, 'Input.insertText', {'text': 'trustleaf.py'})
        time.sleep(0.5)
        # Enter
        cdp(sock, 'Input.dispatchKeyEvent', {'type': 'rawKeyDown', 'key': 'Enter',
             'code': 'Enter', 'windowsVirtualKeyCode': 13})
        cdp(sock, 'Input.dispatchKeyEvent', {'type': 'keyUp', 'key': 'Enter',
             'code': 'Enter', 'windowsVirtualKeyCode': 13})
        time.sleep(3)

    # 3. id now?
    r = eval_js(sock, '''
    (() => {
      const el = document.querySelector('#app, [data-v-app]');
      const store = el.__vue_app__.config.globalProperties.$pinia._s.get('contractsStore');
      const c = store.contracts.find(c => c.name === 'trustleaf.py');
      return c ? 'id=' + c.id : 'gone';
    })()
    ''')
    print('after save ::', r)

    r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r.get('result', {}):
        open('/tmp/studio_saved.png', 'wb').write(base64.b64decode(r['result']['data']))
        print('shot :: /tmp/studio_saved.png')

if __name__ == '__main__':
    main()
