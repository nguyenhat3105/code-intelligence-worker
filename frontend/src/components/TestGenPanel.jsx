import { useState } from 'react'

const TYPE_CFG = {
  unit:        { color:'#6366f1', icon:'🧪' },
  edge_case:   { color:'#f59e0b', icon:'⚠️' },
  negative:    { color:'#ef4444', icon:'❌' },
  integration: { color:'#10b981', icon:'🔗' },
}

export default function TestGenPanel({ tests, language }) {
  const [expanded, setExpanded] = useState(0)
  const [copied, setCopied] = useState(null)
  const testCases = tests.test_cases ?? []
  const framework = tests.framework || (language === 'python' ? 'pytest' : 'junit')

  const copy = (key, text) => {
    navigator.clipboard.writeText(text)
    setCopied(key)
    setTimeout(() => setCopied(null), 2000)
  }

  return (
    <div style={{ padding:20, display:'flex', flexDirection:'column', gap:20 }}>
      {/* Stats */}
      <div style={{ background:'#1c1f2e', borderRadius:12, padding:18, border:'1px solid #10b98140', display:'flex', alignItems:'center', justifyContent:'space-between' }}>
        <div style={{ display:'flex', alignItems:'center', gap:20 }}>
          <div style={{ textAlign:'center' }}>
            <div style={{ fontSize:40, fontWeight:800, color:'#10b981', lineHeight:1 }}>{testCases.length}</div>
            <div style={{ fontSize:12, color:'#10b981', fontWeight:600 }}>TEST CASES</div>
          </div>
          <div>
            <div style={{ color:'#e1e4e8', fontWeight:600, marginBottom:6 }}>Framework: <span style={{ color:'#818cf8' }}>{framework.toUpperCase()}</span></div>
            <div style={{ display:'flex', gap:8, flexWrap:'wrap' }}>
              {Object.entries(TYPE_CFG).map(([type, cfg]) => {
                const count = testCases.filter(t => t.type === type).length
                if (!count) return null
                return <span key={type} style={{ background:cfg.color+'20', color:cfg.color, border:`1px solid ${cfg.color}40`, borderRadius:20, padding:'2px 9px', fontSize:11, fontWeight:600 }}>{cfg.icon} {count} {type}</span>
              })}
            </div>
          </div>
        </div>
        <button onClick={() => copy('all', testCases.map(t => `# ${t.name}\n${t.code}`).join('\n\n'))}
          style={{ background:copied==='all'?'#10b98120':'#1c1f2e', border:`1px solid ${copied==='all'?'#10b981':'#2d3142'}`, color:copied==='all'?'#10b981':'#9ca3af', borderRadius:8, padding:'8px 16px', cursor:'pointer', fontSize:13 }}>
          {copied === 'all' ? '✅ Copied!' : '📋 Copy All'}
        </button>
      </div>

      {tests.summary && (
        <div style={{ background:'#1c1f2e', borderRadius:8, padding:14, border:'1px solid #2d3142', color:'#9ca3af', fontSize:14, lineHeight:1.6 }}>
          <span style={{ color:'#818cf8', fontWeight:600 }}>Strategy: </span>{tests.summary}
        </div>
      )}

      {tests.coverage_areas?.length > 0 && (
        <div>
          <div style={{ color:'#9ca3af', fontSize:13, fontWeight:600, textTransform:'uppercase', letterSpacing:1, marginBottom:10 }}>📊 Coverage Areas</div>
          <div style={{ display:'flex', flexWrap:'wrap', gap:8 }}>
            {tests.coverage_areas.map((area, i) => (
              <span key={i} style={{ background:'#1c1f2e', border:'1px solid #2d3142', borderRadius:20, padding:'4px 12px', color:'#9ca3af', fontSize:12 }}>✓ {area}</span>
            ))}
          </div>
        </div>
      )}

      <div>
        <div style={{ color:'#9ca3af', fontSize:13, fontWeight:600, textTransform:'uppercase', letterSpacing:1, marginBottom:10 }}>🧪 Test Cases ({testCases.length})</div>
        <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
          {testCases.map((tc, i) => {
            const cfg = TYPE_CFG[tc.type] || TYPE_CFG.unit
            const isOpen = expanded === i
            return (
              <div key={i} style={{ background:'#1c1f2e', border:`1px solid ${isOpen ? cfg.color+'50' : '#2d3142'}`, borderRadius:8, overflow:'hidden' }}>
                <div onClick={() => setExpanded(isOpen ? -1 : i)}
                  style={{ padding:'12px 16px', cursor:'pointer', display:'flex', alignItems:'center', gap:10, background:isOpen ? cfg.color+'10' : 'transparent' }}>
                  <span style={{ background:cfg.color+'20', color:cfg.color, border:`1px solid ${cfg.color}40`, borderRadius:4, padding:'1px 7px', fontSize:11, fontWeight:700 }}>{cfg.icon} {tc.type}</span>
                  <span style={{ color:'#e1e4e8', fontWeight:600, fontSize:14, flex:1, fontFamily:'monospace' }}>{tc.name}</span>
                  <span style={{ color:'#6b7280', fontSize:18 }}>{isOpen ? '▼' : '▶'}</span>
                </div>
                {isOpen && (
                  <div>
                    {tc.description && <div style={{ padding:'8px 16px 12px', color:'#9ca3af', fontSize:13, borderBottom:'1px solid #2d3142' }}>{tc.description}</div>}
                    <div style={{ position:'relative' }}>
                      <button onClick={() => copy(i, tc.code)}
                        style={{ position:'absolute', top:8, right:12, zIndex:1, background:copied===i?'#10b98120':'#1c1f2e', border:`1px solid ${copied===i?'#10b981':'#2d3142'}`, color:copied===i?'#10b981':'#6b7280', borderRadius:6, padding:'4px 10px', cursor:'pointer', fontSize:11 }}>
                        {copied === i ? '✅' : '📋'}
                      </button>
                      <pre style={{ margin:0, padding:'14px 16px', background:'#0d1117', color:'#e1e4e8', fontFamily:"'JetBrains Mono','Fira Code',monospace", fontSize:12, lineHeight:1.7, overflowX:'auto', whiteSpace:'pre' }}>
                        {tc.code}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
