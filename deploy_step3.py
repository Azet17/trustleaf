#!/usr/bin/env python3
"""Deploy step 3: 'Start coding' opens Monaco editor with a template contract.
Replace editor content with TrustLeaf code via Monaco API, then find Deploy."""
import json, time
from cdp_driver import ws_connect, cdp, eval_js
import urllib.request

CONTRACT = open('/home/ubuntu/trustleaf/contracts/supplier_trust.py').read()

def get_sock():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read())
    page = [t for t in tabs if t['type'] == 'page'][0]
    sock = ws_connect('/devtools/page/' + page['id'])
    cdp(sock, 'Runtime.enable')
    return sock

def click_text(sock, text, contains=False):
    expr = f'''
    (() => {{
      const els = document.querySelectorAll('button, a, [role=button]');
      for (const e of els) {{
        const t = (e.innerText || '').trim();
        const hit = {json.dumps(contains)} ? t.includes({json.dumps(text)}) : t === {json.dumps(text)};
        if (hit) {{ e.click(); return 'clicked: ' + t.slice(0, 50); }}
      }}
      return 'NOT FOUND: ' + {json.dumps(text)};
    }})()
    '''
    return eval_js(sock, expr)

def main():
    sock = get_sock()
    print('start coding ::', click_text(sock, 'Start coding'))
    time.sleep(5)
    print('url ::', eval_js(sock, 'location.href'))

    # Is Monaco available?
    has_monaco = eval_js(sock, 'typeof monaco !== "undefined"')
    print('monaco ::', has_monaco)

    if has_monaco:
        # Replace full editor content
        expr = f'''
        (() => {{
          const models = monaco.editor.getModels();
          if (!models.length) return 'no models';
          const model = models[0];
          const full = model.getFullModelRange();
          model.pushEditOperations([], [{{ range: full, text: {json.dumps(CONTRACT)} }}], () => null);
          return 'replaced: ' + model.getValue().slice(0, 60);
        }})()
        '''
        print('editor ::', eval_js(sock, expr))

    # Look for deploy button
    time.sleep(2)
    btns = eval_js(sock, '''
    (() => {
      const els = document.querySelectorAll('button');
      return Array.from(els).map(e => (e.innerText || '').trim())
        .filter(t => t && /deploy|run|interact|save/i.test(t));
    })()
    ''')
    print('deploy-ish buttons ::', json.dumps(btns))

if __name__ == '__main__':
    main()
