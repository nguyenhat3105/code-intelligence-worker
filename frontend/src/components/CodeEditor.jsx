import { useMemo, useRef, useState } from 'react'

export default function CodeEditor({ code, onChange, language, issues = [], recentlyFixed = [], placeholder }) {
  const textareaRef = useRef()
  const gutterRef = useRef()
  const overlayRef = useRef()
  const [hoveredIssue, setHoveredIssue] = useState(null)
  const [tooltipPos, setTooltipPos] = useState({ x:0, y:0 })
  const [scrollTop, setScrollTop] = useState(0)

  const LINE_HEIGHT = 21.6
  const PADDING_TOP = 14

  const issuesByLine = useMemo(() => {
    const map = {}
    issues.forEach(issue => {
      if (issue.line) {
        if (!map[issue.line]) map[issue.line] = []
        map[issue.line].push(issue)
      }
    })
    return map
  }, [issues])

  const fixedSet = useMemo(() => new Set(recentlyFixed), [recentlyFixed])
  const lines = code.split('\n')

  const handleScroll = (e) => {
    const st = e.target.scrollTop
    setScrollTop(st)
    if (gutterRef.current) gutterRef.current.scrollTop = st
    if (overlayRef.current) overlayRef.current.scrollTop = st
  }

  const SEV_COLOR = {
    HIGH:    { bg:'rgba(239,68,68,0.15)',   border:'#ef4444', dot:'#ef4444', gutter:'rgba(239,68,68,0.25)' },
    ERROR:   { bg:'rgba(239,68,68,0.15)',   border:'#ef4444', dot:'#ef4444', gutter:'rgba(239,68,68,0.25)' },
    MED:     { bg:'rgba(245,158,11,0.12)',  border:'#f59e0b', dot:'#f59e0b', gutter:'rgba(245,158,11,0.2)' },
    WARNING: { bg:'rgba(245,158,11,0.12)',  border:'#f59e0b', dot:'#f59e0b', gutter:'rgba(245,158,11,0.2)' },
    LOW:     { bg:'rgba(59,130,246,0.10)',  border:'#3b82f6', dot:'#3b82f6', gutter:'rgba(59,130,246,0.15)' },
    INFO:    { bg:'rgba(107,114,128,0.10)', border:'#6b7280', dot:'#6b7280', gutter:'rgba(107,114,128,0.15)' },
  }

  const handleMouseMove = (e) => {
    if (!textareaRef.current) return
    const rect = textareaRef.current.getBoundingClientRect()
    const y = e.clientY - rect.top + scrollTop - PADDING_TOP
    const lineNum = Math.floor(y / LINE_HEIGHT) + 1
    const lineIssues = issuesByLine[lineNum]
    if (lineIssues?.length > 0) {
      setHoveredIssue({ lineNum, issues: lineIssues })
      setTooltipPos({ x: e.clientX, y: e.clientY })
    } else {
      setHoveredIssue(null)
    }
  }

  return (
    <div style={{ position:'relative', flex:1, display:'flex', overflow:'hidden', background:'#0d1117' }}>

      {/* Gutter */}
      <div ref={gutterRef} style={{ width:52, background:'#0d1117', borderRight:'1px solid #1c1f2e', overflow:'hidden', flexShrink:0, paddingTop:PADDING_TOP, userSelect:'none' }}>
        {lines.map((_, i) => {
          const lineNum = i + 1
          const lineIssues = issuesByLine[lineNum]
          const isFixed = fixedSet.has(lineNum)
          const topSev = lineIssues?.[0]?.severity
          const col = topSev ? SEV_COLOR[topSev] : null
          return (
            <div key={lineNum} style={{ height:LINE_HEIGHT, display:'flex', alignItems:'center', paddingRight:6, justifyContent:'flex-end', gap:4, background: isFixed?'rgba(16,185,129,0.1)':col?col.gutter:'transparent' }}>
              {col && !isFixed && <div style={{ width:6, height:6, borderRadius:'50%', background:col.dot, flexShrink:0 }}/>}
              {isFixed && <div style={{ fontSize:9, color:'#10b981', flexShrink:0 }}>✓</div>}
              <span style={{ color:col&&!isFixed?col.dot:isFixed?'#10b981':'#374151', fontSize:11, fontWeight:col||isFixed?600:400, minWidth:24, textAlign:'right' }}>{lineNum}</span>
            </div>
          )
        })}
      </div>

      {/* Highlight overlay */}
      <div ref={overlayRef} style={{ position:'absolute', left:52, right:0, top:0, bottom:0, overflow:'hidden', pointerEvents:'none', paddingTop:PADDING_TOP, paddingLeft:18 }}>
        {lines.map((_, i) => {
          const lineNum = i + 1
          const lineIssues = issuesByLine[lineNum]
          const isFixed = fixedSet.has(lineNum)
          const topSev = lineIssues?.[0]?.severity
          const col = topSev ? SEV_COLOR[topSev] : null
          if (!col && !isFixed) return <div key={lineNum} style={{ height:LINE_HEIGHT }}/>
          return (
            <div key={lineNum} style={{ height:LINE_HEIGHT, background:isFixed?'rgba(16,185,129,0.08)':col.bg, borderLeft:`2px solid ${isFixed?'#10b981':col.border}`, marginLeft:-2, position:'relative' }}>
              {col && !isFixed && <div style={{ position:'absolute', bottom:2, left:0, right:0, height:2, background:`repeating-linear-gradient(90deg,${col.border} 0,${col.border} 4px,transparent 4px,transparent 8px)`, opacity:0.6 }}/>}
            </div>
          )
        })}
      </div>

      {/* Textarea */}
      <textarea
        ref={textareaRef}
        value={code}
        onChange={e => onChange(e.target.value)}
        onScroll={handleScroll}
        onMouseMove={handleMouseMove}
        onMouseLeave={() => setHoveredIssue(null)}
        spellCheck={false}
        style={{ flex:1, background:'transparent', color:'#e1e4e8', border:'none', outline:'none', resize:'none', padding:`${PADDING_TOP}px 18px`, fontFamily:"'JetBrains Mono','Fira Code',monospace", fontSize:12, lineHeight:`${LINE_HEIGHT}px`, position:'relative', zIndex:2, caretColor:'#818cf8', tabSize:2 }}
        placeholder={placeholder}
      />

      {/* Tooltip */}
      {hoveredIssue && (
        <div style={{ position:'fixed', left:Math.min(tooltipPos.x+12, window.innerWidth-320), top:tooltipPos.y+16, zIndex:9999, background:'#1c1f2e', border:`1px solid ${SEV_COLOR[hoveredIssue.issues[0].severity]?.border||'#2d3142'}`, borderRadius:8, padding:'10px 14px', maxWidth:300, boxShadow:'0 8px 32px rgba(0,0,0,0.6)', pointerEvents:'none' }}>
          {hoveredIssue.issues.map((issue,i) => {
            const col = SEV_COLOR[issue.severity] || SEV_COLOR.INFO
            return (
              <div key={i} style={{ marginBottom:i<hoveredIssue.issues.length-1?8:0 }}>
                <div style={{ display:'flex', gap:6, alignItems:'center', marginBottom:4 }}>
                  <span style={{ background:col.bg, color:col.dot, border:`1px solid ${col.border}40`, borderRadius:4, padding:'1px 6px', fontSize:10, fontWeight:700 }}>{issue.severity}</span>
                  <span style={{ color:'#9ca3af', fontSize:10 }}>Line {issue.line}</span>
                </div>
                <div style={{ color:'#e1e4e8', fontSize:12, fontWeight:600, marginBottom:3 }}>{issue.title}</div>
                {issue.suggestion && <div style={{ color:'#6ee7b7', fontSize:11, lineHeight:1.4 }}>💡 {issue.suggestion}</div>}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
