#!/usr/bin/env python3
"""No 'Run and Deploy' text found. The left sidebar has icon rail — the 2nd
icon (code/terminal) might be the Run&Deploy panel. Click left sidebar
icons one by one and check for Deploy button appearing."""
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

    # list left rail icons with positions
    icons = eval_js(sock, '''
    (() => {
      const els = document.querySelectorAll('button, a');
      const out = [];
      for (const e of els) {
        const r = e.getBoundingClientRect();
        if (r.x < 70 && r.width > 0 && r.height > 0) {
          out.push({x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2),
                    w: Math.round(r.width)});
        }
      }
      return out;
    })()
    ''')
    print('rail icons ::', json.dumps(icons))

    # click each icon after the file-explorer one, look for Deploy button
    for i, ic in enumerate(icons):
        x, y = ic['x'], ic['y']
        cdp(sock, 'Input.dispatchMouseEvent', {'type': 'mousePressed', 'x': x, 'y': y,
            'button': 'left', 'clickCount': 1})
        cdp(sock, 'Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': x, 'y': y,
            'button': 'left', 'clickCount': 1})
        time.sleep(1.5)
        dep = eval_js(sock, '''
        (() => {
          const hits = [];
          const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
          while (walker.nextNode()) {
            const t = walker.currentNode.textContent.trim();
            if (/deploy|constructor/i.test(t) && t.length < 50) hits.push(t);
          }
          return hits.length ? hits.slice(0, 3) : null;
        })()
        ''')
        if dep:
            print(f'icon[{i}] ({x},{y}) :: FOUND -> {dep}')

if __name__ == '__main__':
    main()
