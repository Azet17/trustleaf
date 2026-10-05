#!/usr/bin/env python3
"""Get full stderr — data.stderr field directly, larger slice."""
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
      let best = '';
      for (const name of Object.keys(pinia.state.value)) {
        const state = pinia.state.value[name];
        const scan = (obj, depth) => {
          if (depth > 4 || !obj) return;
          if (typeof obj === 'string') {
            if (obj.includes('storage_build') && obj.length > best.length) best = obj;
            return;
          }
          if (Array.isArray(obj)) { obj.forEach(x => scan(x, depth+1)); return; }
          if (typeof obj === 'object') { Object.values(obj).forEach(x => scan(x, depth+1)); }
        };
        scan(state, 0);
      }
      return best ? best.slice(-700) : 'nf';
    })()
    ''')
    print(r)

if __name__ == '__main__':
    main()
