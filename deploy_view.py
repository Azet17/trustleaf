#!/usr/bin/env python3
"""Welcome page overlays. Monaco editor exists in DOM but welcome covers it.
The welcome is a 'home' pane in same tab-group. Fix: close home tab (the
house icon tab has its own close?) or the welcome is shown because
currentContractId not set properly. Set it via store + also close home."""
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

    # Set current contract via store → may switch pane content
    r = eval_js(sock, '''
    (() => {
      const el = document.querySelector('#app, [data-v-app]');
      const store = el.__vue_app__.config.globalProperties.$pinia._s.get('contractsStore');
      const c = store.contracts.find(c => c.name === 'trustleaf.py');
      store.setCurrentContractId(c.id);
      // also check openedFiles
      return {cur: store.currentContractId,
              opened: JSON.stringify(store.openedFiles).slice(0, 200)};
    })()
    ''')
    print('store ::', r)
    time.sleep(2)

    # force click the TAB itself again (button element, not coordinates)
    r = eval_js(sock, '''
    (() => {
      const els = document.querySelectorAll('button');
      for (const e of els) {
        if ((e.innerText || '').trim() === 'trustleaf.py') { e.click(); return 'js-clicked'; }
      }
      return 'nf';
    })()
    ''')
    print('js click ::', r)
    time.sleep(4)

    vis = eval_js(sock, '''
    (() => {
      const ed = document.querySelector('.monaco-editor');
      if (!ed) return {ed: false};
      const r = ed.getBoundingClientRect();
      const welcome = document.body.innerText.includes('Welcome to the GenLayer Studio');
      return {ed: true, w: Math.round(r.width), h: Math.round(r.height),
              welcomeOverlay: welcome};
    })()
    ''')
    print('state ::', json.dumps(vis))

    r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r.get('result', {}):
        open('/tmp/studio_try3.png', 'wb').write(base64.b64decode(r['result']['data']))
        print('shot :: /tmp/studio_try3.png')

if __name__ == '__main__':
    main()
