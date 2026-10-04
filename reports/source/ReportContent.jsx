import React, { useState } from 'react';
import { DataComponent, EvidenceChart, ReportSection, RichNarrative, useDataApp } from '../../data-app-public.jsx';

const fmt=(n,d=2)=>(Object.is(Number(n),-0)?0:Number(n)).toLocaleString('ko-KR',{maximumFractionDigits:d,minimumFractionDigits:d});
const tableCells=line=>line.trim().replace(/^\|/,'').replace(/\|$/,'').split(/(?<!\\)\|/).map(cell=>cell.trim().replace(/\\\|/g,'|'));
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
 return <div className={['authored-narrative',className].filter(Boolean).join(' ')}>{parts.map((part,index)=>part.kind==='prose'?<RichNarrative key={index} id={index===0?id:`${id}:prose-${index}`} value={part.value} label="보고서 문장 편집" {...rest}/>:<div key={index} className="report-table-wrap" role="region" aria-label={`${heading||'보고서'} 비교표`} tabIndex={0}><table className="report-narrative-table" data-reviewed-rows><thead><tr>{part.headers.map((cell,column)=><th key={column} scope="col">{cell}</th>)}</tr></thead><tbody>{part.rows.map((row,rowIndex)=><tr key={rowIndex}>{part.headers.map((_,column)=><td key={column}>{row[column]??''}</td>)}</tr>)}</tbody></table></div>)}</div>;
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
 <MD id="model:context" value="**HYPOTHESIS · 산술 민감도, 회사 전망 아님.** 모든 입력은 설명용 가정입니다. 같은 검토기간의 신규 업무를 대상으로 하며, 기존 거래 이전분은 기존 방식 대비 증분 보수·비용으로 입력합니다. 수수료의 계약·인가상 허용 여부는 별도 확인 대상입니다."/>
 <div className="model-inputs">{fields.map(([k,label,unit])=><label key={k}>{label} <span>({unit})</span><input aria-label={label} aria-invalid={!validField(k)} aria-describedby="model-input-guidance" type="number" min={k==='fee'?undefined:0} step="any" inputMode="decimal" value={v[k]??''} onChange={e=>{const value=e.target.value;setV(current=>({...current,[k]:value}));}}/></label>)}</div>
 <button type="button" className="model-reset" onClick={()=>setV({...defaults})}>기본 가정으로 되돌리기</button>
 <div className="model-result" aria-live="polite" aria-atomic="true"><strong>{valid?`${fmt(result)}억원`:'미확인'}</strong><span>추가 공헌 · 입력에 포함한 비용 차감 후</span><p id="model-input-guidance">{!validInputs?'모든 항목에 숫자를 입력해주세요. 추가 보수는 음수를 허용하며, 과금 기준금액과 비용은 0 이상이어야 합니다.':!valid?'계산 가능한 숫자 범위를 넘었습니다. 입력 규모를 줄여주세요.':spread===0?(Number(v.fixed)+Number(v.burden)>0?'추가 보수와 변동비가 같습니다. 기준금액을 늘려도 기간의 고정비와 추가 부담을 회수하지 못합니다.':'추가 보수와 변동비가 같고 기간 비용이 0이므로, 모든 과금 규모의 추가 공헌은 0입니다.'):spread<0?'추가 보수가 변동비보다 작습니다. 과금 규모가 커질수록 추가 공헌이 감소합니다.':`같은 가정의 손익분기 과금 기준금액은 ${fmt(threshold,0)}억원입니다. 실제 고객 수요와 위험 부담을 확인해야 합니다.`}</p></div>
 <MD id="model:formula" value="계산: 과금 기준금액 × (추가 보수 − 변동비) ÷ 10,000 − 고정비 − 기타 추가 부담. 1bp = 0.01%. 사채의 일회성 발행액 또는 펀드의 평균잔액 등 같은 검토기간·과금 기준을 사용합니다. 손익분기는 고정비와 기타 추가 부담을 같은 검토기간의 고정 총액으로 둔 계산입니다. 조달·자본·예상손실이 잔액이나 기간에 비례하면 규모별로 다시 입력해야 합니다. 추가 보수는 기존 수익 잠식이 더 큰 경우 음수로 입력합니다. 검토시간 절약은 실제 비용 절감이나 추가 처리량으로 이어질 때만 편익입니다."/>
 </div>;
}

export function ReportContent() {
 const {snapshot,reviewedRows,visible,canEdit,mode,appTitle,setAppTitle}=useDataApp();
 const rows=id=>snapshot.queries?.[id]?reviewedRows(id):[];
 const segments=rows('kyobo_segments'),broker=rows('kyobo_brokerage'),cases=rows('us_cases'),policy=rows('korea_policy'),scenarios=rows('scenario_assumptions');
 const text=snapshot.report?.narratives||{}, previews=snapshot.report?.sourcePreviews||{};
 const summary=text.summary||'## 현재 진단\n\n교보의 현재 수익을 기준선으로 삼고, 미국 상품·인프라의 실제 사용 단계와 한국의 제도 범위를 비교한다.';
 const summaryQueries=['us_cases','korea_policy'].filter(q=>snapshot.queries?.[q]);
 const section=(id,title,qids,body)=>{
  const available=qids.filter(q=>snapshot.queries?.[q]);
  return visible(id)&&available.length>0&&<ReportSection key={id} id={id} title={title} queryId={available[0]} queryIds={available} sourceRowsByQuery={Object.fromEntries(available.map(q=>[q,rows(q)]))} showHeading={false}><MD id={`${id}:body`} value={`## ${title}\n\n${body||'이 항목의 근거와 해석을 준비 중입니다.'}`} sourcePreviews={previews}/></ReportSection>;
 };
 const openCase=id=>{const detail=document.getElementById(`case-${id}`);if(detail){detail.open=true;detail.querySelector('summary')?.focus({preventScroll:true});}};
 return <article className="report-content" aria-label="미국 금융권 벤치마킹과 교보증권 대응 보고서">
 <header className="report-hero"><p className="report-eyebrow">미국 금융권 벤치마킹 · 교보증권 대응 검토</p><h1 data-data-app-title contentEditable={canEdit&&mode==='edit'} suppressContentEditableWarning onBlur={canEdit&&mode==='edit'?e=>setAppTitle(e.currentTarget.textContent.trim()||appTitle):undefined}>{appTitle}</h1><MD id="report:intro" className="report-deck" value="토큰화가 바꾸는 상품·담보·기록·결제의 관계를 살펴보고, 교보증권이 지킬 수익과 새로 맡을 유료 업무를 구분한다."/></header>
 {summaryQueries.length>0?visible('report-summary')&&<ReportSection id="report-summary" title="현재 진단과 제안" queryId={summaryQueries[0]} queryIds={summaryQueries} sourceRowsByQuery={Object.fromEntries(summaryQueries.map(q=>[q,rows(q)]))} showHeading={false}><MD id="report:summary" value={summary} sourcePreviews={previews}/></ReportSection>:<MD id="report:summary" value={summary} sourcePreviews={previews}/>}
 {section('kyobo-baseline','교보의 현재 수익에서 출발한다',['kyobo_segments','kyobo_brokerage','kyobo_financials','peer_context'],text.baseline||'**FACT · 2026년 상반기.** 수탁수수료에서 주식 786.56억원, 해외선물 688.28억원이 함께 91.57%를 차지한다. 수탁수수료·순이자·부문 영업이익은 다른 손익 층위다. [교보증권 반기보고서](https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20260814003361).')}
 {visible('broker-chart')&&<EvidenceChart id="broker-chart" queryId="kyobo_brokerage" title="주식과 해외선물이 수탁수수료의 대부분을 차지한다" description="2026년 상반기 별도 · 총수수료 · 억원" rows={broker} sourceRows={broker} spec={{type:'horizontalBar',x:'product',y:'fee',xLabel:'억원',valueDecimals:2,legend:{show:false}}} height={340}/>}
 {visible('segment-chart')&&<EvidenceChart id="segment-chart" queryId="kyobo_segments" title="공시 부문별 영업이익은 증가와 손실이 함께 나타난다" description="2025·2026년 상반기 연결 · 억원 · 부문 간 손익귀속·비용 배부 상세 미확인" rows={segments} sourceRows={segments} spec={{type:'horizontalBar',x:'segment',y:'2026H1',fields:['2025H1','2026H1'],stackable:false,xLabel:'억원',valueDecimals:2,legend:{labels:{'2025H1':'2025년 상반기','2026H1':'2026년 상반기'}}}} height={390}/>}
 {cases.length>0&&section('economic-mechanism','토큰화는 금융 기능의 담당자와 연결 방식을 바꾼다',['us_cases','korea_policy'],text.mechanism)}
 {cases.length>0&&visible('us-benchmark')&&<ReportSection id="us-benchmark" title="미국 금융기관의 실제 선택" queryId="us_cases" sourceRows={cases} showHeading={false}>
 <MD id="us-benchmark:lead" value="## 미국 금융기관은 상품과 인프라의 연결부터 확장하고 있다\n\n단계는 원문의 사용 사실을 기준으로 분류한다. PRODUCTION은 실제 제공·사용이 확인된 범위이며, SCALE은 지속적인 사용량까지 확인된 범위다. 출시 발표와 지속 매출·비용절감·광범위한 이용은 구분한다."/>
 <div className="report-table-wrap" role="region" aria-label="미국 금융기관 사례 비교표" tabIndex={0}><table className="benchmark-table" data-reviewed-rows><thead><tr><th scope="col">기관·사례</th><th scope="col">실제로 바뀐 것</th><th scope="col">확인된 단계</th><th scope="col">남아 있는 제약</th></tr></thead><tbody>{cases.map(c=><tr key={c.id}><td><a href={`#case-${c.id}`} onClick={()=>openCase(c.id)}>{c.title}</a></td><td>{c.change}</td><td>{c.stage}<br/><span className="minor">{c.date}</span></td><td>{c.boundary}</td></tr>)}</tbody></table></div>
 <div className="benchmark-details">{cases.map(c=><details key={c.id} id={`case-${c.id}`} className="case-detail"><summary>{c.title} <span>{c.stage}</span></summary><div data-reviewed-rows><h3>FACT · 원문에서 확인한 범위</h3><p>{evidenceText(c.facts)}</p><h3>INTERPRETATION · 수익과 역할의 이동</h3><p>{evidenceText(c.interpretation)}</p><h3>UNKNOWN · 아직 확인하지 못한 것</h3><p>{evidenceText(c.unknowns)}</p><h3>HYPOTHESIS · 교보에 적용할 조건과 판단 수정 신호</h3><p>{evidenceText(c.kyobo_conditions)}</p><p>{evidenceText(c.update_signals)}</p><div className="case-sources">{c.sources?.map((s,i)=><p key={i}><a href={s.url} target="_blank" rel="noopener noreferrer">{s.title}</a> · {s.date||'공개일 미표시'}</p>)}</div></div></details>)}</div>
 </ReportSection>}
 {policy.length>0&&section('korea-boundary','한국은 단계별로 적용 가능한 상품과 역할이 다르다',['korea_policy'],text.policy)}
 {cases.length>0&&section('kyobo-response','교보는 기존 수익을 방어하며 유료 역할을 검증한다',['kyobo_financials','peer_context','kyobo_ai','us_cases','korea_policy'],text.response)}
 {cases.length>0&&section('scenario-response','환경이 달라지면 투자 범위도 바꾼다',['us_cases','korea_policy'],text.scenarios)}
 {scenarios.length>0&&visible('contribution-model')&&<DataComponent id="contribution-model" title="새 사업은 어떤 조건에서 비용을 회수하는가" queryId="scenario_assumptions" sourceRows={scenarios} kind="custom"><Contribution rows={scenarios}/></DataComponent>}
 {cases.length>0&&section('ai-operating-model','AI는 정보 처리와 예외 검토의 운영 방식을 바꾼다',['kyobo_ai','us_cases','korea_policy'],text.ai)}
 {cases.length>0&&section('decision-signals','확대·수정·보류 판단은 관찰 가능한 신호로 바꾼다',['us_cases','korea_policy'],text.signals)}
 <MD id="report:methods" value={text.methods||'## 근거와 읽는 방법\n\n기준일 2026-10-04. FACT, THEORY, INTERPRETATION, HYPOTHESIS, UNKNOWN을 구분한다. 실적은 2026년 상반기, 잔액은 6월 말이다. 교보의 확정 사업계획이나 내부자료를 제시하는 보고서가 아니다.'} sourcePreviews={previews}/>
 </article>;
}
