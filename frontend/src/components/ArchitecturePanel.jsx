export default function ArchitecturePanel({ t }) {
  const isVi = t.ragTitle === 'Kho tri thức RAG'
  return (
    <div style={{ padding:20, display:'flex', flexDirection:'column', gap:20 }}>
      <div style={{ background:'#1c1f2e', borderRadius:12, padding:20, border:'1px solid #6366f140' }}>
        <div style={{ color:'#818cf8', fontSize:13, fontWeight:700, textTransform:'uppercase', letterSpacing:1, marginBottom:16 }}>
          🏗️ {isVi ? 'Kiến trúc hệ thống' : 'System Architecture'}
        </div>
        <svg viewBox="0 0 760 340" style={{ width:'100%', height:'auto' }} xmlns="http://www.w3.org/2000/svg">
          <rect x="10" y="130" width="100" height="50" rx="8" fill="#6366f120" stroke="#6366f1" strokeWidth="1.5"/>
          <text x="60" y="150" textAnchor="middle" fill="#818cf8" fontSize="11" fontWeight="600">👤 User</text>
          <text x="60" y="168" textAnchor="middle" fill="#6b7280" fontSize="9">React UI</text>
          <line x1="110" y1="155" x2="155" y2="155" stroke="#2d3142" strokeWidth="1.5" markerEnd="url(#arrow)"/>
          <rect x="155" y="110" width="120" height="90" rx="8" fill="#8b5cf620" stroke="#8b5cf6" strokeWidth="1.5"/>
          <text x="215" y="132" textAnchor="middle" fill="#a78bfa" fontSize="11" fontWeight="600">⚡ FastAPI</text>
          <text x="215" y="148" textAnchor="middle" fill="#6b7280" fontSize="9">POST /api/analyze</text>
          <text x="215" y="163" textAnchor="middle" fill="#6b7280" fontSize="9">GET /health</text>
          <text x="215" y="178" textAnchor="middle" fill="#6b7280" fontSize="9">GET /languages</text>
          <line x1="275" y1="155" x2="320" y2="155" stroke="#2d3142" strokeWidth="1.5" markerEnd="url(#arrow)"/>
          <rect x="320" y="90" width="130" height="130" rx="8" fill="#ec489920" stroke="#ec4899" strokeWidth="1.5"/>
          <text x="385" y="112" textAnchor="middle" fill="#f472b6" fontSize="11" fontWeight="600">🧠 AI Agent</text>
          <text x="385" y="128" textAnchor="middle" fill="#6b7280" fontSize="9">LLaMA 3.3 70B</text>
          <text x="385" y="157" textAnchor="middle" fill="#f59e0b" fontSize="9">🔧 Tool 1: Static</text>
          <text x="385" y="171" textAnchor="middle" fill="#f59e0b" fontSize="9">🔧 Tool 2: RAG Search</text>
          <text x="385" y="185" textAnchor="middle" fill="#f59e0b" fontSize="9">🔧 Tool 3: Test Pattern</text>
          <text x="385" y="199" textAnchor="middle" fill="#6b7280" fontSize="8">Function Calling Loop</text>
          <line x1="385" y1="220" x2="300" y2="265" stroke="#2d3142" strokeWidth="1.5" markerEnd="url(#arrow)"/>
          <line x1="385" y1="220" x2="490" y2="265" stroke="#2d3142" strokeWidth="1.5" markerEnd="url(#arrow)"/>
          <line x1="450" y1="155" x2="495" y2="155" stroke="#2d3142" strokeWidth="1.5" markerEnd="url(#arrow)"/>
          <rect x="230" y="265" width="130" height="55" rx="8" stroke="#f97316" strokeWidth="1.5" fill="#f9731615"/>
          <text x="295" y="287" textAnchor="middle" fill="#fb923c" fontSize="11" fontWeight="600">🔧 Static Analyzer</text>
          <text x="295" y="302" textAnchor="middle" fill="#6b7280" fontSize="9">pylint + regex rules</text>
          <text x="295" y="314" textAnchor="middle" fill="#6b7280" fontSize="9">Python & Java</text>
          <rect x="390" y="265" width="130" height="55" rx="8" stroke="#f59e0b" strokeWidth="1.5" fill="#f59e0b15"/>
          <text x="455" y="287" textAnchor="middle" fill="#fbbf24" fontSize="11" fontWeight="600">📚 FAISS RAG</text>
          <text x="455" y="302" textAnchor="middle" fill="#6b7280" fontSize="9">27 docs • 128-dim</text>
          <text x="455" y="314" textAnchor="middle" fill="#6b7280" fontSize="9">Trigram embedding</text>
          <rect x="540" y="110" width="120" height="90" rx="8" fill="#10b98120" stroke="#10b981" strokeWidth="1.5"/>
          <text x="600" y="132" textAnchor="middle" fill="#34d399" fontSize="11" fontWeight="600">⚡ Groq API</text>
          <text x="600" y="148" textAnchor="middle" fill="#6b7280" fontSize="9">llama-3.3-70b</text>
          <text x="600" y="163" textAnchor="middle" fill="#6b7280" fontSize="9">Function Calling</text>
          <text x="600" y="178" textAnchor="middle" fill="#6b7280" fontSize="9">~1-3s latency</text>
          <line x1="540" y1="155" x2="495" y2="155" stroke="#10b981" strokeWidth="1.5" strokeDasharray="4,2"/>
          <rect x="660" y="110" width="90" height="90" rx="8" fill="#6366f120" stroke="#6366f1" strokeWidth="1.5"/>
          <text x="705" y="132" textAnchor="middle" fill="#818cf8" fontSize="11" fontWeight="600">📋 Output</text>
          <text x="705" y="148" textAnchor="middle" fill="#6b7280" fontSize="9">JSON Review</text>
          <text x="705" y="163" textAnchor="middle" fill="#6b7280" fontSize="9">Test Cases</text>
          <text x="705" y="178" textAnchor="middle" fill="#6b7280" fontSize="9">Score + Analytics</text>
          <line x1="660" y1="155" x2="615" y2="155" stroke="#2d3142" strokeWidth="1.5" markerEnd="url(#arrowLeft)"/>
          <defs>
            <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#4b5563"/></marker>
            <marker id="arrowLeft" markerWidth="8" markerHeight="8" refX="2" refY="3" orient="auto"><path d="M8,0 L8,6 L0,3 z" fill="#4b5563"/></marker>
          </defs>
        </svg>
      </div>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:12 }}>
        {[
          { layer:isVi?'🖥️ Giao diện':'🖥️ Frontend', items:['React 18 + Vite','Axios HTTP client','i18n (EN/VI)','localStorage history'], color:'#6366f1' },
          { layer:'⚙️ Backend', items:['Python 3.12','FastAPI + Uvicorn','python-dotenv','asyncio timeout'], color:'#8b5cf6' },
          { layer:isVi?'🤖 AI & Dữ liệu':'🤖 AI & Data', items:['Groq LLaMA 3.3 70B','FAISS vector search','Function Calling','27 KB documents'], color:'#ec4899' },
        ].map(s=>(
          <div key={s.layer} style={{ background:'#13161f', borderRadius:10, padding:16, border:`1px solid ${s.color}30` }}>
            <div style={{ color:s.color, fontWeight:700, fontSize:13, marginBottom:10 }}>{s.layer}</div>
            {s.items.map(item=>(<div key={item} style={{ display:'flex', alignItems:'center', gap:6, marginBottom:6 }}><span style={{ color:s.color, fontSize:10 }}>▸</span><span style={{ color:'#9ca3af', fontSize:12 }}>{item}</span></div>))}
          </div>
        ))}
      </div>
      <div style={{ background:'#1c1f2e', borderRadius:12, padding:20, border:'1px solid #2d3142' }}>
        <div style={{ color:'#9ca3af', fontSize:12, fontWeight:600, textTransform:'uppercase', letterSpacing:1, marginBottom:14 }}>API Endpoints</div>
        {[
          { method:'POST', path:'/api/analyze', desc:isVi?'Phân tích code — Review + Test generation':'Analyze code — Review + Test generation', color:'#10b981' },
          { method:'GET',  path:'/health',      desc:isVi?'Kiểm tra trạng thái server':'Server health check', color:'#6366f1' },
          { method:'GET',  path:'/api/languages', desc:isVi?'Danh sách ngôn ngữ hỗ trợ':'Supported languages', color:'#6366f1' },
        ].map(api=>(
          <div key={api.path} style={{ display:'flex', alignItems:'center', gap:10, background:'#13161f', borderRadius:6, padding:'10px 14px', marginBottom:8, border:'1px solid #2d3142' }}>
            <span style={{ background:api.color+'20', color:api.color, borderRadius:4, padding:'2px 8px', fontSize:11, fontWeight:700, flexShrink:0 }}>{api.method}</span>
            <code style={{ color:'#818cf8', fontSize:12, flex:1 }}>{api.path}</code>
            <span style={{ color:'#6b7280', fontSize:12 }}>{api.desc}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
