#!/usr/bin/env python3
"""Deploy TrustLeaf contract in GenLayer Studio over CDP.
Flow: skip tutorial → create new project → paste contract code → deploy."""
import json, time, sys
from cdp_driver import ws_connect, cdp, eval_js
import urllib.request

def get_sock():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read())
    page = [t for t in tabs if t['type'] == 'page'][0]
    sock = ws_connect('/devtools/page/' + page['id'])
    cdp(sock, 'Runtime.enable')
    return sock

def click_text(sock, text):
    """Click a button/element whose innerText matches."""
    expr = f'''
    (() => {{
      const els = document.querySelectorAll('button, a');
      for (const e of els) {{
        if ((e.innerText || '').trim().startsWith({json.dumps(text)})) {{
          e.click(); return 'clicked: ' + e.innerText.trim().slice(0, 40);
        }}
      }}
      return 'NOT FOUND: ' + {json.dumps(text)};
    }})()
    '''
    return eval_js(sock, expr)

def main():
    sock = get_sock()

    # 1. skip tutorial if present
    r = click_text(sock, 'Skip tutorial')
    print('tutorial ::', r)
    time.sleep(1)

    # 2. check current state — are we in the contracts list?
    state = eval_js(sock, 'location.href + " | " + document.title')
    print('state ::', state)

    # 3. find "New project" / create button
    buttons = eval_js(sock, '''
    (() => {
      const els = document.querySelectorAll('button, a');
      return Array.from(els).map(e => (e.innerText || '').trim().slice(0, 40))
                             .filter(t => t.length > 1);
    })()
    ''')
    print('available buttons ::', json.dumps(buttons, indent=0)[:1200])

if __name__ == '__main__':
    main()
