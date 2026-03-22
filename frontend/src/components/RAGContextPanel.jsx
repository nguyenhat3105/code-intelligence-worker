export default function RAGContextPanel({ result }) {
  const CAT_COLOR = { security:'#ef4444','error-handling':'#f97316',style:'#6366f1',performance:'#f59e0b',testing:'#10b981',design:'#8b5cf6','null-safety':'#ec4899','resource-management':'#14b8a6' }
  return (
    <div style={{ padding:20, display:'flex', flexDirection:'column', gap:20 }}>
      <div style={{ background:'linear-gradient(135deg,#1c1f2e,#161924)', borderRadius:12, padding:20, border:'1px solid #f59e0b40' }}>
        <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:8 }}>
          <span style={{ fontSize:28 }}>📚</span>
          <div>
            <div style={{ color:'#f59e0b', fontWeight:700, fontSize:15 }}>RAG Knowledge Base</div>
            <div style={{ color:'#6b7280', fontSize:12 }}>Retrieval-Augmented Generation — AI augments responses with domain knowledge</div>
          </div>
        </div>
        <div style={{ display:'flex', gap:8, flexWrap:'wrap', marginTop:12 }}>
          {[['27','Docs indexed'],['128','Vector dims'],['FAISS','Search engine'],['Trigram','Embedding']].map(([v,l]) => (
            <div key={l} style={{ background:'#f59e0b15', border:'1px solid #f59e0b30', borderRadius:8, padding:'6px 12px', textAlign:'center' }}>
              <div style={{ color:'#f59e0b', fontWeight:700, fontSize:14 }}>{v}</div>
              <div style={{ color:'#6b7280', fontSize:10 }}>{l}</div>
            </div>
          ))}
        </div>
      </div>
      <div style={{ background:'#1c1f2e', borderRadius:12, padding:20, border:'1px solid #2d3142' }}>
        <div style={{ color:'#9ca3af', fontSize:12, fontWeight:600, textTransform:'uppercase', letterSpacing:1, marginBottom:14 }}>⚙️ RAG Flow</div>
        {[{step:'1',icon:'📝',title:'Code Input',desc:'User submits Python or Java source code',color:'#6366f1'},{step:'2',icon:'🔧',title:'Static Analysis Tool',desc:'AI calls run_static_analysis() → detects issues via pylint + regex',color:'#8b5cf6'},{step:'3',icon:'🔍',title:'RAG Search',desc:'AI calls search_coding_standards() → FAISS finds top-3 relevant docs',color:'#f59e0b'},{step:'4',icon:'📚',title:'Context Injection',desc:'Retrieved docs injected into AI context → enriches review quality',color:'#10b981'},{step:'5',icon:'🧠',title:'AI Synthesis',desc:'LLaMA 3.3 70B synthesizes static analysis + RAG context → JSON output',color:'#ec4899'}].map(s=>(
          <div key={s.step} style={{ display:'flex', alignItems:'flex-start', gap:12, marginBottom:12 }}>
            <div style={{ width:28, height:28, borderRadius:'50%', background:s.color+'25', border:`1px solid ${s.color}60`, display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0, fontSize:12, fontWeight:700, color:s.color }}>{s.step}</div>
            <div><div style={{ color:'#e1e4e8', fontWeight:600, fontSize:13 }}>{s.icon} {s.title}</div><div style={{ color:'#6b7280', fontSize:12, marginTop:2 }}>{s.desc}</div></div>
          </div>
        ))}
      </div>
      <div style={{ background:'#1c1f2e', borderRadius:12, padding:20, border:'1px solid #2d3142' }}>
        <div style={{ color:'#9ca3af', fontSize:12, fontWeight:600, textTransform:'uppercase', letterSpacing:1, marginBottom:14 }}>📖 Knowledge Base Coverage</div>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(2,1fr)', gap:8 }}>
          {[{cat:'Security',count:6,icon:'🔒',color:'#ef4444',desc:'OWASP, SQL injection, secrets'},{cat:'Error Handling',count:4,icon:'⚠️',color:'#f97316',desc:'Python & Java exception patterns'},{cat:'Code Style',count:5,icon:'✨',color:'#6366f1',desc:'PEP 8, Google Style Guide'},{cat:'Performance',count:3,icon:'⚡',color:'#f59e0b',desc:'String concat, generators'},{cat:'pytest Patterns',count:5,icon:'🧪',color:'#10b981',desc:'Fixtures, parametrize, mocking'},{cat:'JUnit 5',count:5,icon:'☕',color:'#84cc16',desc:'Annotations, Mockito, assertions'},{cat:'Design',count:2,icon:'🏗️',color:'#8b5cf6',desc:'SOLID principles'},{cat:'Null Safety',count:2,icon:'❓',color:'#ec4899',desc:'Optional, null checks'}].map(item=>(
            <div key={item.cat} style={{ background:'#13161f', borderRadius:8, padding:'10px 12px', border:`1px solid ${item.color}25` }}>
              <div style={{ display:'flex', alignItems:'center', gap:6, marginBottom:4 }}>
                <span>{item.icon}</span>
                <span style={{ color:item.color, fontWeight:600, fontSize:12 }}>{item.cat}</span>
                <span style={{ marginLeft:'auto', background:item.color+'20', color:item.color, borderRadius:10, padding:'1px 7px', fontSize:10, fontWeight:700 }}>{item.count}</span>
              </div>
              <div style={{ color:'#6b7280', fontSize:11 }}>{item.desc}</div>
            </div>
          ))}
        </div>
      </div>
      {result?.review?.issues?.length > 0 && (
        <div style={{ background:'#1c1f2e', borderRadius:12, padding:20, border:'1px solid #2d3142' }}>
          <div style={{ color:'#9ca3af', fontSize:12, fontWeight:600, textTransform:'uppercase', letterSpacing:1, marginBottom:14 }}>🔗 Issues — RAG Enhanced</div>
          {result.review.issues.slice(0,5).map((issue,i) => {
            const color = CAT_COLOR[(issue.category||'').toLowerCase()] || '#6b7280'
            return (
              <div key={i} style={{ display:'flex', alignItems:'center', gap:10, background:'#13161f', borderRadius:6, padding:'8px 12px', border:'1px solid #2d3142', marginBottom:6 }}>
                <span style={{ background:color+'20', color, borderRadius:4, padding:'1px 7px', fontSize:10, fontWeight:700 }}>{issue.severity}</span>
                <span style={{ color:'#e1e4e8', fontSize:12, flex:1 }}>{issue.title}</span>
                <span style={{ background:'#f59e0b15', color:'#f59e0b', borderRadius:4, padding:'1px 7px', fontSize:10 }}>📚 RAG matched</span>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
