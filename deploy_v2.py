#!/usr/bin/env python3
"""Update contract content (TreeMap fix), reload schema, check Deploy btn."""
import json, time, base64, sys
from cdp_driver import ws_connect, cdp, eval_js
import urllib.request

CONTRACT = open('/home/ubuntu/trustleaf/contracts/supplier_trust.py').read()

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

    r = eval_js(sock, f'''
    (() => {{
      const el = document.querySelector('#app, [data-v-app]');
      const store = el.__vue_app__.config.globalProperties.$pinia._s.get('contractsStore');
      const c = store.contracts.find(c => c.name === 'trustleaf.py');
      c.content = {json.dumps(CONTRACT)};
      if (!c.id) {{ c.id = crypto.randomUUID(); }}
      store.$patch({{currentContractId: c.id}});
      return 'ok id=' + c.id;
    }})()
    ''')
    print('update ::', r)
    time.sleep(2)

    # click Run and Debug panel to refresh schema
    click_xy(sock, 126, 71)
    time.sleep(5)

    panel = eval_js(sock, '''
    (() => {
      const body = document.body.innerText;
      const deployBtn = (() => {
        const els = document.querySelectorAll('button');
        for (const e of els) {
          const r = e.getBoundingClientRect();
          if (r.width > 0 && (e.innerText||'').trim().toLowerCase() === 'deploy') {
            return {x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)};
          }
        }
        return null;
      })();
      return {schemaErr: body.includes('Could not load contract schema'),
              deployBtn};
    })()
    ''')
    print('panel ::', json.dumps(panel, indent=1))

    if panel.get('deployBtn'):
        p = panel['deployBtn']
        click_xy(sock, p['x'], p['y'])
        print('>>> DEPLOY CLICKED — waiting consensus...')
        time.sleep(20)
        state = eval_js(sock, '''
        (() => {
          const body = document.body.innerText;
          const m = body.match(/0x[a-fA-F0-9]{40}/);
          return {addr: m ? m[0] : null,
                  deployed: /deployed|Deployed/.test(body),
                  err: body.includes('Could not load')};
        })()
        ''')
        print('DEPLOY RESULT ::', json.dumps(state, indent=1))

    r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r.get('result', {}):
        open('/tmp/studio_final.png', 'wb').write(base64.b64decode(r['result']['data']))
        print('shot :: /tmp/studio_final.png')

if __name__ == '__main__':
    main()
