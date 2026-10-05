#!/usr/bin/env python3
"""Click trustleaf.py in the contracts list → editor opens → click Run/Deploy."""
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

    # Click trustleaf.py in the contracts sidebar (find clickable el containing text)
    r = eval_js(sock, '''
    (() => {
      const els = document.querySelectorAll('div, span, button, li, a');
      for (const e of els) {
        if ((e.innerText || '').trim() === 'trustleaf.py') {
          e.click();
          return 'clicked trustleaf.py';
        }
      }
      return 'nf';
    })()
    ''')
    print('click file ::', r)
    time.sleep(4)

    # Editor shows TrustLeaf now?
    check = eval_js(sock, 'document.body.innerText.includes("SupplierTrustScore")')
    print('editor TrustLeaf ::', check)

    # Find Deploy/Run button
    btns = eval_js(sock, '''
    (() => {
      const els = document.querySelectorAll('button');
      return Array.from(els).map(e => (e.innerText || '').trim())
        .filter(t => t && /deploy|run/i.test(t));
    })()
    ''')
    print('buttons ::', json.dumps(btns))

    r2 = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r2.get('result', {}):
        open('/tmp/studio_opened.png', 'wb').write(base64.b64decode(r2['result']['data']))
        print('shot :: /tmp/studio_opened.png')

if __name__ == '__main__':
    main()
