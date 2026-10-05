#!/usr/bin/env python3
"""currentContractId was '' — setCurrentContractId(c.id) worked? check again.
openedFiles = [id, null] — the id 'a988...' is trustleaf? Set BOTH currentContractId
AND fix openedFiles ordering via store.patch. Then editor should mount."""
import json, time, base64, sys
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

    r = eval_js(sock, '''
    (() => {
      const el = document.querySelector('#app, [data-v-app]');
      const store = el.__vue_app__.config.globalProperties.$pinia._s.get('contractsStore');
      const c = store.contracts.find(c => c.name === 'trustleaf.py');
      // openedFiles: [openedId, previousId?] — put trustleaf FIRST
      store.$patch({
        currentContractId: c.id,
        openedFiles: [c.id, ...store.openedFiles.filter(x => x && x !== c.id)]
      });
      return {cur: store.currentContractId, opened: JSON.stringify(store.openedFiles)};
    })()
    ''')
    print('patched ::', r)
    time.sleep(4)

    vis = eval_js(sock, '''
    (() => {
      const ed = document.querySelector('.monaco-editor');
      const bodyHas = document.body.innerText.includes('SupplierTrustScore');
      return {editor: !!ed, codeVisible: bodyHas,
              welcome: document.body.innerText.includes('Welcome to the GenLayer Studio')};
    })()
    ''')
    print('state ::', json.dumps(vis))

    r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r.get('result', {}):
        open('/tmp/studio_try4.png', 'wb').write(base64.b64decode(r['result']['data']))
        print('shot :: /tmp/studio_try4.png')

if __name__ == '__main__':
    main()
