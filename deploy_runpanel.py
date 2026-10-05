#!/usr/bin/env python3
"""Per docs: 'Run and Debug button on the LEFT SIDEBAR' (the 2nd icon,
terminal/code icon at rail y=125) OR 'play icon top right of editor pane'.
Earlier rail scan clicked icons but tab wasn't active. Now code IS open.
Click rail icon 2 (24,125), then look for Run&Deploy panel + play icon."""
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
    time.sleep(0.12)
    cdp(sock, 'Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': x, 'y': y,
        'button': 'left', 'clickCount': 1})

def main():
    sock = get_sock()

    # click rail icon 2 (Run and Debug)
    click_xy(sock, 24, 125)
    time.sleep(3)

    # scan for Deploy/Run text now
    found = eval_js(sock, '''
    (() => {
      const hits = [];
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      while (walker.nextNode()) {
        const t = walker.currentNode.textContent.trim();
        if (/^(deploy|run|run and debug|interact)/i.test(t) && t.length < 40) {
          const el = walker.currentNode.parentElement;
          const r = el.getBoundingClientRect();
          hits.push({text: t, x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)});
        }
      }
      return hits.slice(0, 10);
    })()
    ''')
    print('run/deploy texts ::', json.dumps(found, indent=1))

    r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r.get('result', {}):
        open('/tmp/studio_runpanel.png', 'wb').write(base64.b64decode(r['result']['data']))
        print('shot :: /tmp/studio_runpanel.png')

if __name__ == '__main__':
    main()
