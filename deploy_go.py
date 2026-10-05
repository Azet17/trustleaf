#!/usr/bin/env python3
"""FINAL DEPLOY: addContractFile(TrustLeaf) → openFile → click Deploy/Run."""
import json, time, base64
from cdp_driver import ws_connect, cdp, eval_js
import urllib.request

CONTRACT = open('/home/ubuntu/trustleaf/contracts/supplier_trust.py').read()

def get_sock():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read())
    page = [t for t in tabs if t['type'] == 'page'][0]
    sock = ws_connect('/devtools/page/' + page['id'])
    cdp(sock, 'Runtime.enable')
    return sock

def main():
    sock = get_sock()

    # 1. Add contract file via store action
    r = eval_js(sock, f'''
    (() => {{
      const el = document.querySelector('#app, [data-v-app]');
      const store = el.__vue_app__.config.globalProperties.$pinia._s.get('contractsStore');
      store.addContractFile('trustleaf.py', {json.dumps(CONTRACT)});
      return 'added; total=' + store.contracts.length;
    }})()
    ''')
    print('add ::', r)

    # 2. Open it in the editor
    r = eval_js(sock, '''
    (() => {
      const el = document.querySelector('#app, [data-v-app]');
      const store = el.__vue_app__.config.globalProperties.$pinia._s.get('contractsStore');
      const c = store.contracts.find(c => c.name === 'trustleaf.py');
      if (!c) return 'not found';
      store.openFile(c);
      store.setCurrentContractId(c.id);
      return 'opened: ' + c.id;
    })()
    ''')
    print('open ::', r)
    time.sleep(3)

    # 3. Verify editor shows TrustLeaf
    check = eval_js(sock, 'document.body.innerText.includes("SupplierTrustScore")')
    print('editor shows TrustLeaf ::', check)

    # 4. Screenshot evidence
    r2 = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r2.get('result', {}):
        open('/tmp/studio_trustleaf_loaded.png', 'wb').write(base64.b64decode(r2['result']['data']))
        print('shot :: /tmp/studio_trustleaf_loaded.png')

if __name__ == '__main__':
    main()
