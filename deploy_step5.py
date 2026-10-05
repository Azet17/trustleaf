#!/usr/bin/env python3
"""Click 'Start coding' then inspect what changes — maybe it opens a modal
to choose a template. Get proper screenshot + full modal inspection."""
import json, time, base64
from cdp_driver import ws_connect, cdp, eval_js
import urllib.request

def get_sock():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read())
    page = [t for t in tabs if t['type'] == 'page'][0]
    sock = ws_connect('/devtools/page/' + page['id'])
    cdp(sock, 'Runtime.enable')
    return sock

def shot(sock, path):
    r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r.get('result', {}):
        open(path, 'wb').write(base64.b64decode(r['result']['data']))
        print('shot ::', path)

def main():
    sock = get_sock()

    # Click "Start coding" and IMMEDIATELY check for modal
    expr = '''
    (() => {
      const els = document.querySelectorAll('button, a');
      for (const e of els) {
        if ((e.innerText || '').trim() === 'Start coding') { e.click(); return 'clicked'; }
      }
      return 'nf';
    })()
    '''
    print('click ::', eval_js(sock, expr))
    time.sleep(3)

    # Modal / dialog appeared?
    modal = eval_js(sock, '''
    (() => {
      const dlg = document.querySelector('[role=dialog], .modal, [class*="Modal"]');
      if (!dlg) return null;
      const inputs = dlg.querySelectorAll('input');
      const buttons = Array.from(dlg.querySelectorAll('button')).map(b => (b.innerText||'').trim()).filter(Boolean);
      return {title: (dlg.querySelector('h1,h2,h3') || {}).innerText || '', inputs: inputs.length, buttons};
    })()
    ''')
    print('modal ::', json.dumps(modal, indent=1))

    shot(sock, '/tmp/studio_modal.png')

if __name__ == '__main__':
    main()
