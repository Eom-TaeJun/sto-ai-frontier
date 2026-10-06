#!/usr/bin/env python3
"""Rebuild the original report with the environment research integrated by topic.

Uses only Python's standard library. The default base is the immutable first
edition in Git; --base accepts a saved copy for offline generation. No source
report, Git ref, or publication destination is modified by this script.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess

BASE_COMMIT = "7d4c0ec16d24e903b5e68d1cb1d52e0e545ac24c"
REPORT_PATH = "reports/digital-finance-agentic-securities.html"
SOURCE_PATH = "reports/financial-environment-response.html"
SOURCE_DATE = "2026-10-05"
CASE_PATH = "reports/source/kyobo_spc_case.json"
VOID = set("area base br col embed hr img input link meta param source track wbr".split())


class Element:
    def __init__(self, tag, attrs, start, inner_start, parent=None):
        self.tag, self.attrs = tag, dict(attrs)
        self.start, self.inner_start = start, inner_start
        self.inner_end = self.end = inner_start
        self.parent, self.children = parent, []


class Document(HTMLParser):
    """Track original source spans, avoiding reserialization of either report."""
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.source, self.lines = source, [0]
        self.lines.extend(i + 1 for i, char in enumerate(source) if char == "\n")
        self.root = Element("root", [], 0, 0)
        self.root.end = self.root.inner_end = len(source)
        self.stack, self.nodes = [self.root], []
        self.feed(source)

    def position(self):
        line, col = self.getpos()
        return self.lines[line - 1] + col

    def handle_starttag(self, tag, attrs):
        start = self.position()
        node = Element(tag, attrs, start, start + len(self.get_starttag_text()), self.stack[-1])
        self.stack[-1].children.append(node)
        self.nodes.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.stack.pop()

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                node = self.stack[index]
                node.inner_end = self.position()
                node.end = self.source.find(">", node.inner_end) + 1
                del self.stack[index:]
                return

    def by_id(self, value):
        matches = [node for node in self.nodes if node.attrs.get("id") == value]
        if len(matches) != 1:
            raise ValueError(f"Expected one source element #{value}; found {len(matches)}")
        return matches[0]

    def raw(self, node):
        return self.source[node.start:node.end]

    def inner(self, node):
        return self.source[node.inner_start:node.inner_end]


class Text(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.parts = []
        self.feed(source)

    def handle_data(self, text):
        self.parts.append(text)


def plain(source):
    return " ".join("".join(Text(source).parts).split())


CSS = r"""
/* Integrated widgets: the original page shell and prose styles remain intact. */
#report [hidden]{display:none!important}
#report .enrich{margin:26px 0 30px;min-width:0}
#report .enrich h3{margin:1.8em 0 .8em}
#report .enrich h4{font-size:16px;line-height:1.65;margin:1.5em 0 .65em;letter-spacing:-.015em}
#report .enrich h5{font-size:14px;margin:1.25em 0 .6em;line-height:1.65}
#report .enrich .evidence-label{font-size:inherit;padding:0;background:none;border:0;color:inherit}
#report .enrich .muted,#report .enrich .field-label,#report .enrich .diagram-note{color:var(--sub)}
#report .enrich .field-label{display:block;font-size:11px;font-weight:700;margin-bottom:7px}
#report .enrich .table-scroll{overflow:auto;margin:22px 0 24px;border:1px solid var(--rule);border-radius:4px}
#report .enrich .table-scroll table{min-width:680px}
#report .enrich .table-scroll th,#report .enrich .table-scroll td{padding:12px;overflow-wrap:anywhere}
#report .enrich .table-scroll th:first-child,#report .enrich .table-scroll td:first-child{width:22%}
#report .tabs-widget{border:1px solid var(--rule);border-radius:6px;margin:22px 0;background:white;overflow:hidden}
#report .tab-list{display:flex;flex-wrap:wrap;gap:6px;padding:13px;background:var(--wash);border-bottom:1px solid var(--rule)}
#report .tab-list button,#report .filter-controls button,#report .appendix-controls button,.report-control{font:inherit;font-size:12px;border:1px solid #bdc9d0;border-radius:4px;background:white;color:var(--ink);padding:7px 11px;cursor:pointer}
#report .tab-list button[aria-selected=true],#report .filter-controls button[aria-pressed=true]{background:var(--accent);border-color:var(--accent);color:white}
#report .tab-panel{padding:22px 24px}
#report .tab-panel h4{margin-top:0}
#report .asset-grid{display:grid;grid-template-columns:1fr 1fr;gap:25px}
#report .asset-grid p{font-size:13px;margin:8px 0 12px;line-height:1.8}
#report .asset-grid .asset-right{font-size:18px;font-weight:700;color:var(--accent)}
#report .filter-controls{display:flex;align-items:center;flex-wrap:wrap;gap:7px;margin:22px 0 16px}
#report .filter-controls span{font-size:12px;color:var(--sub);margin-left:auto}
#report .institution-grid{display:grid;grid-template-columns:1fr 1fr;gap:15px}
#report .institution-card{border:1px solid var(--rule);border-top:3px solid var(--accent);border-radius:4px;padding:22px 20px;background:white;min-width:0}
#report .institution-card .institution-index,#report .institution-card>span{font-size:11px;color:var(--sub)}
#report .institution-card h4{font-size:19px;margin:5px 0 15px}
#report .institution-card dl{margin:0}
#report .institution-card dl>div{padding:12px 0;border-top:1px solid var(--rule)}
#report .institution-card dt{font-size:11px;font-weight:700;color:var(--sub);margin:0 0 4px}
#report .institution-card dd{font-size:13px;line-height:1.85;margin:0}
#report .agent-flow{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:9px;margin:24px 0 12px}
#report .agent-flow .flow-step{background:var(--wash);border-top:2px solid var(--accent);padding:17px 12px;min-width:0}
#report .agent-flow .flow-step>span{display:block;font-size:11px;color:var(--sub);margin-bottom:8px}
#report .agent-flow .flow-step>strong{display:block;font-size:13px;line-height:1.7}
#report .agent-flow .flow-step small{display:block;font-size:11px;color:var(--sub);margin-top:7px}
#report .enrich .diagram-note{font-size:12px;line-height:1.8}
#report .macro-map{display:grid;grid-template-columns:1fr 1.4fr;gap:20px;border:1px solid var(--rule);background:var(--wash);padding:24px;margin:24px 0}
#report .macro-origin>span{display:block;font-size:11px;color:var(--sub);margin-bottom:10px}
#report .macro-origin strong{display:block;font-size:18px;line-height:1.65}
#report .macro-branches{display:grid;grid-template-columns:1fr 1fr;gap:10px}
#report .macro-branches>div{background:white;border-left:2px solid var(--accent);padding:14px}
#report .macro-branches strong{display:block;font-size:13px}
#report .macro-branches span{display:block;font-size:11px;color:var(--sub);margin-top:5px}
#report .macro-map>p{grid-column:1/-1;font-size:12px;margin:0;color:var(--sub)}
#report .scenarios .tab-panel>p{font-size:14px;color:var(--sub)}
#report .scenarios .tab-panel h5{color:var(--accent)}
#report .source-reports{display:grid;grid-template-columns:1fr 1fr;gap:13px;margin:22px 0}
#report .source-reports a{display:block;padding:18px;background:var(--wash);border:1px solid var(--rule);text-decoration:none}
#report .source-reports span,#report .source-reports small{display:block;font-size:11px;color:var(--sub)}
#report .source-reports strong{display:block;font-size:15px;line-height:1.65;margin:8px 0}
#report .appendix-controls{display:flex;flex-wrap:wrap;gap:8px;margin:22px 0 12px}
#report .evidence-group,#report .source-directory{border:1px solid var(--rule);border-radius:5px;margin:12px 0;background:white}
#report .evidence-group>summary,#report .source-directory>summary{cursor:pointer;padding:18px 20px;font-size:15px;font-weight:700;line-height:1.7;background:var(--wash)}
#report .evidence-group>summary>span{display:inline-block;color:var(--accent);font-size:11px;margin-right:12px}
#report .evidence-body{padding:12px 22px 22px;font-size:13px;line-height:1.9}
#report .evidence-body h5{font-size:16px;margin-top:27px}
#report .evidence-body a{overflow-wrap:anywhere}
#report .source-directory>p{font-size:12px;padding:10px 20px 0}
#report .source-directory ol{padding:0 23px 16px 43px;font-size:11px;line-height:1.8}
#report .source-directory li{padding:10px 0;border-bottom:1px solid var(--rule);overflow-wrap:anywhere}
#report .source-directory li strong,#report .source-directory li a{display:block}
.search-bar{border:1px solid var(--rule);padding:20px 22px;background:var(--wash);margin:0 0 27px;border-radius:5px}
.search-bar label{display:block;font-size:12px;font-weight:700;margin-bottom:8px}
.search-input-row{display:flex;gap:6px;flex-wrap:wrap}
.search-input-row input{min-width:120px;flex:1;font:inherit;font-size:13px;padding:8px 10px;border:1px solid #bdc9d0;border-radius:4px;background:white}
.search-input-row button{font:inherit;font-size:12px;padding:7px 10px;border:1px solid #bdc9d0;border-radius:4px;background:white;cursor:pointer}
.search-input-row button:disabled{opacity:.5;cursor:default}
#search-status{font-size:11px;color:var(--sub);margin:8px 0 0}
#search-results{max-height:300px;overflow:auto;margin-top:12px}
#search-results button{display:block;width:100%;font:inherit;font-size:12px;line-height:1.7;text-align:left;padding:10px;border:0;border-bottom:1px solid var(--rule);background:white;cursor:pointer}
#search-results button[aria-current=true]{background:#e0ecf1}
#report .search-hit{background:#f5eabc!important;box-shadow:0 0 0 4px #f5eabc}
.toc a.active{color:var(--accent);font-weight:700}
.toc a.toc-sub{font-size:11px;padding-left:10px}
button:focus-visible,input:focus-visible,summary:focus-visible,[tabindex]:focus-visible{outline:3px solid #2c8fbc;outline-offset:3px}
.revision-record{margin-top:12px}
@media(max-width:900px){#report .agent-flow{grid-template-columns:1fr 1fr}.toc a.toc-sub{padding-left:0}}
@media(max-width:560px){#report .asset-grid,#report .institution-grid,#report .source-reports,#report .macro-map{grid-template-columns:1fr}#report .macro-branches{grid-template-columns:1fr 1fr}#report .tab-panel{padding:18px}#report .institution-card{padding:18px}#report .agent-flow{grid-template-columns:1fr}#report .agent-flow .flow-step{padding:12px 15px}#report .agent-flow .flow-step>span{margin-bottom:4px}#report .enrich .table-scroll table{min-width:650px}#report .evidence-body{padding:10px 16px 20px}.search-bar{padding:16px}.search-input-row input{flex-basis:100%}.search-input-row button{flex:1}#report .filter-controls span{width:100%;margin-left:0}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
@media print{.search-bar,.report-control,#report .tab-list,#report .filter-controls,#report .appendix-controls{display:none!important}#report .tab-panel[hidden],#report .institution-card[hidden]{display:block!important}#report .enrich{margin:5mm 0}#report .enrich h3{font-size:12pt;break-after:avoid}#report .enrich h4{font-size:11pt;break-after:avoid}#report .enrich h5{font-size:10pt;break-after:avoid}#report .enrich .table-scroll{overflow:visible;border:0;margin:4mm 0}#report .enrich .table-scroll table{min-width:0;font-size:8pt;table-layout:fixed}#report .enrich .table-scroll th,#report .enrich .table-scroll td{padding:2mm;font-size:8pt;overflow-wrap:anywhere}#report .tab-panel{padding:4mm;border:1px solid var(--rule);margin:3mm 0;break-inside:avoid}#report .asset-grid{grid-template-columns:1fr 1fr;gap:4mm}#report .asset-grid p{font-size:8.5pt}#report .asset-grid .asset-right{font-size:11pt}#report .institution-grid{grid-template-columns:1fr 1fr;gap:4mm}#report .institution-card{padding:4mm;break-inside:avoid}#report .institution-card h4{font-size:11pt}#report .institution-card dd{font-size:8.5pt}#report .agent-flow{grid-template-columns:repeat(5,1fr);gap:2mm;break-inside:avoid}#report .agent-flow .flow-step{padding:3mm}#report .agent-flow .flow-step>strong{font-size:8pt}#report .agent-flow .flow-step small,#report .agent-flow .flow-step>span{font-size:7pt}#report .macro-map{padding:4mm;break-inside:avoid}#report .macro-origin strong{font-size:11pt}#report .macro-branches strong{font-size:9pt}#report .macro-branches span{font-size:8pt}#report .source-reports{break-inside:avoid}#report .evidence-group,#report .source-directory{border:0;margin:5mm 0}#report .evidence-group>summary,#report .source-directory>summary{padding:4mm 0;font-size:12pt;break-after:avoid;background:none}#report .evidence-body{padding:0;font-size:8.5pt}#report .evidence-body p{font-size:8.5pt;line-height:1.8}#report .source-directory ol{padding-left:6mm;font-size:7.5pt}#report .source-directory li{break-inside:avoid;font-size:7.5pt}#report .search-hit{background:transparent!important;box-shadow:none}#report a[data-source-number]::after{content:" [" attr(data-source-number) "]";font-size:6.5pt}}
"""

CONTROLS = """
<div class="search-bar" role="search" aria-label="보고서 검색">
<label for="report-search">보고서 안에서 찾기</label><div class="search-input-row">
<input id="report-search" type="search" placeholder="예: USDC, 국채, 한국은행, 수탁" autocomplete="off">
<button type="button" id="search-prev" aria-label="이전 검색 결과">이전</button><button type="button" id="search-next" aria-label="다음 검색 결과">다음</button><button type="button" id="search-clear">지우기</button></div>
<p id="search-status" role="status">두 글자 이상 입력하면 본문과 상세 근거를 함께 찾습니다.</p><div id="search-results" hidden></div></div>
<noscript><p class="note">자산·환경 비교는 모두 표시됩니다. 근거는 제목을 눌러 펼칠 수 있으며 브라우저의 찾기를 사용할 수 있습니다.</p><style>#report .tab-panel[hidden],#report .institution-card[hidden]{display:block!important}#report .tab-list,#report .filter-controls,.search-bar,.report-control,#report .appendix-controls{display:none!important}</style></noscript>
"""

JAVASCRIPT = r"""
<script>(()=>{
  'use strict';
  const report=document.getElementById('report');
  if(!report)return;
  const savedDocument='<!doctype html>\n'+document.documentElement.outerHTML;
  const tabs=[...report.querySelectorAll('[data-tabs]')];
  function activateTab(widget,index,focus=false){
    if(!widget)return;
    const buttons=[...widget.querySelectorAll('[role=tab]')];
    const panels=[...widget.querySelectorAll('[role=tabpanel]')];
    if(index<0||index>=buttons.length||panels.length!==buttons.length)return;
    buttons.forEach((button,i)=>{button.setAttribute('aria-selected',String(i===index));button.tabIndex=i===index?0:-1;panels[i].hidden=i!==index;});
    if(focus)buttons[index].focus();
  }
  tabs.forEach(widget=>{
    const buttons=[...widget.querySelectorAll('[role=tab]')];
    buttons.forEach((button,index)=>{
      button.addEventListener('click',()=>activateTab(widget,index));
      button.addEventListener('keydown',event=>{
        let next=index;
        if(event.key==='ArrowRight')next=(index+1)%buttons.length;
        else if(event.key==='ArrowLeft')next=(index+buttons.length-1)%buttons.length;
        else if(event.key==='Home')next=0;
        else if(event.key==='End')next=buttons.length-1;
        else return;
        event.preventDefault();activateTab(widget,next,true);
      });
    });
  });
  const cards=[...report.querySelectorAll('[data-institution]')];
  const filters=[...report.querySelectorAll('[data-filter]')];
  const count=document.getElementById('env-institution-count');
  function filterCards(key){
    filters.forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.filter===key)));
    cards.forEach(card=>card.hidden=key!=='all'&&card.dataset.institution!==key);
    if(count)count.textContent=cards.filter(card=>!card.hidden).length+'개 유형';
  }
  filters.forEach(button=>button.addEventListener('click',()=>filterCards(button.dataset.filter)));
  filterCards('all');
  const evidence=[...report.querySelectorAll('.evidence-group')];
  document.getElementById('env-expand-evidence')?.addEventListener('click',()=>evidence.forEach(detail=>detail.open=true));
  document.getElementById('env-collapse-evidence')?.addEventListener('click',()=>evidence.forEach(detail=>detail.open=false));
  const search=document.getElementById('report-search');
  const status=document.getElementById('search-status');
  const results=document.getElementById('search-results');
  const previous=document.getElementById('search-prev');
  const next=document.getElementById('search-next');
  const searchNodes=[...report.querySelectorAll('p,li,td,th,h2,h3,h4,h5,dd,dt,details>summary')].filter(node=>!node.closest('.search-bar,noscript'));
  let matches=[],selected=-1,timer;
  function clearHighlight(){report.querySelectorAll('.search-hit').forEach(node=>node.classList.remove('search-hit'));}
  function revealNode(node){
    if(!node)return;
    let parent=node;
    while(parent&&parent!==report){
      if(parent.tagName==='DETAILS')parent.open=true;
      if(parent.classList.contains('institution-card'))filterCards('all');
      if(parent.getAttribute('role')==='tabpanel'){
        const widget=parent.closest('[data-tabs]');
        if(widget)activateTab(widget,[...widget.querySelectorAll('[role=tabpanel]')].indexOf(parent));
      }
      parent=parent.parentElement;
    }
  }
  function chooseMatch(index){
    if(!matches.length)return;
    selected=(index+matches.length)%matches.length;
    const node=matches[selected];revealNode(node);clearHighlight();node.classList.add('search-hit');
    node.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'center'});
    const scroller=node.closest('.table-scroll,.table-wrap');
    if(scroller)scroller.scrollLeft=Math.max(0,node.offsetLeft-scroller.offsetLeft-25);
    if(status)status.textContent=matches.length+'곳에서 찾았습니다 · '+(selected+1)+'번째';
    results?.querySelectorAll('button').forEach((button,i)=>button.setAttribute('aria-current',String(i===selected)));
  }
  function runSearch(){
    if(!search||!status||!results||!previous||!next)return;
    const query=search.value.trim().toLocaleLowerCase();
    clearHighlight();results.replaceChildren();selected=-1;
    if(query.length<2){matches=[];results.hidden=true;status.textContent='두 글자 이상 입력하면 본문과 상세 근거를 함께 찾습니다.';previous.disabled=next.disabled=true;return;}
    matches=searchNodes.filter(node=>node.textContent.toLocaleLowerCase().includes(query));
    status.textContent=matches.length?matches.length+'곳에서 찾았습니다. 결과를 선택하거나 다음을 누르세요.':'일치하는 내용이 없습니다.';
    results.hidden=!matches.length;previous.disabled=next.disabled=!matches.length;
    matches.slice(0,40).forEach((node,index)=>{
      const button=document.createElement('button');button.type='button';
      let section=node;
      while(section.parentElement&&section.parentElement!==report)section=section.parentElement;
      const title=section.querySelector('h2')?.textContent||'본문과 자료';
      const text=node.textContent.replace(/\s+/g,' ').trim();const at=text.toLocaleLowerCase().indexOf(query);
      const from=Math.max(0,at-22);const snippet=(from?'…':'')+text.slice(from,from+140)+(text.length>from+140?'…':'');
      button.textContent=(index+1)+'. '+title+' · '+snippet;
      button.addEventListener('click',()=>chooseMatch(index));results.appendChild(button);
    });
    if(matches.length>40){const note=document.createElement('p');note.textContent='목록은 처음 40곳을 표시합니다. 이전·다음으로 전체 결과를 이동할 수 있습니다.';results.appendChild(note);}
  }
  if(previous)previous.disabled=true;if(next)next.disabled=true;
  search?.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(runSearch,150);});
  search?.addEventListener('keydown',event=>{if(event.key==='Enter'){event.preventDefault();clearTimeout(timer);runSearch();chooseMatch(0);}if(event.key==='Escape'){search.value='';runSearch();}});
  previous?.addEventListener('click',()=>chooseMatch(selected<0?matches.length-1:selected-1));
  next?.addEventListener('click',()=>chooseMatch(selected+1));
  document.getElementById('search-clear')?.addEventListener('click',()=>{if(search){search.value='';runSearch();search.focus();}});
  function revealHash(hash){
    let id;try{id=decodeURIComponent(hash.replace(/^#/,''));}catch{return;}
    const target=document.getElementById(id);if(!target)return;revealNode(target);
  }
  document.querySelectorAll('a[href^="#"]').forEach(link=>link.addEventListener('click',()=>revealHash(link.hash)));
  window.addEventListener('hashchange',()=>revealHash(location.hash));
  if(location.hash)revealHash(location.hash);
  const tocLinks=[...document.querySelectorAll('.toc a')];
  let queued=false;
  function updateReading(){
    let current=tocLinks[0];
    for(const link of tocLinks){const target=document.getElementById(link.hash.slice(1));if(target&&target.getBoundingClientRect().top<=100)current=link;}
    tocLinks.forEach(link=>{const active=link===current;link.classList.toggle('active',active);if(active)link.setAttribute('aria-current','location');else link.removeAttribute('aria-current');});
    queued=false;
  }
  window.addEventListener('scroll',()=>{if(!queued){queued=true;requestAnimationFrame(updateReading);}},{passive:true});
  window.addEventListener('resize',updateReading);updateReading();
  const printDetails=[...report.querySelectorAll('.evidence-group,.source-directory')];
  const panels=[...report.querySelectorAll('[role=tabpanel]')];
  let printState=null;
  function preparePrint(){
    if(printState)return;
    printState={details:printDetails.map(detail=>detail.open),panels:panels.map(panel=>panel.hidden),cards:cards.map(card=>card.hidden)};
    printDetails.forEach(detail=>detail.open=true);panels.forEach(panel=>panel.hidden=false);cards.forEach(card=>card.hidden=false);
  }
  function restorePrint(){
    if(!printState)return;
    printDetails.forEach((detail,i)=>detail.open=printState.details[i]);panels.forEach((panel,i)=>panel.hidden=printState.panels[i]);cards.forEach((card,i)=>card.hidden=printState.cards[i]);printState=null;
  }
  window.addEventListener('beforeprint',preparePrint);window.addEventListener('afterprint',restorePrint);
  document.getElementById('save-report')?.addEventListener('click',()=>{
    const blob=new Blob([savedDocument],{type:'text/html;charset=utf-8'});const url=URL.createObjectURL(blob);
    const link=document.createElement('a');link.href=url;link.download='digital-finance-agentic-securities.html';document.body.appendChild(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),10000);
  });
})();</script>
"""


def external_links(document):
    result = {}
    for node in document.nodes:
        url = node.attrs.get("href", "")
        if url.startswith(("https://", "http://")):
            result.setdefault(url, plain(document.inner(node)) or url)
    return result


def source_directory(urls):
    rows = []
    for number, (url, label) in enumerate(urls.items(), 1):
        rows.append(f'<li><strong>{number}. {escape(label)}</strong><a target="_blank" rel="noopener noreferrer" href="{escape(url, quote=True)}">{escape(url)}</a></li>')
    return '<details class="source-directory" id="integrated-source-directory"><summary>원문 주소 목록</summary><p>환경·기관 연구의 출처 번호 순서를 유지하고 기존 증권업 보고서의 추가 원문을 뒤에 함께 담았습니다. 원래 보고서의 위첨자 주석은 위 주석 1~14에서 확인할 수 있습니다.</p><ol>' + "\n".join(rows) + "</ol></details>"


def build(base, environment):
    base_doc, env_doc = Document(base), Document(environment)
    sections = {i: env_doc.by_id(f"section-{i}") for i in range(1, 12)}
    expected_counts = {1:7, 2:8, 3:19, 4:10, 5:24, 6:6, 7:14, 8:7, 9:7, 10:7, 11:12}
    for number, count in expected_counts.items():
        if len(sections[number].children) != count:
            raise ValueError(f"Source section {number} structure changed; review topic mapping")
    id_map = {node.attrs["id"]:"env-"+node.attrs["id"] for node in env_doc.nodes if "id" in node.attrs}
    id_map["section-8"] = "macro"
    used, dropped, mapping = set(), [], []
    old_imported_roles = "BNY와 Securitize가 각각 transfer agent/tokenization provider"
    new_imported_roles = 'BSTBL의 이전대리는 BNY, BRSRV의 이전대리는 Securitize. 상품별 계약 역할은 <a href="#env-source-B5">상세 근거 B5</a> 참조'
    if environment.count(old_imported_roles) != 1:
        raise ValueError("Imported B3 role cell changed; review source correction")

    def transform(fragment):
        def attribute(match):
            name, quote, value = match.group(1), match.group(2), match.group(3)
            if name == "href" and value.startswith("#"):
                value = "#" + id_map.get(value[1:], value[1:])
            elif name in ("id", "for", "aria-controls", "aria-labelledby", "aria-describedby"):
                value = " ".join(id_map.get(part, part) for part in value.split())
            elif name == "class":
                value = " ".join("agent-flow" if part == "flow" else part for part in value.split())
            return name + "=" + quote + value + quote
        fragment = re.sub(r'\b(id|href|for|aria-controls|aria-labelledby|aria-describedby|class)=("|\')(.*?)\2', attribute, fragment)
        fragment = fragment.replace(old_imported_roles, new_imported_roles)
        # The imported main heading becomes a subsection title; its descendants
        # sit one level lower, without a second independent chapter numbering.
        return re.sub(r'<(/?)h([234])\b', lambda m:"<"+m.group(1)+"h"+str(int(m.group(2))+1), fragment)

    def group(number, indices, title, anchor=None):
        indices = list(indices)
        used.update((number,index) for index in indices)
        heading_id = f"env-heading-{number}" if anchor is None or anchor == id_map[f"section-{number}"] else anchor+"-heading"
        anchor = anchor or id_map[f"section-{number}"]
        content = "\n".join(transform(env_doc.raw(sections[number].children[index])) for index in indices)
        mapping.append({"source_section":number,"source_child_indices":indices,"destination_anchor":anchor,"title":title})
        return f'<div class="enrich" id="{anchor}"><h3 id="{heading_id}">{escape(title)}</h3>\n{content}\n</div>'

    additions = {key:[] for key in ("change","actors","policy","agents","kyobo","outlook","sources")}
    additions["change"] += [
        group(1, range(4,7), "경제 원리로 비교하는 비용·권리·책임"),
        group(2, range(1,5), "자산별 권리와 실제 현금화 조건"),
    ]
    additions["actors"] += [
        group(3, [2,3,4,6,7,8,9], "지급·운용·사모자산에서 확인한 실제 사례"),
        group(6, range(1,6), "금융주체별 수익모델과 대응"),
        group(7, range(6,10), "은행과 플랫폼의 계약과 협상력", "env-bank-platform"),
    ]
    # International regulation precedes local institutional detail. Macro is a
    # subsection in the original policy chapter, retaining its seven chapters.
    policy_global = group(4, [1,3,4,5,6,7,8,9], "세계 제도 비교와 국제 업무의 경계")
    policy_korea = group(7, [1,2,3,4,5,10,11,12,13], "한국의 공공 인프라와 미국 정책 대응의 비교")
    additions["policy"] += [
        group(2, range(5,8), "여덟 가지 인프라가 함께 바뀐다", "env-infrastructure"),
        group(3, range(10,19), "시장 결제·지급망·DeFi의 운영 조건", "env-market-infrastructure"),
        group(8, range(1,7), "자금 이동이 거시경제로 전파되는 경로", "macro"),
    ]
    additions["agents"] += [group(5, [index for index in range(1,23) if index != 4], "에이전트의 실행·수탁·회복 설계")]
    additions["kyobo"] += [group(10, [1,2,3], "고객 업무를 연결하는 실행 순서와 판단 기준")]
    additions["outlook"] += [
        group(9, range(1,7), "환경별 전략과 새로운 수익·알파의 구분"),
        group(10, range(4,7), "발표를 경제적 변화로 확인하는 순서", "env-observation"),
    ]
    # Environment source numbers follow first occurrence order. Preserve that
    # order, then append the original report's additional URLs.
    urls = external_links(env_doc)
    for url, label in external_links(base_doc).items():
        urls.setdefault(url, label)
    additions["sources"] += [group(11, range(1,11), "자료의 범위와 상세 근거")]
    additions["sources"].append('<div class="enrich">'+source_directory(urls)+"</div>")

    reasons = {
        (1,1):"General digitization introduction already covered in original change chapter",
        (1,2):"Central outlook already connected in original summary and agents chapters",
        (1,3):"Institution incentives already discussed in original actors chapter",
        (3,1):"Independent report introduction replaced by integrated source scope",
        (3,5):"JPM Coin/MONY distinction already preserved in original actors paragraph; URLs retained in directory and evidence",
        (4,2):"CLARITY procedural defeat restored as a focused paragraph beside original ref8; repeated OCC example-limit discussion omitted; source URLs retained",
        (5,4):"Repeated Korean enterprise data-purchase premise; original premise and subsequent execution details retained",
        (5,23):"Independent report's next-chapter transition no longer matches integrated chapter order",
        (11,11):"Original source directory replaced by complete original-plus-environment URL union",
    }
    for number, section in sections.items():
        for index,node in enumerate(section.children):
            if index == 0 or (number,index) in used:
                continue
            reason = reasons.get((number,index))
            if not reason:
                raise ValueError(f"Unaccounted content omission {number}:{index}")
            dropped.append({"source_section":number,"source_child_index":index,"reason":reason,"text":plain(env_doc.raw(node)),"external_urls":list(external_links(Document(env_doc.raw(node))))})

    result = base
    replacements = []
    # Existing paragraphs are left in place. Local institutional detail follows
    # the original BOK discussion, while the full international table follows
    # the original regulation analysis.
    policy = base_doc.by_id("policy")
    policy_html = base_doc.raw(policy)
    clarity = '<p>CLARITY 관련 2026년 9월 15일 상원 기록은 심의개시 동의의 토론종결 표결 부결이다. 본안의 최종 부결이나 제정으로 읽을 수 없으며, 이후 입법절차 전체의 최신 상태를 판정한 것은 아니다.<sup><a href="#ref8">8</a></sup></p>'
    first_policy_paragraph = base_doc.raw(next(node for node in policy.children if node.tag == "p"))
    policy_html = policy_html.replace(first_policy_paragraph, first_policy_paragraph+"\n"+clarity, 1)
    policy_html = policy_html.replace("<h3>한국은행의 선택은 예금과 중앙은행 결제의 연결에 있다</h3>", policy_global+"\n<h3>한국은행의 선택은 예금과 중앙은행 결제의 연결에 있다</h3>", 1)
    policy_html = policy_html.replace("<h3>빠른 결제와 적은 자금 소요는 같은 말이 아니다</h3>", policy_korea+"\n<h3>빠른 결제와 적은 자금 소요는 같은 말이 아니다</h3>", 1)
    for key,fragments in additions.items():
        node = base_doc.by_id(key)
        original = base_doc.raw(node)
        content = policy_html if key == "policy" else original
        close = content.rfind("</section>")
        content = content[:close]+"\n"+"\n".join(fragments)+"\n"+content[close:]
        replacements.append((node.start,node.end,content))
    for start,end,content in sorted(replacements, reverse=True):
        result = result[:start]+content+result[end:]

    old_role = "BNY와 Securitize는 각각 명의관리·토큰화 제공자로 참여한다."
    new_role = 'BSTBL의 이전대리는 BNY가, BRSRV의 이전대리는 Securitize가 맡는다. 두 상품의 계약상 역할과 보수는 <a href="#env-source-B5">상세 근거 B5</a>에서 구분한다.'
    if result.count(old_role) != 1:
        raise ValueError("Original BlackRock role sentence changed; review source correction")
    result = result.replace(old_role,new_role,1)
    result = result.replace("통합 초판 1.0", "통합 개정 2.0")
    result = result.replace("</style>\n</head>", "</style>\n<style>"+CSS+"</style>\n</head>",1)
    if CSS not in result:
        raise ValueError("Could not locate original head style boundary")
    result = result.replace('<article id="report">', '<article id="report">\n'+CONTROLS,1)
    result = result.replace('<a href="#policy">3. 제도와 인프라의 역할</a>', '<a href="#policy">3. 제도와 인프라의 역할</a><a class="toc-sub" href="#macro">자금 이동과 거시경제</a>',1)
    print_button = '<button class="print" type="button" onclick="window.print()">인쇄</button>'
    result = result.replace(print_button, print_button+'\n<button class="report-control" id="save-report" type="button">HTML 저장</button>\n<p class="meta revision-record">자료 기준일 2026-10-05 · 기록일 2026-10-05 · 통합 개정 2.0<br>금융환경·기관 대응의 상세 비교와 근거를 관련 장에서 함께 읽을 수 있습니다.</p>',1)
    result = result.replace("</body>", JAVASCRIPT+"</body>",1)

    result = result.rstrip() + "\n"
    merged_doc = Document(result)
    ids = [node.attrs["id"] for node in merged_doc.nodes if "id" in node.attrs]
    duplicates = [key for key,count in Counter(ids).items() if count > 1]
    if duplicates:
        raise ValueError(f"Duplicate IDs: {duplicates}")
    missing_targets=[]
    for node in merged_doc.nodes:
        for name in ("href","for","aria-controls","aria-labelledby","aria-describedby"):
            value=node.attrs.get(name,"")
            targets = [value[1:]] if name=="href" and value.startswith("#") else (value.split() if name!="href" else [])
            missing_targets.extend(target for target in targets if target and target not in ids)
    if missing_targets:
        raise ValueError(f"Missing fragment or accessibility targets: {sorted(set(missing_targets))}")
    actual_urls = external_links(merged_doc)
    missing_urls = set(urls)-set(actual_urls)
    if missing_urls:
        raise ValueError(f"Missing external URLs: {sorted(missing_urls)}")
    report_original = base_doc.by_id("report")
    base_paragraphs = [base_doc.raw(node) for node in base_doc.nodes if node.tag=="p" and report_original.start<node.start<report_original.end]
    lost_paragraphs = [plain(paragraph) for paragraph in base_paragraphs if paragraph.replace(old_role,new_role) not in result]
    if lost_paragraphs:
        raise ValueError(f"Lost original report paragraphs: {lost_paragraphs}")
    original_ids = [node.attrs["id"] for node in base_doc.nodes if "id" in node.attrs]
    missing_original_ids = set(original_ids)-set(ids)
    if missing_original_ids:
        raise ValueError(f"Lost original anchors: {sorted(missing_original_ids)}")
    manifest = {
        "source_date":SOURCE_DATE,"record_date":SOURCE_DATE,"version":"통합 개정 2.0",
        "base_commit":BASE_COMMIT,"base_path":REPORT_PATH,"environment_path":SOURCE_PATH,
        "title":plain(base_doc.inner(next(node for node in base_doc.nodes if node.tag=="title"))),
        "base_sha256":hashlib.sha256(base.encode("utf-8")).hexdigest(),
        "environment_sha256":hashlib.sha256(environment.encode("utf-8")).hexdigest(),
        "result_sha256":hashlib.sha256(result.encode("utf-8")).hexdigest(),
        "bytes":len(result.encode("utf-8")),"base_paragraphs_preserved":len(base_paragraphs),
        "original_anchor_count":len(original_ids),"original_anchors_preserved":not missing_original_ids,
        "main_chapters":7,"new_main_chapters":[],"new_subsection_anchors":[entry["destination_anchor"] for entry in mapping],
        "mapping":mapping,"dropped_imported_blocks":dropped,
        "focused_restored_content":[{"source_section":4,"source_child_index":2,"destination":"policy","text":plain(clarity),"reference":"ref8","reason":"Preserve unique procedural defeat while omitting repeated OCC20-percent explanation"}],
        "base_sentence_corrections":[{"old":old_role,"new":plain(new_role),"evidence_anchor":"env-source-B5"}],
        "imported_cell_corrections":[{"source":"evidence B3","old":old_imported_roles,"new":plain(new_imported_roles),"evidence_anchor":"env-source-B5","source_report_modified":False}],
        "source_url_union":list(urls),"expected_external_urls":len(urls),"result_external_urls":len(actual_urls),
        "missing_source_urls":sorted(missing_urls),"duplicate_ids":duplicates,"missing_targets":missing_targets,
        "head_shell_preserved":True,"source_report_unchanged":True,
        "verification_scope":"Generation checks preserve original paragraphs/anchors and complete source URL union. Browser interaction, layout, print, and repository tests are separate checks.",
    }
    return result,manifest


def apply_kyobo_case(result, manifest, case):
    """Add the reviewed single-business decision without replacing the research."""
    if case["record_date"] != SOURCE_DATE:
        raise ValueError("The requested report record date must stay October 5")
    body = case["content_html"]
    if re.search(r"<script|\son\w+=", body, re.I):
        raise ValueError("Reviewed case content must not introduce executable markup")
    rows = []
    for fact in case["financial_facts"]:
        amount = fact["value_krw_thousand"]
        rows.append("<tr><td>"+escape(fact["label"])+"</td><td>"+f"{amount/100000:.1f}"+"억원</td><td>"+escape(fact["boundary"])+"</td></tr>")
    body = body.replace("{{financial_rows}}", "\n".join(rows))
    if "{{" in body:
        raise ValueError("Unresolved case content placeholder")
    doc = Document(result)
    chapter = doc.by_id("kyobo")
    first_p = next(node for node in chapter.children if node.tag == "p")
    result = result[:first_p.end]+"\n"+body+"\n"+result[first_p.end:]
    result = result.replace("6. 교보증권에는 상품 공급과 관리비용의 연결이 중요하다", case["chapter_title"], 1)
    doc = Document(result)
    summary = doc.by_id("summary")
    result = result[:summary.inner_end]+"\n"+case["summary_html"]+"\n"+result[summary.inner_end:]
    items = []
    for source in case["sources"]:
        link = '<a target="_blank" rel="noopener noreferrer" href="'+escape(source["url"], quote=True)+'">'+escape(source["title"])+"</a>"
        items.append('<li id="'+escape(source["id"], quote=True)+'">'+link+"<p>"+escape(source["location"])+"</p><p>"+escape(source["scope"])+"</p><p>공개일 "+escape(source["published_date"])+" · 원문 확인일 "+escape(source["verified_date"])+"</p></li>")
    evidence = '<div class="enrich"><details class="source-directory" id="kyobo-spc-evidence"><summary>교보증권 단일 업무의 확인 근거와 미확인 항목</summary><div class="evidence-body"><ol>'+"\n".join(items)+"</ol><p>"+escape(case["unknowns_note"])+"</p></div></details></div>"
    doc = Document(result)
    sources = doc.by_id("sources")
    result = result[:sources.inner_end]+"\n"+evidence+"\n"+result[sources.inner_end:]
    result = result.replace("통합 개정 2.0", "통합 개정 2.1")
    result = result.replace("자료 기준일 2026-10-05 · 기록일 2026-10-05 · 통합 개정 2.1", "초기 자료 기준일 2026-10-05 · 기록일 2026-10-05 · 통합 개정 2.1 · 교보 사례 추가 확인 2026-10-06", 1)
    result = result.replace('<a href="#kyobo">6. 교보증권에 적용할 방향</a>', '<a href="#kyobo">6. 교보증권에 적용할 방향</a><a class="toc-sub" href="#kyobo-spc-case">유동화SPC 사후관리 한 업무</a>', 1)
    result = result.rstrip()+"\n"
    final_doc = Document(result)
    ids = [node.attrs["id"] for node in final_doc.nodes if "id" in node.attrs]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate IDs after adding the case")
    for node in final_doc.nodes:
        value = node.attrs.get("href", "")
        if value.startswith("#") and value[1:] not in ids:
            raise ValueError("Unresolved case source anchor "+value)
    manifest.update({"version":"통합 개정 2.1", "result_sha256":hashlib.sha256(result.encode("utf-8")).hexdigest(), "bytes":len(result.encode("utf-8")), "result_external_urls":len(external_links(final_doc)), "decision_case":{"source_path":CASE_PATH,"verified_date":case["verified_date"],"selected_business":case["selected_business"],"scope":"One proposed Kyobo workflow; financial disclosures are not this product's earnings; no fabricated cost or client data", "source_urls":[source["url"] for source in case["sources"]]}})
    return result, manifest


def main():
    repo = Path(__file__).resolve().parents[1]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base",type=Path,help="Saved original report; defaults to git show of immutable first edition")
    parser.add_argument("--environment",type=Path,default=repo/SOURCE_PATH)
    parser.add_argument("--output",type=Path,default=repo/REPORT_PATH)
    parser.add_argument("--manifest",type=Path,help="Optional local verification manifest")
    parser.add_argument("--case",type=Path,default=repo/CASE_PATH,help="Reviewed Kyobo single-business case")
    args=parser.parse_args()
    if args.base:
        base=args.base.read_text(encoding="utf-8")
    else:
        base=subprocess.run(["git","-c",f"safe.directory={repo.as_posix()}","show",f"{BASE_COMMIT}:{REPORT_PATH}"],cwd=repo,check=True,capture_output=True,encoding="utf-8").stdout
    environment=args.environment.read_text(encoding="utf-8")
    result,manifest=build(base,environment)
    case=json.loads(args.case.read_text(encoding="utf-8"))
    result,manifest=apply_kyobo_case(result,manifest,case)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(result,encoding="utf-8",newline="\n")
    if args.manifest:
        args.manifest.parent.mkdir(parents=True,exist_ok=True)
        args.manifest.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps({"output":str(args.output),"bytes":manifest["bytes"],"sha256":manifest["result_sha256"],"external_urls":manifest["result_external_urls"],"original_paragraphs":manifest["base_paragraphs_preserved"],"source_date":SOURCE_DATE,"version":manifest["version"]},ensure_ascii=True))


if __name__=="__main__":
    main()
