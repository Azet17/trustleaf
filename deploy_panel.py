#!/usr/bin/env python3
"""Click 'Run and Debug' panel header → panel opens → find Deploy button inside."""
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

    # click the Run and Debug panel
    click_xy(sock, 126, 71)
    time.sleep(3)

    # scan all buttons/labels inside the panel now
    items = eval_js(sock, '''
    (() => {
      const hits = [];
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      while (walker.nextNode()) {
        const t = walker.currentNode.textContent.trim();
        if (t && t.length < 50 && /deploy|constructor|run|interact|method/i.test(t)) {
          const el = walker.currentNode.parentElement;
          const r = el.getBoundingClientRect();
          if (r.width > 0) hits.push({text: t.slice(0, 40),
              x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)});
        }
      }
      return hits.slice(0, 15);
    })()
    ''')
    print('panel items ::', json.dumps(items, indent=1)[:2000])

    r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r.get('result', {}):
        open('/tmp/studio_runpanel_open.png', 'wb').write(base64.b64decode(r['result']['data']))
        print('shot :: /tmp/studio_runpanel_open.png')

if __name__ == '__main__':
    main()
