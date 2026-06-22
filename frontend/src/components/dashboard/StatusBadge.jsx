const STATUS_MAP = {
  PENDING:          { label: 'Pending',          bg: 'var(--pending-bg)',         color: 'var(--pending-text)' },
  CALL_INITIATED:   { label: 'Call Initiated',   bg: 'var(--initiated-bg)',       color: 'var(--initiated-text)' },
  QUALIFIED:        { label: 'Qualified',         bg: 'var(--qualified-bg)',       color: 'var(--qualified-text)' },
  NOT_INTERESTED:   { label: 'Not Interested',   bg: 'var(--not-interested-bg)',  color: 'var(--not-interested-text)' },
  NEEDS_REVIEW:     { label: 'Needs Review',     bg: 'var(--needs-review-bg)',    color: 'var(--needs-review-text)' },
  FAILED:           { label: 'Failed',            bg: 'var(--failed-bg)',          color: 'var(--failed-text)' },
}

export default function StatusBadge({ status }) {
  const cfg = STATUS_MAP[status] || STATUS_MAP.PENDING

  return (
    <span
      className="animate-fade-in"
      style={{
        display: 'inline-block',
        padding: '2px 10px',
        borderRadius: '999px',
        fontSize: '12px',
        fontWeight: 500,
        background: cfg.bg,
        color: cfg.color,
        whiteSpace: 'nowrap',
      }}
    >
      {cfg.label}
    </span>
  )
}
