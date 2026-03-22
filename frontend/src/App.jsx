import { useState } from 'react'
import axios from 'axios'
import CodeReviewPanel from './components/CodeReviewPanel.jsx'
import TestGenPanel from './components/TestGenPanel.jsx'

const SAMPLE_PYTHON = `import sqlite3

def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Vulnerable to SQL injection
    query = "SELECT * FROM users WHERE id = " + str(user_id)
    cursor.execute(query)
    result = cursor.fetchone()
    return result

def authenticate(username, password):
    # Hardcoded password - never do this!
    admin_password = "admin123"
    if password == admin_password:
        return True
    try:
        user = get_user(username)
        return user is not None
    except:
        pass

def process_data(items):
    result = ""
    for item in items:
        result += str(item) + ","
    print("Processed: " + result)
    return result
`

const SAMPLE_JAVA = `import java.sql.*;
import java.util.List;

public class UserService {
    private static final String PASSWORD = "secret123";

    public Object findUser(String userId) {
        try {
            Connection conn = DriverManager.getConnection("jdbc:mysql://localhost/db");
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery("SELECT * FROM users WHERE id = " + userId);
            if (rs.next()) {
                return rs.getString("name");
            }
        } catch (Exception e) {
            // Empty catch block
        }
        return null;
    }

    public String buildReport(List<String> items) {
        String result = "";
        for (String item : items) {
            result += item + ", ";
        }
        System.out.println("Report: " + result);
        return result;
    }
}
`

export default function App() {
  const [code, setCode] = useState(SAMPLE_PYTHON)
  const [language, setLanguage] = useState('python')
  const [mode, setMode] = useState('both')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('review')

  const handleAnalyze = async () => {
    if (!code.trim()) return
    setLoading(true); setError(null); setResult(null)
    try {
      const res = await axios.post('/api/analyze', { code, language, mode })
      setResult(res.data)
      setActiveTab(mode === 'test' ? 'tests' : 'review')
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const loadSample = (lang) => {
    setLanguage(lang)
    setCode(lang === 'python' ? SAMPLE_PYTHON : SAMPLE_JAVA)
    setResult(null)
  }

  const scoreColor = result?.review ? (result.review.score >= 80 ? '#10b981' : result.review.score >= 60 ? '#f59e0b' : '#ef4444') : '#6366f1'

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Header */}
      <header style={{ background: 'linear-gradient(135deg,#1a1d27,#12151e)', borderBottom: '1px solid #2d3142', padding: '14px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ background: 'linear-gradient(135deg,#6366f1,#8b5cf6)', borderRadius: 10, padding: '7px 10px', fontSize: 20 }}>🧠</div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 18, color: '#fff' }}>Code Intelligence Worker</div>
            <div style={{ fontSize: 12, color: '#6b7280' }}>AI-Powered Code Review & Test Generation</div>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {[['#6366f1','AI Agent'],['#10b981','RAG'],['#f59e0b','Function Calling']].map(([c,l]) => (
            <span key={l} style={{ background: c+'20', border:`1px solid ${c}40`, color:c, borderRadius:20, padding:'3px 10px', fontSize:11, fontWeight:600 }}>{l}</span>
          ))}
        </div>
      </header>

      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Left — Input */}
        <div style={{ width: '42%', display: 'flex', flexDirection: 'column', borderRight: '1px solid #2d3142', background: '#13161f' }}>
          <div style={{ padding: '14px 18px', borderBottom: '1px solid #2d3142', display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
            {['python','java'].map(lang => (
              <button key={lang} onClick={() => loadSample(lang)} style={{ padding:'6px 14px', borderRadius:6, border:'1px solid', borderColor: language===lang?'#6366f1':'#2d3142', background: language===lang?'#6366f115':'transparent', color: language===lang?'#818cf8':'#9ca3af', cursor:'pointer', fontSize:12, fontWeight:600, textTransform:'uppercase', letterSpacing:1 }}>{lang}</button>
            ))}
            <select value={mode} onChange={e=>setMode(e.target.value)} style={{ background:'#1c1f2e', border:'1px solid #2d3142', color:'#e1e4e8', borderRadius:6, padding:'6px 10px', fontSize:13, cursor:'pointer' }}>
              <option value="both">Review + Tests</option>
              <option value="review">Review Only</option>
              <option value="test">Tests Only</option>
            </select>
            <button onClick={handleAnalyze} disabled={loading} style={{ marginLeft:'auto', padding:'7px 20px', borderRadius:6, border:'none', background: loading?'#374151':'linear-gradient(135deg,#6366f1,#8b5cf6)', color:'#fff', cursor: loading?'not-allowed':'pointer', fontWeight:600, fontSize:14, display:'flex', alignItems:'center', gap:8 }}>
              {loading ? '⏳ Analyzing...' : '⚡ Analyze'}
            </button>
          </div>
          <textarea value={code} onChange={e=>setCode(e.target.value)} spellCheck={false} style={{ flex:1, background:'#0d1117', color:'#e1e4e8', border:'none', outline:'none', padding:'16px 20px', fontFamily:"'JetBrains Mono','Fira Code',monospace", fontSize:13, lineHeight:1.7, resize:'none', tabSize:2 }} placeholder="Paste your code here..." />
        </div>

        {/* Right — Results */}
        <div style={{ flex:1, display:'flex', flexDirection:'column', overflow:'hidden' }}>
          {!result && !loading && !error && (
            <div style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:16, color:'#4b5563' }}>
              <div style={{ fontSize:64 }}>🤖</div>
              <div style={{ fontSize:20, color:'#6b7280', fontWeight:600 }}>Ready to analyze your code</div>
              <div style={{ fontSize:14, textAlign:'center', maxWidth:320, lineHeight:1.6, color:'#4b5563' }}>
                Paste your code on the left, select language and mode, then click <strong style={{color:'#818cf8'}}>⚡ Analyze</strong>
              </div>
            </div>
          )}
          {loading && (
            <div style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:20 }}>
              <div style={{ fontSize:48 }}>⚡</div>
              <div style={{ color:'#818cf8', fontWeight:600, fontSize:16 }}>Analyzing your code...</div>
              {['🔧 Running static analysis...','📚 Searching knowledge base (RAG)...','🧠 AI agent synthesizing results...'].map((s,i)=>(
                <div key={i} style={{ background:'#1c1f2e', border:'1px solid #2d3142', borderRadius:8, padding:'10px 20px', color:'#9ca3af', fontSize:13 }}>{s}</div>
              ))}
            </div>
          )}
          {error && <div style={{ padding:24 }}><div style={{ background:'#2d1515', border:'1px solid #ef4444', borderRadius:8, padding:16, color:'#fca5a5' }}>❌ {error}</div></div>}
          {result && (
            <>
              <div style={{ display:'flex', borderBottom:'1px solid #2d3142', background:'#13161f', padding:'0 20px' }}>
                {result.review && (
                  <button onClick={()=>setActiveTab('review')} style={{ padding:'12px 20px', border:'none', borderBottom: activeTab==='review'?'2px solid #6366f1':'2px solid transparent', background:'transparent', color: activeTab==='review'?'#818cf8':'#6b7280', cursor:'pointer', fontSize:14, fontWeight: activeTab==='review'?600:400, display:'flex', alignItems:'center', gap:8 }}>
                    🔍 Code Review
                    <span style={{ background:scoreColor+'30', color:scoreColor, borderRadius:10, padding:'1px 7px', fontSize:11, fontWeight:700 }}>{result.review.issues?.length ?? 0}</span>
                  </button>
                )}
                {result.tests && (
                  <button onClick={()=>setActiveTab('tests')} style={{ padding:'12px 20px', border:'none', borderBottom: activeTab==='tests'?'2px solid #6366f1':'2px solid transparent', background:'transparent', color: activeTab==='tests'?'#818cf8':'#6b7280', cursor:'pointer', fontSize:14, fontWeight: activeTab==='tests'?600:400, display:'flex', alignItems:'center', gap:8 }}>
                    🧪 Test Cases
                    <span style={{ background:'#10b98130', color:'#10b981', borderRadius:10, padding:'1px 7px', fontSize:11, fontWeight:700 }}>{result.tests.test_cases?.length ?? 0}</span>
                  </button>
                )}
              </div>
              <div style={{ flex:1, overflow:'auto' }}>
                {activeTab==='review' && result.review && <CodeReviewPanel review={result.review} />}
                {activeTab==='tests' && result.tests && <TestGenPanel tests={result.tests} language={result.language} />}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
