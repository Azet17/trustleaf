#!/usr/bin/env python3
"""Blue play button top-right of editor area (visible in screenshot).
Click 1st rail icon (files) to go back to contracts panel, open trustleaf,
then locate the blue play button precisely and click it."""
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
    time.sleep(0.1)
    cdp(sock, 'Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': x, 'y': y,
        'button': 'left', 'clickCount': 1})

def main():
    sock = get_sock()

    # 1. back to files panel (icon 1: y=77)
    click_xy(sock, 24, 77)
    time.sleep(2)

    # 2. open trustleaf via store
    eval_js(sock, '''
    (() => {
      const el = document.querySelector('#app, [data-v-app]');
      const store = el.__vue_app__.config.globalProperties.$pinia._s.get('contractsStore');
      const c = store.contracts.find(c => c.name === 'trustleaf.py');
      if (c) store.$patch({currentContractId: c.id,
        openedFiles: [c.id, ...store.openedFiles.filter(x => x && x !== c.id)]});
      return c ? c.id : 'nf';
    })()
    ''')
    time.sleep(3)
    vis = eval_js(sock, 'document.body.innerText.includes("SupplierTrustScore")')
    print('code visible ::', vis)

    # 3. find the blue play button = button with svg, top-right area (x>1500, y<130)
    play = eval_js(sock, '''
    (() => {
      const els = document.querySelectorAll('button');
      const out = [];
      for (const e of els) {
        const r = e.getBoundingClientRect();
        if (r.width > 0 && r.y < 130 && r.x > 1400) {
          out.push({x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2),
                    w: Math.round(r.width), cls: (e.className||'').toString().slice(0, 80),
                    text: (e.innerText||'').trim().slice(0, 20)});
        }
      }
      return out;
    })()
    ''')
    print('top-right buttons ::', json.dumps(play, indent=1))

    # 4. click it (first one)
    if play:
        p = play[0]
        click_xy(sock, p['x'], p['y'])
        time.sleep(6)
        state = eval_js(sock, '''
        (() => {
          const el = document.querySelector('#app, [data-v-app]');
          const ts = el.__vue_app__.config.globalProperties.$pinia._s.get('transactionsStore');
          const dlg = document.querySelector('[role=dialog], .modal, [class*="modal"]');
          return {txs: ts ? ts.$state.allTransactions.length : 'n/a',
                  dialog: dlg ? (dlg.innerText||'').slice(0, 250) : null,
                  bodySnippet: document.body.innerText.slice(0, 300).replace(/\\n+/g, ' | ')};
        })()
        ''')
        print('after click ::', json.dumps(state, indent=1)[:1200])

    r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r.get('result', {}):
        open('/tmp/studio_play.png', 'wb').write(base64.b64decode(r['result']['data']))
        print('shot :: /tmp/studio_play.png')

if __name__ == '__main__':
    main()
