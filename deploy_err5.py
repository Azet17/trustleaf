#!/usr/bin/env python3
"""Still schema error — get the NEW traceback (may be different now)."""
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
      let newest = null, newestTs = 0;
      const scan = (obj, depth) => {
        if (depth > 5 || !obj) return;
        if (typeof obj === 'object') {
          if (obj.stderr && typeof obj.stderr === 'string' && obj.stderr.includes('Traceback')) {
            const ts = Number(obj.ts || obj.timestamp || 0);
            if (ts >= newestTs) { newestTs = ts; newest = obj.stderr; }
          }
          Object.values(obj).forEach(x => scan(x, depth+1));
        } else if (Array.isArray(obj)) {
          obj.forEach(x => scan(x, depth+1));
        }
      };
      scan(pinia.state.value, 0);
      return newest ? newest.slice(-800) : 'no stderr found';
    })()
    ''')
    print(r)

if __name__ == '__main__':
    main()
