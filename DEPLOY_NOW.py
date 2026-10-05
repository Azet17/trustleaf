#!/usr/bin/env python3
"""CLICK DEPLOY! Button at ~(146, 353). Then wait for consensus & read result."""
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

    click_xy(sock, 146, 353)
    print('>>> DEPLOY CLICKED — waiting for validator consensus (up to 60s)...')

    addr = None
    for i in range(12):
        time.sleep(5)
        state = eval_js(sock, '''
        (() => {
          const body = document.body.innerText;
          const m = body.match(/0x[a-fA-F0-9]{40}/);
          const el = document.querySelector('#app, [data-v-app]');
          const ts = el.__vue_app__.config.globalProperties.$pinia._s.get('transactionsStore');
          let txInfo = null;
          if (ts) {
            const txs = ts.$state.allTransactions || [];
            if (txs.length) txInfo = JSON.stringify(txs[txs.length-1]).slice(0, 400);
          }
          return {addr: m ? m[0] : null,
                  deployed: /Deployed|deployed successfully/i.test(body),
                  status: /PENDING|PROPOSING|COMMITTING|REVEALING|ACCEPTED|FINALIZED/.test(body) ?
                          (body.match(/PENDING|PROPOSING|COMMITTING|REVEALING|ACCEPTED|FINALIZED/) || [])[0] : null,
                  err: /failed|error/i.test((body.match(/Transactions[\\s\\S]{0,300}/) || [''])[0]),
                  txInfo};
        })()
        ''')
        print(f'[{(i+1)*5}s] ::', json.dumps(state))
        if state.get('addr') or state.get('err'):
            addr = state.get('addr')
            break

    print()
    print('=' * 50)
    print('CONTRACT ADDRESS ::', addr or 'check screenshot')
    print('=' * 50)

    r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r.get('result', {}):
        open('/tmp/studio_DEPLOYED.png', 'wb').write(base64.b64decode(r['result']['data']))
        print('shot :: /tmp/studio_DEPLOYED.png')

if __name__ == '__main__':
    main()
