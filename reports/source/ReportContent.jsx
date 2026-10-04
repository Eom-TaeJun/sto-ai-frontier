import React, { useState } from 'react';
import { DataComponent, EvidenceChart, ReportSection, RichNarrative, useDataApp } from '../../data-app-public.jsx';

const fmt=(n,d=2)=>(Object.is(Number(n),-0)?0:Number(n)).toLocaleString('ko-KR',{maximumFractionDigits:d,minimumFractionDigits:d});
const tableCells=line=>line.trim().replace(/^\|/,'').replace(/\|$/,'').split(/(?<!\\)\|/).map(cell=>cell.trim().replace(/\\\|/g,'|'));
const numericCell=value=>typeof value==='string'&&/^[-+−]?\d[\d,]*(?:\.\d+)?\s*(?:억원|조원|원|%|bp)?$/.test(value.trim());
function narrativeParts(value) {
 if(typeof value!=='string')return [{kind:'prose',value}];
 const lines=value.split('\n'),parts=[];let prose=[],i=0,fenced=false;
 const flush=()=>{const text=prose.join('\n').trim();if(text)parts.push({kind:'prose',value:text});prose=[];};
 while(i<lines.length){
  if(lines[i].trim().startsWith('```'))fenced=!fenced;
  const separator=lines[i+1]&&tableCells(lines[i+1]);
  if(!fenced&&lines[i].includes('|')&&separator?.length>1&&separator.every(cell=>/^:?-{3,}:?$/.test(cell))){
   flush();const headers=tableCells(lines[i]),rows=[];i+=2;
   while(i<lines.length&&lines[i].trim().startsWith('|')){rows.push(tableCells(lines[i]));i++;}
   parts.push({kind:'table',headers,rows});
  }else{prose.push(lines[i]);i++;}
 }
 flush();return parts;
}
const MD=({id,value,className='',...rest})=>{
 const parts=narrativeParts(value);
 if(!parts.some(part=>part.kind==='table'))return <RichNarrative id={id} value={value} className={className} label="보고서 문장 편집" {...rest}/>;
 const heading=typeof value==='string'?value.match(/^#{1,6}\s+(.+)$/m)?.[1]:null;
 return <div className={['authored-narrative',className].filter(Boolean).join(' ')}>{parts.map((part,index)=>part.kind==='prose'?<RichNarrative key={index} id={index===0?id:`${id}:prose-${index}`} value={part.value} label="보고서 문장 편집" {...rest}/>:<div key={index} className="report-table-wrap" role="region" aria-label={`${heading||'보고서'} 비교표`} tabIndex={0}><table className="report-narrative-table" data-reviewed-rows><thead><tr>{part.headers.map((cell,column)=><th key={column} scope="col" className={part.rows.length>0&&part.rows.every(row=>numericCell(row[column]))?'report-cell-number':undefined}>{cell}</th>)}</tr></thead><tbody>{part.rows.map((row,rowIndex)=><tr key={rowIndex}>{part.headers.map((_,column)=><td key={column} className={numericCell(row[column])?'report-cell-number':undefined}>{row[column]??''}</td>)}</tr>)}</tbody></table></div>)}</div>;
};
const evidenceText=value=>Array.isArray(value)?value.join('\n\n'):value??'미확인';

function Contribution({rows}) {
 const defaults=rows[0]||{volume:1000,fee:30,variable:10,fixed:1.5,burden:0.5};
 const [v,setV]=useState(defaults);
 const fields=[['volume','검토기간 과금 기준금액','억원'],['fee','기존 수익 대체분을 뺀 추가 보수','bp'],['variable','제휴·운영 변동비','bp'],['fixed','추가 고정비','억원'],['burden','조달·자본·예상손실 등 추가 부담','억원']];
 const validField=k=>v[k]!==''&&v[k]!=null&&Number.isFinite(Number(v[k]))&&(k==='fee'||Number(v[k])>=0);
 const validInputs=fields.every(([k])=>validField(k));
 const spread=validInputs?Number(v.fee)-Number(v.variable):null;
 const result=validInputs?Number(v.volume)*(spread/10000)-Number(v.fixed)-Number(v.burden):null;
 const threshold=spread>0?(Number(v.fixed)+Number(v.burden))/(spread/10000):null;
 const valid=validInputs&&Number.isFinite(result)&&(threshold===null||Number.isFinite(threshold));
 return <div className="decision-model">
 <MD id="model:context" value="아래 계산은 입력 가정에 따른 증분 손익을 비교하기 위한 도구입니다. 초기값은 설명용 가정이며 실제 보수·원가나 회사 전망이 아닙니다. 같은 검토기간의 신규 업무를 대상으로 하며, 기존 거래 이전분은 기존 방식 대비 추가 보수·비용으로 입력합니다. 수수료의 계약·인가상 허용 여부는 별도로 확인해야 합니다."/>
 <div className="model-inputs">{fields.map(([k,label,unit])=><label key={k}>{label} <span>({unit})</span><input aria-label={label} aria-invalid={!validField(k)} aria-describedby="model-input-guidance" type="number" min={k==='fee'?undefined:0} step="any" inputMode="decimal" value={v[k]??''} onChange={e=>{const value=e.target.value;setV(current=>({...current,[k]:value}));}}/></label>)}</div>
 <button type="button" className="model-reset" onClick={()=>setV({...defaults})}>기본 가정으로 되돌리기</button>
 <div className="model-result" aria-live="polite" aria-atomic="true"><strong>{valid?`${fmt(result)}억원`:'계산불가'}</strong><span>추가 공헌 · 입력에 포함한 비용 차감 후</span><p id="model-input-guidance">{!validInputs?'모든 항목에 숫자를 입력해주세요. 추가 보수는 음수를 허용하며, 과금 기준금액과 비용은 0 이상이어야 합니다.':!valid?'계산 가능한 숫자 범위를 넘었습니다. 입력 규모를 줄여주세요.':spread===0?(Number(v.fixed)+Number(v.burden)>0?'추가 보수와 변동비가 같습니다. 기준금액을 늘려도 기간의 고정비와 추가 부담을 회수하지 못합니다.':'추가 보수와 변동비가 같고 기간 비용이 0이므로, 모든 과금 규모의 추가 공헌은 0입니다.'):spread<0?'추가 보수가 변동비보다 작습니다. 과금 규모가 커질수록 추가 공헌이 감소합니다.':`같은 가정의 손익분기 과금 기준금액은 ${fmt(threshold,0)}억원입니다. 실제 고객 수요와 위험 부담을 확인해야 합니다.`}</p></div>
 <MD id="model:formula" value="계산: 과금 기준금액 × (추가 보수 − 변동비) ÷ 10,000 − 고정비 − 기타 추가 부담. 1bp = 0.01%. 사채의 일회성 발행액 또는 펀드의 평균잔액 등 같은 검토기간·과금 기준을 사용합니다. 손익분기는 고정비와 기타 추가 부담을 같은 검토기간의 고정 총액으로 둔 계산입니다. 조달·자본·예상손실이 잔액이나 기간에 비례하면 규모별로 다시 입력해야 합니다. 추가 보수는 기존 수익 잠식이 더 큰 경우 음수로 입력합니다. 검토시간 절약은 실제 비용 절감이나 추가 처리량으로 이어질 때만 편익입니다."/>
 </div>;
}

export function ReportContent() {
 const {snapshot,reviewedRows,visible,canEdit,mode,appTitle,setAppTitle}=useDataApp();
 const rows=id=>snapshot.queries?.[id]?reviewedRows(id):[];
 const segments=rows('kyobo_segments'),broker=rows('kyobo_brokerage'),cases=rows('us_cases'),policy=rows('korea_policy'),scenarios=rows('scenario_assumptions');
 const text=snapshot.report?.narratives||{}, previews=snapshot.report?.sourcePreviews||{};
 const summary=text.summary||'## 요약\n\n교보증권의 기존 수익, 국내 제도의 적용 범위와 미국 금융기관의 사업모델을 기준으로 초기 진입 업무와 투자 확대 조건을 검토한다.';
 const summaryQueries=['us_cases','korea_policy','kyobo_brokerage','kyobo_financials','peer_context'].filter(q=>snapshot.queries?.[q]);
 const section=(id,title,qids,body)=>{
  const available=qids.filter(q=>snapshot.queries?.[q]);
  return visible(id)&&available.length>0&&<ReportSection key={id} id={id} title={title} queryId={available[0]} queryIds={available} sourceRowsByQuery={Object.fromEntries(available.map(q=>[q,rows(q)]))} showHeading={false}><MD id={`${id}:body`} value={body||'이 항목의 근거와 분석을 준비 중입니다.'} sourcePreviews={previews}/></ReportSection>;
 };
 const openCase=id=>{const detail=document.getElementById(`case-${id}`);if(detail){detail.open=true;detail.querySelector('summary')?.focus({preventScroll:true});}};
 const stageLabel=stage=>stage==='PILOT'?'실증':'제공·사용';
 const asOf=(snapshot.report?.asOf||'2026-10-04').replace(/-/g,'.');
 const toc=[
  ['chapter-1','Ⅰ. 교보증권의 사업여건과 제도 변화'],
  ['chapter-2','Ⅱ. 미국 금융기관의 사업모델과 수익조건'],
  ['chapter-3','Ⅲ. 교보증권의 진입대안과 우선순위'],
  ['chapter-4','Ⅳ. 단계별 추진방향과 운영과제'],
  ['references','참고자료 및 분석 범위'],
  ['appendix-1','부록 1. 공시 부문별 영업이익'],
  ['appendix-2','부록 2. 미국 사례 상세자료'],
  ['appendix-3','부록 3. 증분 손익 계산']
 ];
 return <article className="report-content" aria-label="토큰증권 제도 시행에 대비한 교보증권의 사업전략 보고서">
  <header className="report-hero">
   <p className="report-eyebrow">{asOf} · 사업전략 검토</p>
   <h1 data-data-app-title contentEditable={canEdit&&mode==='edit'} suppressContentEditableWarning onBlur={canEdit&&mode==='edit'?e=>setAppTitle(e.currentTarget.textContent.trim()||appTitle):undefined}>{appTitle}</h1>
   <MD id="report:intro" className="report-deck" value="미국 금융기관의 사업모델과 초기 진입과제"/>
  </header>

  {summaryQueries.length>0?visible('report-summary')&&<ReportSection id="report-summary" title="요약" queryId={summaryQueries[0]} queryIds={summaryQueries} sourceRowsByQuery={Object.fromEntries(summaryQueries.map(q=>[q,rows(q)]))} showHeading={false}><MD id="report:summary" value={summary} sourcePreviews={previews}/></ReportSection>:<MD id="report:summary" value={summary} sourcePreviews={previews}/>}

  <nav className="report-toc" aria-label="보고서 목차">
   <p className="report-toc-title">목차</p>
   <ol>{toc.map(([id,label])=><li key={id}><a href={`#${id}`}>{label}</a></li>)}</ol>
  </nav>

  <section id="chapter-1" className="report-chapter" aria-labelledby="chapter-1-title">
   <h2 id="chapter-1-title" className="report-chapter-title">Ⅰ. 교보증권의 사업여건과 제도 변화</h2>
   {section('kyobo-baseline','현재 수익구조와 경쟁 여건',['kyobo_segments','kyobo_brokerage','kyobo_financials','peer_context'],text.baseline)}
   {visible('broker-chart')&&<EvidenceChart id="broker-chart" queryId="kyobo_brokerage" title="그림 1. 상품별 수탁수수료 구성" description="2026년 상반기 별도 · 총수수료 · 억원" rows={broker} sourceRows={broker} spec={{type:'horizontalBar',x:'product',y:'fee',xLabel:'억원',valueDecimals:2,legend:{show:false}}} height={340}/>}
   {policy.length>0&&section('korea-boundary','국내 제도의 초기 적용 범위',['korea_policy'],text.policy)}
  </section>

  <section id="chapter-2" className="report-chapter" aria-labelledby="chapter-2-title">
   <h2 id="chapter-2-title" className="report-chapter-title">Ⅱ. 미국 금융기관의 사업모델과 수익조건</h2>
   {cases.length>0&&section('economic-mechanism','미국 금융기관의 사업모델과 수익조건',['us_cases','korea_policy'],text.mechanism)}
  </section>

  <section id="chapter-3" className="report-chapter" aria-labelledby="chapter-3-title">
   <h2 id="chapter-3-title" className="report-chapter-title">Ⅲ. 교보증권의 진입대안과 우선순위</h2>
   {cases.length>0&&section('kyobo-response','교보증권의 진입대안과 우선순위',['kyobo_financials','peer_context','kyobo_ai','us_cases','korea_policy'],text.response)}
  </section>

  <section id="chapter-4" className="report-chapter" aria-labelledby="chapter-4-title">
   <h2 id="chapter-4-title" className="report-chapter-title">Ⅳ. 단계별 추진방향과 운영과제</h2>
   {cases.length>0&&section('scenario-response','제도와 수요에 따른 투자 범위',['us_cases','korea_policy'],text.scenarios)}
   {cases.length>0&&section('ai-operating-model','지원부문의 운영과제와 AI 활용',['kyobo_ai','us_cases','korea_policy'],text.ai)}
   {cases.length>0&&section('decision-signals','착수·확대·중단의 판단 기준',['us_cases','korea_policy'],text.signals)}
  </section>

  <section id="references" className="report-references" aria-label="참고자료 및 분석 범위">
   <MD id="report:methods" value={text.methods||'## 참고자료 및 분석 범위\n\n공개자료를 바탕으로 교보증권의 수익구조, 미국 금융기관의 사업모델과 국내 제도를 비교한다. 자료별 기준일과 수익 지표의 정의를 확인해야 한다.'} sourcePreviews={previews}/>
  </section>

  <section id="appendix-1" className="report-appendix" aria-labelledby="appendix-1-title">
   <h2 id="appendix-1-title" className="report-appendix-title">부록 1. 공시 부문별 영업이익</h2>
   {visible('segment-chart')&&<EvidenceChart id="segment-chart" queryId="kyobo_segments" title="그림 2. 공시 부문별 영업이익" description="2025·2026년 상반기 연결 · 억원 · 부문 간 손익귀속·비용 배부 상세는 추가 확인 필요" rows={segments} sourceRows={segments} spec={{type:'horizontalBar',x:'segment',y:'2026H1',fields:['2025H1','2026H1'],stackable:false,xLabel:'억원',valueDecimals:2,legend:{labels:{'2025H1':'2025년 상반기','2026H1':'2026년 상반기'}}}} height={390}/>}
  </section>

  <section id="appendix-2" className="report-appendix" aria-labelledby="appendix-2-title">
   <h2 id="appendix-2-title" className="report-appendix-title">부록 2. 미국 사례 상세자료</h2>
   {cases.length>0&&visible('us-benchmark')&&<ReportSection id="us-benchmark" title="미국 사례 상세자료" queryId="us_cases" sourceRows={cases} showHeading={false}>
    <MD id="us-benchmark:lead" value="본문의 사업모델 비교에 사용한 사례다. 제공·사용 또는 실증 여부는 공개자료에서 확인된 범위이며, 지속 매출·비용 절감과 이용 규모는 사례별로 별도 확인해야 한다. 기관·사례명을 누르면 상세자료로 이동한다."/>
    <div className="report-table-wrap" role="region" aria-label="미국 금융기관 사례 비교표" tabIndex={0}>
     <table className="benchmark-table" data-reviewed-rows>
      <caption>부표 1. 미국 금융기관의 토큰화 사례와 적용 범위</caption>
      <thead><tr><th scope="col">기관·사례</th><th scope="col">상품·업무의 변화</th><th scope="col">제공 현황</th><th scope="col">적용 범위와 제약</th></tr></thead>
      <tbody>{cases.map(c=><tr key={c.id}><td><a href={`#case-${c.id}`} onClick={()=>openCase(c.id)}>{c.title}</a></td><td>{c.change}</td><td>{stageLabel(c.stage)}<br/><span className="minor">{c.date}</span></td><td>{c.boundary}</td></tr>)}</tbody>
     </table>
    </div>
    <div className="benchmark-details">{cases.map(c=><details key={c.id} id={`case-${c.id}`} className="case-detail">
     <summary>{c.title} <span>{stageLabel(c.stage)}</span></summary>
     <div data-reviewed-rows>
      <h3>상품·운영구조</h3><p>{evidenceText(c.facts)}</p>
      <h3>사업상 의미</h3><p>{evidenceText(c.interpretation)}</p>
      <h3>추가 확인사항</h3><p>{evidenceText(c.unknowns)}</p>
      <h3>국내 적용조건</h3><p>{evidenceText(c.kyobo_conditions)}</p><p>{evidenceText(c.update_signals)}</p>
      <div className="case-sources">{c.sources?.map((s,i)=><p key={i}><a href={s.url} target="_blank" rel="noopener noreferrer">{s.title}</a> · {s.date||'공개일 미표시'}</p>)}</div>
     </div>
    </details>)}</div>
   </ReportSection>}
  </section>

  <section id="appendix-3" className="report-appendix" aria-labelledby="appendix-3-title">
   <h2 id="appendix-3-title" className="report-appendix-title">부록 3. 증분 손익 계산</h2>
   {scenarios.length>0&&visible('contribution-model')&&<DataComponent id="contribution-model" title="증분 손익과 손익분기 조건" queryId="scenario_assumptions" sourceRows={scenarios} kind="custom"><Contribution rows={scenarios}/></DataComponent>}
  </section>
 </article>;
}
