#!/usr/bin/env python3
"""Check final deploy status — wait until ACCEPTED/FINALIZED."""
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
    for i in range(10):
        time.sleep(6)
        state = eval_js(sock, '''
        (() => {
          const el = document.querySelector('#app, [data-v-app]');
          const ts = el.__vue_app__.config.globalProperties.$pinia._s.get('transactionsStore');
          const txs = ts ? (ts.$state.allTransactions || []) : [];
          const last = txs.length ? txs[txs.length-1] : null;
          return last ? {status: last.statusName,
                         hash: (last.hash||'').slice(0, 20),
                         addr: last.contractAddress || '(pending)'} : {status: 'no tx'};
        })()
        ''')
        print(f'[{(i+1)*6}s] ::', json.dumps(state))
        if state.get('status') in ('ACCEPTED', 'FINALIZED', 'ERROR'):
            break

    r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r.get('result', {}):
        open('/tmp/studio_deploy_status.png', 'wb').write(base64.b64decode(r['result']['data']))
        print('shot :: /tmp/studio_deploy_status.png')

if __name__ == '__main__':
    main()
