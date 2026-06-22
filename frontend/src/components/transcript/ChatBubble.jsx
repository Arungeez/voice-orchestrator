export default function ChatBubble({ role, content }) {
  const isAssistant = role === 'assistant'

  return (
    <div style={{
      display: 'flex',
      justifyContent: isAssistant ? 'flex-start' : 'flex-end',
      marginBottom: 10,
    }}>
      <div style={{
        maxWidth: '80%',
        padding: '8px 12px',
        borderRadius: isAssistant ? '4px 12px 12px 12px' : '12px 4px 12px 12px',
        background: isAssistant ? 'var(--bg-app)' : 'var(--accent-light)',
        borderLeft: isAssistant ? '3px solid var(--border-strong)' : 'none',
        borderRight: isAssistant ? 'none' : '3px solid var(--accent)',
        fontSize: 13,
        lineHeight: 1.5,
        color: 'var(--text-primary)',
      }}>
        <div style={{
          fontSize: 10,
          fontWeight: 600,
          color: 'var(--text-muted)',
          marginBottom: 4,
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
        }}>
          {isAssistant ? 'AI Assistant' : 'Lead'}
        </div>
        {content}
      </div>
    </div>
  )
}
