#!/usr/bin/env python3
"""The traceback ends at _storage_build_struct — storage generator fails on
class-level type annotations. dict[str, str] class annotations may not be
supported; need gl.^ storage types or different annotation style.
Check docs quickly then rewrite contract using supported storage types."""
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
    # find the exact stderr and get the LAST lines (the exception line)
    r = eval_js(sock, '''
    (() => {
      const el = document.querySelector('#app, [data-v-app]');
      const pinia = el.__vue_app__.config.globalProperties.$pinia;
      let best = '';
      const scan = (obj, depth) => {
        if (depth > 4 || !obj) return;
        if (typeof obj === 'string') {
          if (obj.includes('_storage_build_struct') && obj.includes('Error') || 
              (obj.includes('stderr') && obj.includes('storage'))) {
            if (obj.length > best.length) best = obj;
          }
          return;
        }
        if (Array.isArray(obj)) { obj.forEach(x => scan(x, depth+1)); return; }
        if (typeof obj === 'object') { Object.values(obj).forEach(x => scan(x, depth+1)); }
      };
      scan(pinia.state.value, 0);
      // extract stderr field
      try {
        const parsed = JSON.parse(best);
        return (parsed.data ? parsed.data.stderr : best).slice(-600);
      } catch(e) { return best.slice(-600); }
    })()
    ''')
    print(r)

if __name__ == '__main__':
    main()
