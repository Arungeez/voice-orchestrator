export default function Sidebar({ companies, activeCompanyId, onSelect, activeTab, onTabChange, wsConnected }) {
  return (
    <aside style={{
      width: 240,
      minHeight: '100vh',
      background: 'var(--bg-sidebar)',
      borderRight: '1px solid var(--border-default)',
      display: 'flex',
      flexDirection: 'column',
      flexShrink: 0,
    }}>
      {/* Logo */}
      <div style={{
        padding: '20px 18px 16px',
        borderBottom: '1px solid var(--border-default)',
      }}>
        <div style={{ fontWeight: 700, fontSize: 16, color: 'var(--text-primary)', letterSpacing: '-0.3px' }}>
          VoiceOrch
        </div>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
          AI Lead Qualification
        </div>
      </div>

      {/* Companies */}
      <div style={{ padding: '14px 0 8px' }}>
        <div style={{
          padding: '0 18px 8px',
          fontSize: 11,
          fontWeight: 600,
          color: 'var(--text-muted)',
          textTransform: 'uppercase',
          letterSpacing: '0.06em',
        }}>
          Companies
        </div>
        {companies.map(company => {
          const isActive = company._id === activeCompanyId
          return (
            <button
              key={company._id}
              onClick={() => onSelect(company._id)}
              style={{
                width: '100%',
                padding: '9px 18px',
                textAlign: 'left',
                background: isActive ? 'var(--accent-light)' : 'transparent',
                border: 'none',
                borderLeft: isActive ? '3px solid var(--accent)' : '3px solid transparent',
                cursor: 'pointer',
                fontSize: 13,
                fontWeight: isActive ? 600 : 400,
                color: isActive ? 'var(--accent)' : 'var(--text-secondary)',
                transition: 'all 0.1s ease',
                fontFamily: 'inherit',
              }}
              onMouseEnter={e => { if (!isActive) e.currentTarget.style.background = 'var(--bg-hover)' }}
              onMouseLeave={e => { if (!isActive) e.currentTarget.style.background = 'transparent' }}
            >
              {company.name}
              <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 400, marginTop: 1 }}>
                {company.industry}
              </div>
            </button>
          )
        })}
      </div>

      {/* Nav */}
      <div style={{ padding: '8px 0', borderTop: '1px solid var(--border-default)', marginTop: 8 }}>
        <div style={{
          padding: '0 18px 8px',
          fontSize: 11,
          fontWeight: 600,
          color: 'var(--text-muted)',
          textTransform: 'uppercase',
          letterSpacing: '0.06em',
        }}>
          Navigation
        </div>
        {['Dashboard', 'Logs'].map(tab => {
          const isActive = activeTab === tab
          return (
            <button
              key={tab}
              onClick={() => onTabChange(tab)}
              style={{
                width: '100%',
                padding: '9px 18px',
                textAlign: 'left',
                background: isActive ? 'var(--bg-hover)' : 'transparent',
                border: 'none',
                borderLeft: isActive ? '3px solid var(--border-strong)' : '3px solid transparent',
                cursor: 'pointer',
                fontSize: 13,
                color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                fontWeight: isActive ? 500 : 400,
                transition: 'all 0.1s ease',
                fontFamily: 'inherit',
              }}
              onMouseEnter={e => { if (!isActive) e.currentTarget.style.background = 'var(--bg-hover)' }}
              onMouseLeave={e => { if (!isActive) e.currentTarget.style.background = 'transparent' }}
            >
              {tab}
            </button>
          )
        })}
      </div>

      {/* WS Status */}
      <div style={{ marginTop: 'auto', padding: '14px 18px', borderTop: '1px solid var(--border-default)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
          <div style={{
            width: 7, height: 7, borderRadius: '50%',
            background: wsConnected ? '#10B981' : '#D1D5DB',
          }} />
          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
            {wsConnected ? 'Live updates on' : 'Connecting...'}
          </span>
        </div>
      </div>
    </aside>
  )
}
