#!/usr/bin/env python3
"""Alternative deploy path: GenLayer Studio has an API? No — use the
'Open Contract' import flow, or check if Studio supports URL param like
?code= or drag-drop. Inspect page's vue/nuxt router + localStorage keys."""
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

    # 1. What JS framework + router?
    info = eval_js(sock, '''
    (() => {
      const out = {};
      out.nuxt = !!window.__NUXT__;
      out.vue = !!(window.__VUE__ || document.querySelector('#__nuxt, [data-v-app]'));
      out.next = !!window.__NEXT_DATA__;
      out.localStorageKeys = Object.keys(localStorage).slice(0, 20);
      out.sessionKeys = Object.keys(sessionStorage).slice(0, 10);
      // find contracts in localStorage (studio may store them there)
      const found = {};
      for (const k of Object.keys(localStorage)) {
        const v = localStorage.getItem(k);
        if (v && v.includes('storage.py')) found[k] = v.slice(0, 100);
      }
      out.contractsIn = found;
      return out;
    })()
    ''')
    print(json.dumps(info, indent=1)[:2000])

if __name__ == '__main__':
    main()
