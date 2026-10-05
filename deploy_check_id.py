#!/usr/bin/env python3
"""Contract added but id undefined — addContractFile may need different
shape or the save action assigns id. Check the added entry & find save
icon (in panel header icons) to persist."""
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

    # inspect the trustleaf entry
    r = eval_js(sock, '''
    (() => {
      const el = document.querySelector('#app, [data-v-app]');
      const store = el.__vue_app__.config.globalProperties.$pinia._s.get('contractsStore');
      const c = store.contracts.find(c => c.name === 'trustleaf.py');
      return c ? JSON.stringify({id: c.id, name: c.name, len: (c.content||'').length,
                                  keys: Object.keys(c), example: c.example}) : 'gone';
    })()
    ''')
    print('entry ::', r)

    # Also: is trustleaf.py now visible in the sidebar list?
    vis = eval_js(sock, 'document.body.innerText.includes("trustleaf.py")')
    print('sidebar shows ::', vis)

if __name__ == '__main__':
    main()
