#!/usr/bin/env python3
"""Debug: 'Start coding' click did not navigate. Inspect if new tab/window
opened, or if a modal appeared. Also try direct URL routes."""
import json, time
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

    # What tabs exist now? Maybe Studio opened a NEW tab for the editor.
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read())
    print('tabs ::')
    for t in tabs:
        if t['type'] == 'page':
            print(' ', t['id'][:10], t['url'][:80])

    # Try known Studio editor routes directly
    for route in ['/contracts/new', '/ide', '/editor', '/contracts/ide']:
        cdp(sock, 'Page.enable')
        cdp(sock, 'Page.navigate', {'url': f'https://studio.genlayer.com{route}'})
        time.sleep(4)
        url = eval_js(sock, 'location.href')
        title = eval_js(sock, 'document.title')
        has_editor = eval_js(sock, '!!document.querySelector(".monaco-editor, [class*=editor]")')
        print(f'{route} :: url={url[:60]} editor={has_editor}')

if __name__ == '__main__':
    main()
