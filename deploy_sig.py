#!/usr/bin/env python3
"""Debug addContractFile signature — check its source via .toString()."""
import json, time
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
    src = eval_js(sock, '''
    (() => {
      const el = document.querySelector('#app, [data-v-app]');
      const store = el.__vue_app__.config.globalProperties.$pinia._s.get('contractsStore');
      return {
        add: store.addContractFile.toString().slice(0, 400),
        open: store.openFile.toString().slice(0, 300)
      };
    })()
    ''')
    print(json.dumps(src, indent=1))

if __name__ == '__main__':
    main()
