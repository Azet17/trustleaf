#!/usr/bin/env python3
"""After re-navigation the openedFiles reset (trustleaf tab gone).
storage.py tab is active and blue play button at (990, 69) EXISTS.
Plan: open trustleaf via store, click storage.py tab OFF? No — click
trustleaf in sidebar list, then the play button deploys CURRENT contract.
Actually simpler: the play button probably deploys the ACTIVE tab contract.
1. Open trustleaf (store patch + click sidebar item)
2. Verify tab visible
3. Click play (990,69)"""
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

    # 1. click trustleaf.py in sidebar list (find exact)
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
    print('sidebar trustleaf ::', item)
    if not item:
        print('trustleaf not in list!'); sys.exit(1)
    click_xy(sock, item['x'], item['y'])
    time.sleep(4)

    vis = eval_js(sock, 'document.body.innerText.includes("SupplierTrustScore")')
    tabs_now = eval_js(sock, '''
    (() => {
      const els = document.querySelectorAll('button');
      return Array.from(els).map(e => (e.innerText||'').trim())
        .filter(t => t.endsWith('.py'));
    })()
    ''')
    print(f'code visible :: {vis} | tabs :: {tabs_now}')

    # 2. locate blue play button NOW (may have moved)
    play = eval_js(sock, '''
    (() => {
      const els = document.querySelectorAll('button');
      for (const e of els) {
        const r = e.getBoundingClientRect();
        if (r.width > 0 && r.y < 130 && r.x > 900) {
          return {x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2),
                  cls: (e.className||'').toString().slice(0, 100)};
        }
      }
      return null;
    })()
    ''')
    print('play button ::', play)

    if not play:
        print('NO PLAY BUTTON'); sys.exit(1)

    # 3. CLICK PLAY → deploy trustleaf
    click_xy(sock, play['x'], play['y'])
    time.sleep(8)

    state = eval_js(sock, '''
    (() => {
      const el = document.querySelector('#app, [data-v-app]');
      const ts = el.__vue_app__.config.globalProperties.$pinia._s.get('transactionsStore');
      const dlg = document.querySelector('[role=dialog], .modal, [class*="modal"], [class*="dialog"]');
      return {txs: ts ? JSON.stringify(ts.$state).slice(0, 400) : 'n/a',
              dialog: dlg ? (dlg.innerText||'').slice(0, 300) : null};
    })()
    ''')
    print('after play ::', json.dumps(state, indent=1)[:1500])

    r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r.get('result', {}):
        open('/tmp/studio_fired.png', 'wb').write(base64.b64decode(r['result']['data']))
        print('shot :: /tmp/studio_fired.png')

if __name__ == '__main__':
    main()
