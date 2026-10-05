#!/usr/bin/env python3
"""Vue app with Pinia contractsStore. Inject contract via the store directly.
Try: window.__pinia or app instance; else use IndexedDB."""
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

    # Find Vue app instance → pinia stores
    probe = eval_js(sock, '''
    (() => {
      const el = document.querySelector('#app, [data-v-app], #__nuxt');
      if (!el) return 'no app el';
      const vueApp = el.__vue_app__;
      if (!vueApp) return 'no vue app';
      const pinia = vueApp.config.globalProperties.$pinia;
      if (!pinia) return 'no pinia';
      const stores = Object.keys(pinia.state.value);
      return {stores};
    })()
    ''')
    print('stores ::', probe)

    if 'contracts' in str(probe):
        # Inspect the contracts store shape
        shape = eval_js(sock, '''
        (() => {
          const el = document.querySelector('#app, [data-v-app], #__nuxt');
          const pinia = el.__vue_app__.config.globalProperties.$pinia;
          const cs = pinia.state.value.contractsStore;
          return {keys: Object.keys(cs), sample: JSON.stringify(cs).slice(0, 800)};
        })()
        ''')
        print('contractsStore ::', json.dumps(shape, indent=1)[:1500])

if __name__ == '__main__':
    main()
