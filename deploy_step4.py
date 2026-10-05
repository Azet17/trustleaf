#!/usr/bin/env python3
"""Deploy: Studio editor lives on /contracts page itself (has editor=True).
Find the editor + Deploy button state there. Screenshot for evidence."""
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
    print('url ::', eval_js(sock, 'location.href'))

    # Editor ada di page ini. Cek monaco global & models:
    print('monaco global ::', eval_js(sock, 'typeof monaco'))
    print('monaco models ::', eval_js(sock, 'typeof monaco !== "undefined" ? monaco.editor.getModels().length : -1'))

    # Cari tombol dengan teks relevan:
    btns = eval_js(sock, '''
    (() => {
      const els = document.querySelectorAll('button, a');
      return Array.from(els).map(e => (e.innerText || '').trim())
        .filter(t => t.length > 1 && t.length < 40);
    })()
    ''')
    print('all buttons ::', json.dumps(btns))

    # Screenshot buat lihat layout
    r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r:
        open('/tmp/studio_layout.png', 'wb').write(json.loads(json.dumps({'x': r['data']}))['x'].encode() and __import__('base64').b64decode(r['data']))
        print('screenshot :: /tmp/studio_layout.png')
    else:
        print('screenshot err ::', str(r)[:200])

if __name__ == '__main__':
    main()
