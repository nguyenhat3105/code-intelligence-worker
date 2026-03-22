export default function SeverityChart({ review }) {
  const issues = review.issues ?? []
  const score = review.score ?? 0
  const groups = [
    { label: 'HIGH / ERROR', keys: ['HIGH','ERROR'], color: '#ef4444' },
    { label: 'MEDIUM / WARNING', keys: ['MED','WARNING'], color: '#f59e0b' },
    { label: 'LOW / INFO', keys: ['LOW','INFO'], color: '#3b82f6' },
  ]
  const categories = {}
  issues.forEach(i => { const cat = i.category || 'Other'; categories[cat] = (categories[cat] || 0) + 1 })
  const scoreColor = score >= 80 ? '#10b981' : score >= 60 ? '#f59e0b' : '#ef4444'
  const maxCat = Math.max(...Object.values(categories), 1)
  return (
    <div style={{ padding:20, display:'flex', flexDirection:'column', gap:20 }}>
      <div style={{ background:'#1c1f2e', borderRadius:12, padding:20, border:`1px solid ${scoreColor}40` }}>
        <div style={{ color:'#9ca3af', fontSize:12, fontWeight:600, textTransform:'uppercase', letterSpacing:1, marginBottom:12 }}>📊 Quality Score</div>
        <div style={{ display:'flex', alignItems:'center', gap:20 }}>
          <div style={{ position:'relative', width:100, height:100, flexShrink:0 }}>
            <svg viewBox="0 0 100 100" style={{ transform:'rotate(-90deg)', width:100, height:100 }}>
              <circle cx="50" cy="50" r="40" fill="none" stroke="#2d3142" strokeWidth="10"/>
              <circle cx="50" cy="50" r="40" fill="none" stroke={scoreColor} strokeWidth="10"
                strokeDasharray={`${2*Math.PI*40*score/100} ${2*Math.PI*40}`} strokeLinecap="round"/>
            </svg>
            <div style={{ position:'absolute', inset:0, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
              <span style={{ fontSize:22, fontWeight:800, color:scoreColor }}>{score}</span>
              <span style={{ fontSize:9, color:'#6b7280' }}>/ 100</span>
            </div>
          </div>
          <div style={{ flex:1 }}>
            {groups.map(g => {
              const count = issues.filter(i => g.keys.includes(i.severity)).length
              const pct = issues.length ? (count/issues.length)*100 : 0
              return (
                <div key={g.label} style={{ marginBottom:10 }}>
                  <div style={{ display:'flex', justifyContent:'space-between', marginBottom:4 }}>
                    <span style={{ fontSize:12, color:g.color, fontWeight:600 }}>{g.label}</span>
                    <span style={{ fontSize:12, color:'#9ca3af' }}>{count} issues</span>
                  </div>
                  <div style={{ background:'#2d3142', borderRadius:4, height:6, overflow:'hidden' }}>
                    <div style={{ width:`${pct}%`, height:'100%', background:g.color, borderRadius:4 }}/>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
      {Object.keys(categories).length > 0 && (
        <div style={{ background:'#1c1f2e', borderRadius:12, padding:20, border:'1px solid #2d3142' }}>
          <div style={{ color:'#9ca3af', fontSize:12, fontWeight:600, textTransform:'uppercase', letterSpacing:1, marginBottom:16 }}>📂 Issues by Category</div>
          {Object.entries(categories).sort((a,b)=>b[1]-a[1]).map(([cat,count]) => {
            const pct = (count/maxCat)*100
            const catColors = { Security:'#ef4444', Performance:'#f59e0b', Style:'#6366f1', Bug:'#ec4899', 'error-handling':'#f97316', design:'#8b5cf6' }
            const color = catColors[cat] || '#6b7280'
            return (
              <div key={cat} style={{ marginBottom:10 }}>
                <div style={{ display:'flex', justifyContent:'space-between', marginBottom:4 }}>
                  <span style={{ fontSize:13, color:'#e1e4e8' }}>{cat}</span>
                  <span style={{ fontSize:12, color, fontWeight:700 }}>{count}</span>
                </div>
                <div style={{ background:'#2d3142', borderRadius:4, height:8, overflow:'hidden' }}>
                  <div style={{ width:`${pct}%`, height:'100%', background:color, borderRadius:4 }}/>
                </div>
              </div>
            )
          })}
        </div>
      )}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:12 }}>
        {[{label:'Total Issues',value:issues.length,color:'#e1e4e8',icon:'⚠️'},{label:'Critical',value:issues.filter(i=>['HIGH','ERROR'].includes(i.severity)).length,color:'#ef4444',icon:'🔴'},{label:'Categories',value:Object.keys(categories).length,color:'#818cf8',icon:'📂'}].map(s=>(
          <div key={s.label} style={{ background:'#1c1f2e', borderRadius:10, padding:16, border:'1px solid #2d3142', textAlign:'center' }}>
            <div style={{ fontSize:24 }}>{s.icon}</div>
            <div style={{ fontSize:28, fontWeight:800, color:s.color, lineHeight:1.2 }}>{s.value}</div>
            <div style={{ fontSize:11, color:'#6b7280', marginTop:2 }}>{s.label}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
