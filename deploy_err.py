#!/usr/bin/env python3
"""Get full RPC error from logs — click the error log entry to expand, or
grab log data from the consensusStore/logs. Try store first."""
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

    # pinia stores — find logs/error store
    r = eval_js(sock, '''
    (() => {
      const el = document.querySelector('#app, [data-v-app]');
      const pinia = el.__vue_app__.config.globalProperties.$pinia;
      const out = {};
      for (const name of Object.keys(pinia.state.value)) {
        const s = JSON.stringify(pinia.state.value[name]);
        if (s.includes('getContractSchema') || s.includes('Traceback')) {
          // find exact entry
          const state = pinia.state.value[name];
          for (const k of Object.keys(state)) {
            const arr = state[k];
            if (Array.isArray(arr)) {
              for (const item of arr) {
                const s2 = JSON.stringify(item);
                if (s2.includes('Traceback')) {
                  out.hit = s2.slice(0, 1500);
                  break;
                }
              }
            }
          }
        }
      }
      return out.hit || 'not found in stores: ' + Object.keys(pinia.state.value).join(',');
    })()
    ''')
    print(r)

if __name__ == '__main__':
    main()
