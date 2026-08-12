import React,{useState} from 'react';
import {createRoot} from 'react-dom/client';
import * as d3 from 'd3';
import './style.css';

function App(){
 const [q,setQ]=useState(''); const [results,setResults]=useState<any[]>([]);
 async function search(){ const r=await fetch(`http://localhost:8000/api/v1/search?q=${encodeURIComponent(q)}`); setResults((await r.json()).results||[]); }
 return <main><header><h1>Web Data Indexer</h1><p>Search documents, inspect entities and trace provenance.</p></header><section className="search"><input value={q} onChange={e=>setQ(e.target.value)} placeholder="Search indexed web data"/><button onClick={search}>Search</button></section><section><h2>Results</h2>{results.map(r=><article key={r.id}><a href={r.url} target="_blank">{r.title||r.url}</a><small>{r.url}</small></article>)}</section><section><h2>Entity Graph</h2><svg id="graph" width="700" height="260"><text x="20" y="30">Select an entity to visualize its relationship graph.</text></svg></section></main>
}
createRoot(document.getElementById('root')!).render(<App/>);
void d3;
