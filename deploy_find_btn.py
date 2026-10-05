#!/usr/bin/env python3
"""Editor open, no Deploy button visible. Check viewport height — the Run
button was visible in earlier storage.py screenshot (top-right corner).
May need to scroll up or the button only appears with wider viewport.
Try: set viewport bigger + look for svg play icons clickable."""
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

    # Set bigger viewport
    cdp(sock, 'Emulation.setDeviceMetricsOverride',
        {'width': 1600, 'height': 1000, 'deviceScaleFactor': 1, 'mobile': False})
    time.sleep(2)

    # Find ANY element with svg play icon or title/aria-label deploy/run
    found = eval_js(sock, '''
    (() => {
      const out = [];
      const els = document.querySelectorAll('button, [title], [aria-label]');
      for (const e of els) {
        const t = (e.getAttribute('title') || '') + '|' + (e.getAttribute('aria-label') || '') + '|' + (e.innerText || '').trim();
        if (/deploy|run|play/i.test(t) || e.querySelector('svg[class*="play"], svg[class*="deploy"]')) {
          const r = e.getBoundingClientRect();
          out.push({tag: e.tagName, label: t.slice(0, 50), x: Math.round(r.x), y: Math.round(r.y), vis: r.width > 0});
        }
      }
      return out.slice(0, 10);
    })()
    ''')
    print('deploy-like elements ::', json.dumps(found, indent=1))

    shot = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in shot.get('result', {}):
        open('/tmp/studio_wide.png', 'wb').write(base64.b64decode(shot['result']['data']))
        print('shot :: /tmp/studio_wide.png')

if __name__ == '__main__':
    main()
