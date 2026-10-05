#!/usr/bin/env python3
"""Panel ready: 'Not deployed yet' + Constructor Inputs. Find & click the
Deploy button in this panel."""
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

    # find Deploy button
    dep = eval_js(sock, '''
    (() => {
      const els = document.querySelectorAll('button');
      for (const e of els) {
        if ((e.innerText || '').trim().toLowerCase() === 'deploy') {
          const r = e.getBoundingClientRect();
          return {x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)};
        }
      }
      return null;
    })()
    ''')
    print('deploy button ::', dep)
    if not dep:
        sys.exit(1)

    click_xy(sock, dep['x'], dep['y'])
    print('clicked DEPLOY — waiting for consensus...')
    time.sleep(15)

    # check result
    state = eval_js(sock, '''
    (() => {
      const el = document.querySelector('#app, [data-v-app]');
      const ts = el.__vue_app__.config.globalProperties.$pinia._s.get('transactionsStore');
      const body = document.body.innerText;
      const addrMatch = body.match(/0x[a-fA-F0-9]{40}/);
      return {txs: ts ? ts.$state.allTransactions.length : 'n/a',
              contractAddr: addrMatch ? addrMatch[0] : null,
              deployed: body.includes('deployed'),
              error: /error|failed/i.test(body.slice(-500))};
    })()
    ''')
    print('result ::', json.dumps(state, indent=1))

    r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r.get('result', {}):
        open('/tmp/studio_deployed.png', 'wb').write(base64.b64decode(r['result']['data']))
        print('shot :: /tmp/studio_deployed.png')

if __name__ == '__main__':
    main()
