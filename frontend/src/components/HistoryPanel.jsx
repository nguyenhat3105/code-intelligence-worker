export default function HistoryPanel({ history, onLoad, onClear }) {
  const scoreColor = s => s >= 80 ? '#10b981' : s >= 60 ? '#f59e0b' : '#ef4444'
  return (
    <div style={{ display:'flex', flexDirection:'column', height:'100%' }}>
      <div style={{ padding:'14px 16px', borderBottom:'1px solid #2d3142', display:'flex', alignItems:'center', justifyContent:'space-between' }}>
        <div style={{ color:'#e1e4e8', fontWeight:600, fontSize:14 }}>🕐 History</div>
        {history.length > 0 && <button onClick={onClear} style={{ background:'transparent', border:'1px solid #2d3142', color:'#6b7280', borderRadius:6, padding:'3px 8px', cursor:'pointer', fontSize:11 }}>Clear</button>}
      </div>
      <div style={{ flex:1, overflow:'auto' }}>
        {history.length === 0 ? (
          <div style={{ padding:20, textAlign:'center', color:'#4b5563', fontSize:13 }}>No history yet.<br/>Analyze some code first!</div>
        ) : history.map(entry => (
          <div key={entry.id} onClick={() => onLoad(entry)} style={{ padding:'12px 16px', cursor:'pointer', borderBottom:'1px solid #1c1f2e' }}
            onMouseEnter={e=>e.currentTarget.style.background='#1c1f2e'} onMouseLeave={e=>e.currentTarget.style.background='transparent'}>
            <div style={{ display:'flex', alignItems:'center', gap:6, marginBottom:4 }}>
              <span style={{ fontSize:11 }}>{entry.language==='python'?'🐍':'☕'}</span>
              <span style={{ color:'#9ca3af', fontSize:11, textTransform:'uppercase', fontWeight:600 }}>{entry.language}</span>
              {entry.score !== null && <span style={{ marginLeft:'auto', background:scoreColor(entry.score)+'25', color:scoreColor(entry.score), borderRadius:10, padding:'1px 7px', fontSize:11, fontWeight:700 }}>{entry.score}</span>}
            </div>
            <div style={{ color:'#6b7280', fontSize:11, fontFamily:'monospace', whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis', marginBottom:4 }}>{entry.codeSnippet}</div>
            <div style={{ display:'flex', gap:8 }}>
              {entry.issueCount > 0 && <span style={{ color:'#ef4444', fontSize:10 }}>⚠️ {entry.issueCount}</span>}
              {entry.testCount > 0 && <span style={{ color:'#10b981', fontSize:10 }}>🧪 {entry.testCount}</span>}
              <span style={{ color:'#374151', fontSize:10, marginLeft:'auto' }}>{entry.timestamp}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
