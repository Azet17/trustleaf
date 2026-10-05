#!/usr/bin/env python3
"""Get the RAW action signatures (wrapped by pinia). Dig into pinia._s store
object's own property or check errors from calling with various arg shapes."""
import json, time
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

    # call addContractFile with object + capture any error
    r = eval_js(sock, f'''
    (() => {{
      const el = document.querySelector('#app, [data-v-app]');
      const store = el.__vue_app__.config.globalProperties.$pinia._s.get('contractsStore');
      try {{
        // try object arg first
        const before = store.contracts.length;
        store.addContractFile({{ name: 'trustleaf.py', content: {json.dumps(CONTRACT)} }});
        const after = store.contracts.length;
        return 'obj-arg: ' + before + '->' + after + '; last=' + JSON.stringify(store.contracts[store.contracts.length-1]).slice(0,100);
      }} catch(e) {{ return 'ERR obj: ' + e.message; }}
    }})()
    ''')
    print('try obj ::', r)

    if 'ERR' in str(r):
        r = eval_js(sock, f'''
        (() => {{
          const el = document.querySelector('#app, [data-v-app]');
          const store = el.__vue_app__.config.globalProperties.$pinia._s.get('contractsStore');
          try {{
            const before = store.contracts.length;
            store.addContractFile('trustleaf.py', {json.dumps(CONTRACT)}, false);
            return '3-arg: ' + before + '->' + store.contracts.length;
          }} catch(e) {{ return 'ERR 3arg: ' + e.message; }}
        }})()
        ''')
        print('try 3arg ::', r)

if __name__ == '__main__':
    main()
