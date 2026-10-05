#!/usr/bin/env python3
"""Rail icons didn't reveal Deploy. Per docs the 'Run and Deploy' panel is a
TAB in the right side of the editor OR bottom. Take full screenshot and
look at right edge — maybe panel is collapsed. Also try keyboard shortcut
(F5? Ctrl+Enter?) commonly used for deploy in Studio."""
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
    cdp(sock, 'Input.dispatchMouseEvent', {'type': 'mousePressed', 'x': x, 'y': y,
        'button': 'left', 'clickCount': 1})
    time.sleep(0.1)
    cdp(sock, 'Input.dispatchMouseEvent', {'type': 'mouseReleased', 'x': x, 'y': y,
        'button': 'left', 'clickCount': 1})

def main():
    sock = get_sock()

    # Try Ctrl+Enter and F5 in editor (focus first)
    eval_js(sock, '''
    (() => { const ed = document.querySelector('.monaco-editor textarea'); if (ed) ed.focus(); return 1; })()
    ''')
    # Ctrl+Enter
    cdp(sock, 'Input.dispatchKeyEvent', {'type': 'rawKeyDown', 'key': 'Enter',
         'code': 'Enter', 'windowsVirtualKeyCode': 13, 'modifiers': 2})
    cdp(sock, 'Input.dispatchKeyEvent', {'type': 'keyUp', 'key': 'Enter',
         'code': 'Enter', 'windowsVirtualKeyCode': 13, 'modifiers': 2})
    time.sleep(3)

    dep = eval_js(sock, '''
    (() => {
      const hits = [];
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      while (walker.nextNode()) {
        const t = walker.currentNode.textContent.trim();
        if (/deploy|constructor inputs/i.test(t) && t.length < 50) hits.push(t);
      }
      const dlg = document.querySelector('[role=dialog], .modal');
      return {hits: hits.slice(0, 5), dialog: dlg ? dlg.innerText.slice(0, 150) : null};
    })()
    ''')
    print('after ctrl+enter ::', json.dumps(dep, indent=1))

    r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r.get('result', {}):
        open('/tmp/studio_deploy_try.png', 'wb').write(base64.b64decode(r['result']['data']))
        print('shot :: /tmp/studio_deploy_try.png')

if __name__ == '__main__':
    main()
