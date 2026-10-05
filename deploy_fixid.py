#!/usr/bin/env python3
"""Panel says: 'select an intelligent contract in the Files list'.
trustleaf.py tab is open but store's currentContractId might not match
because the persisted entry lacks id. Check currentContractId & entry id,
fix mismatch, then re-open Run&Debug panel."""
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

    # full store state for trustleaf
    r = eval_js(sock, '''
    (() => {
      const el = document.querySelector('#app, [data-v-app]');
      const store = el.__vue_app__.config.globalProperties.$pinia._s.get('contractsStore');
      const c = store.contracts.find(c => c.name === 'trustleaf.py');
      return {cur: store.currentContractId,
              tl_id: c ? c.id : 'MISSING',
              opened: JSON.stringify(store.openedFiles),
              n: store.contracts.length};
    })()
    ''')
    print('store ::', json.dumps(r))

    # If tl has no id, assign one + set current
    r = eval_js(sock, '''
    (() => {
      const el = document.querySelector('#app, [data-v-app]');
      const store = el.__vue_app__.config.globalProperties.$pinia._s.get('contractsStore');
      let c = store.contracts.find(c => c.name === 'trustleaf.py');
      if (!c.id) c.id = crypto.randomUUID();
      store.$patch({currentContractId: c.id});
      return 'set cur=' + store.currentContractId;
    })()
    ''')
    print('fix ::', r)
    time.sleep(2)

    # click Run and Debug panel header again to refresh
    click_xy(sock, 126, 71)
    time.sleep(2)
    click_xy(sock, 126, 71)
    time.sleep(3)

    # now check panel content for Deploy
    items = eval_js(sock, '''
    (() => {
      const hits = [];
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      while (walker.nextNode()) {
        const t = walker.currentNode.textContent.trim();
        if (/deploy|constructor/i.test(t) && t.length < 60) {
          const el = walker.currentNode.parentElement;
          const r = el.getBoundingClientRect();
          if (r.width > 0) hits.push({text: t.slice(0, 40),
              x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)});
        }
      }
      return hits.slice(0, 8);
    })()
    ''')
    print('panel now ::', json.dumps(items, indent=1))

    r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r.get('result', {}):
        open('/tmp/studio_panel2.png', 'wb').write(base64.b64decode(r['result']['data']))
        print('shot :: /tmp/studio_panel2.png')

if __name__ == '__main__':
    main()
