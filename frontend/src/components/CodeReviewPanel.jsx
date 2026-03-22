const SEV = {
  HIGH:    { color:'#ef4444', icon:'🔴' },
  ERROR:   { color:'#ef4444', icon:'🔴' },
  MED:     { color:'#f59e0b', icon:'🟡' },
  WARNING: { color:'#f59e0b', icon:'🟡' },
  LOW:     { color:'#3b82f6', icon:'🔵' },
  INFO:    { color:'#6b7280', icon:'⚪' },
}
const CAT_ICON = { Security:'🔒', security:'🔒', Performance:'⚡', performance:'⚡', Style:'✨', style:'✨', Bug:'🐛', 'error-handling':'⚠️', 'null-check':'❓', design:'🏗️', 'code-quality':'📝' }

export default function CodeReviewPanel({ review }) {
  const score = review.score ?? 0
  const issues = review.issues ?? []
  const positives = review.positive_aspects ?? []
  const scoreColor = score >= 80 ? '#10b981' : score >= 60 ? '#f59e0b' : '#ef4444'
  const scoreLabel = score >= 80 ? 'Good' : score >= 60 ? 'Needs Work' : 'Critical'

  return (
    <div style={{ padding:20, display:'flex', flexDirection:'column', gap:20 }}>
      {/* Score */}
      <div style={{ background:'#1c1f2e', borderRadius:12, padding:20, border:`1px solid ${scoreColor}40`, display:'flex', alignItems:'center', gap:24 }}>
        <div style={{ textAlign:'center' }}>
          <div style={{ fontSize:48, fontWeight:800, color:scoreColor, lineHeight:1 }}>{score}</div>
          <div style={{ fontSize:12, color:scoreColor, fontWeight:600, marginTop:2 }}>{scoreLabel}</div>
        </div>
        <div style={{ flex:1 }}>
          <div style={{ color:'#e1e4e8', fontWeight:600, marginBottom:8 }}>Code Quality Score</div>
          <div style={{ background:'#2d3142', borderRadius:6, height:8, overflow:'hidden' }}>
            <div style={{ height:'100%', width:`${score}%`, background:`linear-gradient(90deg,${scoreColor},${scoreColor}aa)`, borderRadius:6 }} />
          </div>
          <div style={{ display:'flex', gap:16, marginTop:10 }}>
            {[['#ef4444','High',['HIGH','ERROR']],['#f59e0b','Medium',['MED','WARNING']],['#3b82f6','Low',['LOW','INFO']]].map(([c,l,sevs])=>(
              <div key={l} style={{ display:'flex', alignItems:'center', gap:5 }}>
                <span style={{ background:c+'25', color:c, borderRadius:10, padding:'1px 8px', fontSize:12, fontWeight:700 }}>{issues.filter(i=>sevs.includes(i.severity)).length}</span>
                <span style={{ color:'#6b7280', fontSize:12 }}>{l}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {review.summary && (
        <div style={{ background:'#1c1f2e', borderRadius:8, padding:14, border:'1px solid #2d3142', color:'#9ca3af', fontSize:14, lineHeight:1.6 }}>
          <span style={{ color:'#818cf8', fontWeight:600 }}>Summary: </span>{review.summary}
        </div>
      )}

      {issues.length > 0 && (
        <div>
          <div style={{ color:'#9ca3af', fontSize:13, fontWeight:600, textTransform:'uppercase', letterSpacing:1, marginBottom:10 }}>⚠️ Issues Found ({issues.length})</div>
          <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
            {issues.map((issue, i) => {
              const sev = SEV[issue.severity] || SEV.INFO
              return (
                <div key={i} style={{ background:sev.color+'10', border:`1px solid ${sev.color}30`, borderLeft:`3px solid ${sev.color}`, borderRadius:8, padding:14 }}>
                  <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:6 }}>
                    <span style={{ background:sev.color+'20', color:sev.color, border:`1px solid ${sev.color}40`, borderRadius:4, padding:'1px 7px', fontSize:11, fontWeight:700 }}>{sev.icon} {issue.severity}</span>
                    {issue.line && <span style={{ color:'#6b7280', fontSize:12 }}>Line {issue.line}</span>}
                    <span style={{ color:'#6b7280', fontSize:12 }}>{CAT_ICON[issue.category]||'📌'} {issue.category}</span>
                  </div>
                  <div style={{ color:'#e1e4e8', fontWeight:600, marginBottom:4 }}>{issue.title}</div>
                  {issue.description && <div style={{ color:'#9ca3af', fontSize:13, marginBottom:6, lineHeight:1.5 }}>{issue.description}</div>}
                  {issue.suggestion && (
                    <div style={{ background:'#10b98115', border:'1px solid #10b98130', borderRadius:6, padding:'7px 10px', color:'#6ee7b7', fontSize:12, lineHeight:1.5 }}>
                      💡 <strong>Fix:</strong> {issue.suggestion}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {positives.length > 0 && (
        <div>
          <div style={{ color:'#9ca3af', fontSize:13, fontWeight:600, textTransform:'uppercase', letterSpacing:1, marginBottom:10 }}>✅ Positive Aspects</div>
          {positives.map((p,i) => (
            <div key={i} style={{ display:'flex', gap:8, background:'#10b98110', border:'1px solid #10b98120', borderRadius:6, padding:'8px 12px', color:'#6ee7b7', fontSize:13, marginBottom:6 }}>
              <span>✓</span> {p}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
