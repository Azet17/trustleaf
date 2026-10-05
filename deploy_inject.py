#!/usr/bin/env python3
"""FINAL: inject TrustLeaf contract via Vue Pinia contractsStore,
create the contract entry, open it in editor, then trigger deploy."""
import json, time, base64, uuid
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

    # 1. Look at full shape of an existing contract entry
    shape = eval_js(sock, '''
    (() => {
      const el = document.querySelector('#app, [data-v-app], #__nuxt');
      const pinia = el.__vue_app__.config.globalProperties.$pinia;
      const cs = pinia.state.value.contractsStore;
      const c = cs.contracts[0];
      return Object.keys(c);
    })()
    ''')
    print('contract keys ::', shape)

    # 2. Check for create/add action on the store instance itself
    actions = eval_js(sock, '''
    (() => {
      const el = document.querySelector('#app, [data-v-app], #__nuxt');
      const pinia = el.__vue_app__.config.globalProperties.$pinia;
      // get store instance (with actions)
      const store = pinia._s.get('contractsStore');
      if (!store) return 'no store instance';
      return Object.keys(store).filter(k => typeof store[k] === 'function');
    })()
    ''')
    print('store actions ::', json.dumps(actions))

if __name__ == '__main__':
    main()
