#!/usr/bin/env python3
"""Open trustleaf.py in editor, then find & click Deploy/Run button."""
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

    # Open trustleaf.py
    r = eval_js(sock, '''
    (() => {
      const el = document.querySelector('#app, [data-v-app]');
      const store = el.__vue_app__.config.globalProperties.$pinia._s.get('contractsStore');
      const c = store.contracts.find(c => c.name === 'trustleaf.py');
      if (!c) return 'nf';
      store.openFile(c);
      store.setCurrentContractId(c.id);
      return 'opened ' + c.id;
    })()
    ''')
    print('open ::', r)
    time.sleep(4)

    check = eval_js(sock, 'document.body.innerText.includes("SupplierTrustScore")')
    print('editor shows TrustLeaf ::', check)

    # Find deploy-related buttons now visible
    btns = eval_js(sock, '''
    (() => {
      const els = document.querySelectorAll('button');
      return Array.from(els).map(e => (e.innerText || '').trim())
        .filter(t => t && /deploy|run|interact/i.test(t) && t.length < 30);
    })()
    ''')
    print('deploy buttons ::', json.dumps(btns))

    r2 = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r2.get('result', {}):
        open('/tmp/studio_trustleaf.png', 'wb').write(base64.b64decode(r2['result']['data']))
        print('shot :: /tmp/studio_trustleaf.png')

if __name__ == '__main__':
    main()
