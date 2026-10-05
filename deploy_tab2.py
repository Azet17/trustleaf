#!/usr/bin/env python3
"""Trustleaf tab inactive — home tab active. The home tab overlaps at same y.
Click trustleaf.py tab precisely at its center (604, 71) — earlier click at
(590,71) may have hit home tab. Get exact rect of trustleaf tab button then
click its center precisely."""
import json, time, base64, sys
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
    time.sleep(0.15)
    cdp(sock, 'Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': x, 'y': y,
        'button': 'left', 'clickCount': 1})

def main():
    sock = get_sock()

    # exact rect of trustleaf tab
    rect = eval_js(sock, '''
    (() => {
      const els = document.querySelectorAll('button');
      for (const e of els) {
        if ((e.innerText || '').trim() === 'trustleaf.py') {
          const r = e.getBoundingClientRect();
          return {cx: Math.round(r.x + r.width/2), cy: Math.round(r.y + r.height/2),
                  full: r.width + 'x' + r.height};
        }
      }
      return null;
    })()
    ''')
    print('tab rect ::', rect)
    if not rect:
        sys.exit(1)

    # click exactly center
    click_xy(sock, rect['cx'], rect['cy'])
    time.sleep(5)

    vis = eval_js(sock, '!!document.querySelector(".monaco-editor")')
    has_code = eval_js(sock, 'document.body.innerText.includes("SupplierTrustScore")')
    print(f'editor visible :: {vis} | code present :: {has_code}')

    # find deploy button in editor toolbar now
    btns = eval_js(sock, '''
    (() => {
      const ed = document.querySelector('.monaco-editor');
      if (!ed) return 'no editor';
      // scan buttons in the editor's parent toolbar area
      const pane = ed.closest('[class*="editor"], [class*="pane"], [class*="container"]') || ed.parentElement;
      const els = document.querySelectorAll('button');
      const out = [];
      for (const e of els) {
        const r = e.getBoundingClientRect();
        if (r.width > 0 && r.y < 140 && r.x > 640) {
          out.push({x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width),
                    text: (e.innerText||'').trim().slice(0,20),
                    svg: !!e.querySelector('svg')});
        }
      }
      return out;
    })()
    ''')
    print('editor-top buttons ::', json.dumps(btns, indent=0)[:1200])

    r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r.get('result', {}):
        open('/tmp/studio_editor_on.png', 'wb').write(base64.b64decode(r['result']['data']))
        print('shot :: /tmp/studio_editor_on.png')

if __name__ == '__main__':
    main()
