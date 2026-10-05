#!/usr/bin/env python3
"""The (356,55) button = HOME. Deploy button must appear INSIDE the editor
toolbar AFTER opening the file tab. Click the trustleaf.py TAB itself
(537,71), wait, then rescan the strip for new buttons that appear."""
import json, time, base64
from cdp_driver import ws_connect, cdp, eval_js
import urllib.request

def get_sock():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read())
    page = [t for t in tabs if t['type'] == 'page'][0]
    sock = ws_connect('/devtools/page/' + page['id'])
    cdp(sock, 'Runtime.enable')
    return sock

def click_xy(sock, x, y):
    cdp(sock, 'Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': x, 'y': y})
    cdp(sock, 'Input.dispatchMouseEvent', {'type': 'mousePressed', 'x': x, 'y': y,
        'button': 'left', 'clickCount': 1})
    time.sleep(0.1)
    cdp(sock, 'Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': x, 'y': y,
        'button': 'left', 'clickCount': 1})

def main():
    sock = get_sock()

    # Click trustleaf.py tab
    click_xy(sock, 590, 71)
    time.sleep(4)

    # verify editor visible
    vis = eval_js(sock, '!!document.querySelector(".monaco-editor") && document.body.innerText.includes("SupplierTrustScore")')
    print('editor visible ::', vis)

    # rescan full page for any button containing Deploy text/icon
    allb = eval_js(sock, '''
    (() => {
      const els = document.querySelectorAll('button, [role=button]');
      const out = [];
      for (const e of els) {
        const r = e.getBoundingClientRect();
        const t = (e.innerText || '').trim();
        const title = e.getAttribute('title') || e.getAttribute('aria-label') || '';
        if (r.width > 0 && (t || title)) {
          out.push({x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width),
                    text: t.slice(0, 25), title: title.slice(0, 25)});
        }
      }
      return out;
    })()
    ''')
    print('visible labeled buttons ::')
    print(json.dumps(allb, indent=0)[:2000])

    r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r.get('result', {}):
        open('/tmp/studio_tab_active.png', 'wb').write(base64.b64decode(r['result']['data']))
        print('shot :: /tmp/studio_tab_active.png')

if __name__ == '__main__':
    main()
