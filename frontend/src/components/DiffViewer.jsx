export default function DiffViewer({ diff, reason, whatChanged, pros, cons, isVi, onConfirm, onCancel, loading }) {
  if (!diff || diff.length === 0) return null
  const removed = diff.filter(d => d.type === 'removed').length
  const added   = diff.filter(d => d.type === 'added').length
  const CONTEXT = 3
  const changeIndices = new Set(diff.map((d,i) => d.type !== 'unchanged' ? i : -1).filter(i => i >= 0))
  const visibleIndices = new Set()
  changeIndices.forEach(ci => { for (let i=Math.max(0,ci-CONTEXT); i<=Math.min(diff.length-1,ci+CONTEXT); i++) visibleIndices.add(i) })
  const segments = []; let prevVisible = -1
  diff.forEach((line,i) => {
    if (!visibleIndices.has(i)) return
    if (prevVisible !== -1 && i > prevVisible+1) segments.push({ type:'separator', count: i-prevVisible-1 })
    segments.push({ ...line, index:i }); prevVisible = i
  })
  return (
    <div style={{ display:'flex', flexDirection:'column', gap:0 }}>
      <div style={{ background:'#161924', borderRadius:'10px 10px 0 0', padding:'14px 16px', border:'1px solid #2d3142', borderBottom:'none' }}>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:10 }}>
          <div style={{ color:'#e1e4e8', fontWeight:700, fontSize:14 }}>🔍 {isVi?'Xem trước thay đổi':'Preview Changes'}</div>
          <div style={{ display:'flex', gap:8 }}>
            <span style={{ background:'#ef444420', color:'#ef4444', border:'1px solid #ef444440', borderRadius:6, padding:'2px 10px', fontSize:12, fontWeight:700 }}>-{removed} {isVi?'xóa':'removed'}</span>
            <span style={{ background:'#10b98120', color:'#10b981', border:'1px solid #10b98140', borderRadius:6, padding:'2px 10px', fontSize:12, fontWeight:700 }}>+{added} {isVi?'thêm':'added'}</span>
          </div>
        </div>
        {reason && (
          <div style={{ background:'#6366f115', border:'1px solid #6366f130', borderRadius:8, padding:'8px 12px', marginBottom:8 }}>
            <div style={{ color:'#818cf8', fontSize:11, fontWeight:600, textTransform:'uppercase', letterSpacing:1, marginBottom:4 }}>📌 {isVi?'Lý do thay đổi':'Reason'}</div>
            <div style={{ color:'#c4b5fd', fontSize:13, lineHeight:1.5 }}>{reason}</div>
          </div>
        )}
        {whatChanged && (
          <div style={{ background:'#f59e0b10', border:'1px solid #f59e0b30', borderRadius:8, padding:'8px 12px' }}>
            <div style={{ color:'#f59e0b', fontSize:11, fontWeight:600, textTransform:'uppercase', letterSpacing:1, marginBottom:4 }}>✏️ {isVi?'Vị trí thay đổi':'What Changed'}</div>
            <div style={{ color:'#fcd34d', fontSize:13, lineHeight:1.5 }}>{whatChanged}</div>
          </div>
        )}
      </div>
      <div style={{ border:'1px solid #2d3142', borderTop:'none', background:'#0d1117', overflow:'auto', maxHeight:360, fontFamily:"'JetBrains Mono',monospace", fontSize:12, lineHeight:1.7 }}>
        {segments.map((seg,i) => {
          if (seg.type === 'separator') return <div key={`sep-${i}`} style={{ background:'#1c1f2e', color:'#4b5563', padding:'3px 12px', fontSize:11, borderTop:'1px solid #2d3142', borderBottom:'1px solid #2d3142' }}>⋯ {seg.count} {isVi?'dòng không đổi':'unchanged lines'}</div>
          const bg = seg.type==='removed'?'#ef444412':seg.type==='added'?'#10b98112':'transparent'
          const border = seg.type==='removed'?'#ef4444':seg.type==='added'?'#10b981':'transparent'
          const color = seg.type==='removed'?'#fca5a5':seg.type==='added'?'#6ee7b7':'#9ca3af'
          const prefix = seg.type==='removed'?'-':seg.type==='added'?'+':' '
          return (
            <div key={i} style={{ display:'flex', background:bg, borderLeft:`3px solid ${border}` }}>
              <span style={{ width:40, textAlign:'right', color:'#374151', padding:'0 6px', userSelect:'none', fontSize:11, flexShrink:0 }}>{seg.line_old||''}</span>
              <span style={{ width:40, textAlign:'right', color:'#374151', padding:'0 6px', userSelect:'none', fontSize:11, flexShrink:0 }}>{seg.line_new||''}</span>
              <span style={{ width:18, textAlign:'center', color:seg.type==='removed'?'#ef4444':seg.type==='added'?'#10b981':'#374151', fontWeight:700, flexShrink:0 }}>{prefix}</span>
              <span style={{ color, padding:'0 8px', whiteSpace:'pre', flex:1 }}>{seg.content||' '}</span>
            </div>
          )
        })}
      </div>
      {(pros?.length>0||cons?.length>0) && (
        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:0, border:'1px solid #2d3142', borderTop:'none' }}>
          <div style={{ background:'#10b98108', padding:'12px 14px', borderRight:'1px solid #2d3142' }}>
            <div style={{ color:'#10b981', fontSize:11, fontWeight:700, textTransform:'uppercase', letterSpacing:1, marginBottom:8 }}>✅ {isVi?'Ưu điểm':'Pros'}</div>
            {pros?.map((p,i)=>(<div key={i} style={{ display:'flex', gap:6, color:'#6ee7b7', fontSize:12, marginBottom:5, lineHeight:1.4 }}><span>+</span>{p}</div>))}
          </div>
          <div style={{ background:'#ef444408', padding:'12px 14px' }}>
            <div style={{ color:'#ef4444', fontSize:11, fontWeight:700, textTransform:'uppercase', letterSpacing:1, marginBottom:8 }}>⚠️ {isVi?'Nhược điểm':'Cons'}</div>
            {cons?.length>0 ? cons.map((c,i)=>(<div key={i} style={{ display:'flex', gap:6, color:'#fca5a5', fontSize:12, marginBottom:5, lineHeight:1.4 }}><span>−</span>{c}</div>)) : <div style={{ color:'#4b5563', fontSize:12 }}>{isVi?'Không có nhược điểm đáng kể':'No significant tradeoffs'}</div>}
          </div>
        </div>
      )}
      <div style={{ display:'flex', gap:10, padding:'12px 0 4px' }}>
        <button onClick={onConfirm} disabled={loading} style={{ flex:1, padding:'9px 0', borderRadius:8, border:'none', background:loading?'#374151':'linear-gradient(135deg,#10b981,#059669)', color:'#fff', cursor:loading?'not-allowed':'pointer', fontWeight:700, fontSize:13, display:'flex', alignItems:'center', justifyContent:'center', gap:6 }}>
          {loading ? '⏳ '+(isVi?'Đang áp dụng...':'Applying...') : '✅ '+(isVi?'Xác nhận áp dụng':'Confirm & Apply')}
        </button>
        <button onClick={onCancel} disabled={loading} style={{ padding:'9px 20px', borderRadius:8, border:'1px solid #2d3142', background:'transparent', color:'#9ca3af', cursor:'pointer', fontWeight:600, fontSize:13 }}>
          {isVi?'Hủy':'Cancel'}
        </button>
      </div>
    </div>
  )
}
