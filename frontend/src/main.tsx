import React, {useEffect, useRef, useState} from 'react';
import {createRoot} from 'react-dom/client';
import * as d3 from 'd3';
import './style.css';

const API = 'http://localhost:8000/api/v1';

type Entity = {id:number; canonical_name:string; entity_type:string};
type Graph = {nodes:Entity[]; edges:{source:number; target:number; type:string; weight:number}[]};

function GraphView({entityId}:{entityId:number|null}) {
  const ref = useRef<SVGSVGElement|null>(null);
  useEffect(() => {
    if (!ref.current || !entityId) return;
    fetch(`${API}/entities/${entityId}/graph`).then(r=>r.json()).then((graph:Graph)=>{
      const svg = d3.select(ref.current); svg.selectAll('*').remove();
      const width = 760, height = 360;
      const simulation = d3.forceSimulation(graph.nodes as any)
        .force('link', d3.forceLink(graph.edges).id((d:any)=>d.id).distance(110))
        .force('charge', d3.forceManyBody().strength(-320))
        .force('center', d3.forceCenter(width/2, height/2));
      const link = svg.append('g').selectAll('line').data(graph.edges).join('line').attr('stroke-width', (d:any)=>Math.max(1,d.weight));
      const node = svg.append('g').selectAll('g').data(graph.nodes).join('g').call(d3.drag<any,any>()
        .on('start', (event,d)=>{if(!event.active) simulation.alphaTarget(.3).restart(); d.fx=d.x; d.fy=d.y;})
        .on('drag', (event,d)=>{d.fx=event.x; d.fy=event.y;})
        .on('end', (event,d)=>{if(!event.active) simulation.alphaTarget(0); d.fx=null; d.fy=null;}));
      node.append('circle').attr('r', (d:any)=>d.id===entityId?12:8);
      node.append('text').text((d:any)=>d.canonical_name).attr('x',12).attr('y',4).style('font-size','11px');
      simulation.on('tick',()=>{
        link.attr('x1',(d:any)=>d.source.x).attr('y1',(d:any)=>d.source.y).attr('x2',(d:any)=>d.target.x).attr('y2',(d:any)=>d.target.y);
        node.attr('transform',(d:any)=>`translate(${d.x},${d.y})`);
      });
      return () => simulation.stop();
    });
  }, [entityId]);
  return <svg ref={ref} width="760" height="360" viewBox="0 0 760 360"/>;
}

function App(){
 const [q,setQ]=useState(''); const [results,setResults]=useState<any[]>([]); const [entities,setEntities]=useState<Entity[]>([]); const [entityId,setEntityId]=useState<number|null>(null);
 async function search(){ const r=await fetch(`${API}/search?q=${encodeURIComponent(q)}`); setResults((await r.json()).results||[]); }
 async function loadEntities(){ const r=await fetch(`${API}/entities?limit=50`); setEntities((await r.json()).results||[]); }
 useEffect(()=>{loadEntities()},[]);
 return <main><header><h1>Web Data Indexer</h1><p>Search indexed documents, explore entity relationships, and inspect provenance.</p></header>
 <section className="search"><input value={q} onChange={e=>setQ(e.target.value)} onKeyDown={e=>e.key==='Enter'&&search()} placeholder="Search indexed web data"/><button onClick={search}>Search</button></section>
 <section><h2>Results</h2>{results.map(r=><article key={r.id}><a href={r.url} target="_blank" rel="noreferrer">{r.title||r.url}</a><small>{r.url}</small></article>)}</section>
 <section><h2>Entities</h2><div className="entities">{entities.map(e=><button key={e.id} onClick={()=>setEntityId(e.id)}>{e.canonical_name}</button>)}</div></section>
 <section><h2>Entity Graph</h2>{entityId?<GraphView entityId={entityId}/>:<p>Select an entity above.</p>}</section></main>
}
createRoot(document.getElementById('root')!).render(<App/>);
