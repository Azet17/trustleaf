#!/usr/bin/env python3
"""Docs: 'Run and Deploy' is a TAB (likely in the left sidebar icons or a
pane header). Look for text 'Run and Deploy' or similar tab in the page."""
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

    # search all text nodes for deploy-related labels
    found = eval_js(sock, '''
    (() => {
      const hits = [];
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      while (walker.nextNode()) {
        const t = walker.currentNode.textContent.trim();
        if (/run|deploy|interact/i.test(t) && t.length < 40) {
          const el = walker.currentNode.parentElement;
          const r = el.getBoundingClientRect();
          hits.push({text: t, tag: el.tagName, x: Math.round(r.x), y: Math.round(r.y),
                     vis: r.width > 0});
        }
      }
      return hits.slice(0, 20);
    })()
    ''')
    print('deploy text hits ::', json.dumps(found, indent=1)[:1800])

if __name__ == '__main__':
    main()
