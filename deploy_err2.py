#!/usr/bin/env python3
"""Get the REST of the traceback (it was cut at 1500 chars)."""
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
    r = eval_js(sock, '''
    (() => {
      const el = document.querySelector('#app, [data-v-app]');
      const pinia = el.__vue_app__.config.globalProperties.$pinia;
      for (const name of Object.keys(pinia.state.value)) {
        const state = pinia.state.value[name];
        for (const k of Object.keys(state)) {
          const arr = state[k];
          if (Array.isArray(arr)) {
            for (const item of arr) {
              const s2 = JSON.stringify(item);
              if (s2.includes('_storage_build_struct')) {
                const data = item.data || {};
                const stderr = data.stderr || '';
                // tail of stderr = actual error
                return stderr.slice(-900);
              }
            }
          }
        }
      }
      return 'nf';
    })()
    ''')
    print(r)

if __name__ == '__main__':
    main()
