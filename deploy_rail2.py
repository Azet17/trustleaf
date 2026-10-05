#!/usr/bin/env python3
"""OOPS — Ctrl+Enter / F5 opened a Google Form (feedback survey navigated
away!). Navigate back to Studio, reopen trustleaf, and look at the sidebar
icons panel — per docs there's an icon rail on far-left with a 'Run & Deploy'
panel. Navigate and re-verify carefully. AVOID any navigation shortcuts."""
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
    cdp(sock, 'Input.dispatchMouseEvent', {'type': 'mousePressed', 'x': x, 'y': y,
        'button': 'left', 'clickCount': 1})
    time.sleep(0.1)
    cdp(sock, 'Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': x, 'y': y,
        'button': 'left', 'clickCount': 1})

def main():
    sock = get_sock()

    # back to studio
    cdp(sock, 'Page.navigate', {'url': 'https://studio.genlayer.com/contracts'})
    time.sleep(10)
    print('url ::', eval_js(sock, 'location.href'))

    # dismiss tutorial if reappears
    eval_js(sock, '''
    (() => {
      const els = document.querySelectorAll('button');
      for (const e of els) if ((e.innerText||'').trim() === 'Skip tutorial') { e.click(); return 1; }
      return 0;
    })()
    ''')
    time.sleep(1)

    # open trustleaf via store
    eval_js(sock, '''
    (() => {
      const el = document.querySelector('#app, [data-v-app]');
      const store = el.__vue_app__.config.globalProperties.$pinia._s.get('contractsStore');
      const c = store.contracts.find(c => c.name === 'trustleaf.py');
      if (c) {
        store.$patch({currentContractId: c.id,
          openedFiles: [c.id, ...store.openedFiles.filter(x => x && x !== c.id)]});
      }
      return c ? c.id : 'nf';
    })()
    ''')
    time.sleep(4)

    vis = eval_js(sock, 'document.body.innerText.includes("SupplierTrustScore")')
    print('code visible ::', vis)

    # THE ICON RAIL — click icon 2 (y=125) and icon 3 (y=173) one at a time,
    # screenshot each, looking for Deploy panel
    for i, y in enumerate([77, 125, 173]):
        click_xy(sock, 24, y)
        time.sleep(2)
        dep = eval_js(sock, '''
        (() => {
          const t = document.body.innerText;
          return {deploy: /deploy/i.test(t), ctor: /constructor/i.test(t),
                  run: /\bRun\b/.test(t)};
        })()
        ''')
        print(f'icon y={y} :: {json.dumps(dep)}')

    r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r.get('result', {}):
        open('/tmp/studio_rail.png', 'wb').write(base64.b64decode(r['result']['data']))
        print('shot :: /tmp/studio_rail.png')

if __name__ == '__main__':
    main()
