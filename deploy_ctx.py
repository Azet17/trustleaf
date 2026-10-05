#!/usr/bin/env python3
"""No deploy button visible. In GenLayer Studio, deploy = right-click on
the contract file in explorer ('Deploy contract' context menu) OR an icon
in the file panel header. Try right-click on trustleaf.py in sidebar."""
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

    # find trustleaf.py item in sidebar, right-click it
    r = eval_js(sock, '''
    (() => {
      const els = document.querySelectorAll('*');
      for (const e of els) {
        if (e.children.length === 0 && (e.innerText || '').trim() === 'trustleaf.py') {
          const r = e.getBoundingClientRect();
          return {x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)};
        }
      }
      return null;
    })()
    ''')
    print('sidebar item ::', r)
    x, y = r['x'], r['y']

    cdp(sock, 'Input.dispatchMouseEvent', {'type': 'mouseMoved', 'x': x, 'y': y})
    cdp(sock, 'Input.dispatchMouseEvent', {'type': 'mousePressed', 'x': x, 'y': y,
        'button': 'right', 'clickCount': 1})
    cdp(sock, 'Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': x, 'y': y,
        'button': 'right', 'clickCount': 1})
    time.sleep(2)

    # context menu appeared?
    menu = eval_js(sock, '''
    (() => {
      const menus = document.querySelectorAll('[role=menu], .context-menu, [class*="dropdown"], [class*="popover"], [class*="menu"]');
      const out = [];
      for (const m of menus) {
        const r = m.getBoundingClientRect();
        if (r.width > 0 && r.height > 0) {
          out.push({cls: (m.className||'').toString().slice(0, 50),
                    items: (m.innerText || '').trim().slice(0, 200)});
        }
      }
      return out;
    })()
    ''')
    print('context menu ::', json.dumps(menu, indent=1)[:1500])

    r2 = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r2.get('result', {}):
        open('/tmp/studio_ctx.png', 'wb').write(base64.b64decode(r2['result']['data']))
        print('shot :: /tmp/studio_ctx.png')

if __name__ == '__main__':
    main()
