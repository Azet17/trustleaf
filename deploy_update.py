#!/usr/bin/env python3
"""Update the in-Studio trustleaf.py content with the FIXED contract code,
then reload schema. New code: helper method removed (genlayer schema
inference chokes on nested gl.* calls outside decorated methods)."""
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

    # update contract content in store
    r = eval_js(sock, f'''
    (() => {{
      const el = document.querySelector('#app, [data-v-app]');
      const store = el.__vue_app__.config.globalProperties.$pinia._s.get('contractsStore');
      const c = store.contracts.find(c => c.name === 'trustleaf.py');
      if (!c) return 'MISSING';
      c.content = {json.dumps(CONTRACT)};
      if (!c.id) c.id = crypto.randomUUID();
      store.$patch({{currentContractId: c.id}});
      return 'updated id=' + c.id + ' len=' + c.content.length;
    }})()
    ''')
    print('update ::', r)
    time.sleep(2)

    # open trustleaf tab (click in sidebar)
    item = eval_js(sock, '''
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
    if item:
        click_xy(sock, item['x'], item['y'])
        time.sleep(3)

    # open Run and Debug panel
    click_xy(sock, 126, 71)
    time.sleep(4)

    # check schema now loads (error gone?) + Deploy button appears
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
              notDeployed: body.includes('Not deployed yet'),
              deployBtn};
    })()
    ''')
    print('panel ::', json.dumps(panel, indent=1))

    r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r.get('result', {}):
        open('/tmp/studio_schema2.png', 'wb').write(base64.b64decode(r['result']['data']))
        print('shot :: /tmp/studio_schema2.png')

if __name__ == '__main__':
    main()
