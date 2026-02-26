import { GenUICard } from '../GenUICard'

export function OrderCard({ data }) {
    const { order_id, status } = data
    // Normalize field names: backend returns placed_on, items use qty not quantity
    const date = data.date || data.placed_on
    const items = data.items || []
    const total = data.total || 0

    const statusColors = {
        'delivered': 'var(--accent-sage)',
        'shipped': 'var(--accent-slate)',
        'processing': 'var(--accent-amber)',
        'cancelled': 'var(--accent-rust)',
    }
    const color = statusColors[status?.toLowerCase()] || 'var(--text-secondary)'

    return (
        <GenUICard id={`order-${order_id}`}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
                <div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>
                        Order
                    </div>
                    <div style={{ fontFamily: 'JetBrains Mono', fontSize: '16px', color: 'var(--text-primary)' }}>
                        #{order_id}
                    </div>
                </div>

                <div style={{
                    padding: '4px 12px',
                    borderRadius: '16px',
                    background: `color-mix(in srgb, ${color} 15%, transparent)`,
                    color: color,
                    fontSize: '12px',
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                }}>
                    {status}
                </div>
            </div>

            <div style={{ borderTop: '1px solid rgba(255,255,255,0.05)', borderBottom: '1px solid rgba(255,255,255,0.05)', padding: '16px 0', marginBottom: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {items.map((item, idx) => (
                    <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
                        <div style={{ display: 'flex', gap: '12px' }}>
                            <span style={{ color: 'var(--text-muted)' }}>{item.quantity || item.qty || 1}x</span>
                            <span style={{ color: 'var(--text-secondary)' }}>{item.name}</span>
                        </div>
                        <span style={{ color: 'var(--text-primary)' }}>${(item.price || 0).toFixed(2)}</span>
                    </div>
                ))}
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    Placed on {date ? new Date(date).toLocaleDateString() : '—'}
                </div>
                <div style={{ fontSize: '18px', fontWeight: 600, color: 'var(--text-primary)' }}>
                    Total: ${(total || 0).toFixed(2)}
                </div>
            </div>
        </GenUICard>
    )
}

export function EscalationCard({ data }) {
    const { ticket_id } = data
    // Normalize: backend returns message, not agent_name/issue_summary
    const agent_name = data.agent_name || 'Support Agent'
    const issue_summary = data.issue_summary || data.message || ''
    return (
        <GenUICard id={`escalation-${ticket_id}`}>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '16px' }}>
                <div style={{
                    width: '48px',
                    height: '48px',
                    borderRadius: '50%',
                    background: 'var(--accent-amber)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '24px',
                    flexShrink: 0,
                    boxShadow: '0 0 24px rgba(232, 184, 109, 0.4)'
                }}>
                    🎧
                </div>

                <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '18px', fontWeight: 500, color: 'var(--text-primary)', marginBottom: '4px' }}>
                        Live Agent Connected
                    </div>
                    <div style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '16px' }}>
                        You are now chatting with <span style={{ color: 'var(--accent-amber)' }}>{agent_name}</span>.
                    </div>

                    <div style={{
                        padding: '12px',
                        background: 'rgba(255,255,255,0.03)',
                        borderRadius: '8px',
                        borderLeft: '2px solid var(--accent-amber)',
                        fontSize: '13px',
                        color: 'var(--text-muted)'
                    }}>
                        <div style={{ marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.05em', fontSize: '11px' }}>Context Transferred</div>
                        {issue_summary}
                    </div>
                </div>
            </div>
        </GenUICard>
    )
}

export function TicketCard({ data }) {
    const { ticket_id, issue, priority, status, created_at } = data

    const priorityColors = {
        'urgent': 'var(--accent-rust)',
        'high': 'var(--accent-amber)',
        'medium': 'var(--accent-violet)',
        'low': 'var(--accent-slate)',
    }
    const borderColor = priorityColors[priority?.toLowerCase()] || 'var(--text-secondary)'

    return (
        <GenUICard id={`ticket-${ticket_id}`}>
            <div style={{
                borderLeft: `3px solid ${borderColor}`,
                paddingLeft: '16px',
                background: 'rgba(255,255,255,0.01)',
                borderRadius: '0 8px 8px 0'
            }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                    <div style={{ fontSize: '18px', fontWeight: 500 }}>Support Ticket</div>
                    <div style={{ fontFamily: 'JetBrains Mono', color: 'var(--text-muted)', fontSize: '14px' }}>
                        #{ticket_id}
                    </div>
                </div>

                <div style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '16px', lineHeight: 1.5 }}>
                    {issue}
                </div>

                <div style={{ display: 'flex', gap: '12px', fontSize: '12px' }}>
                    <span style={{
                        background: `color-mix(in srgb, ${borderColor} 15%, transparent)`,
                        color: borderColor,
                        padding: '2px 8px',
                        borderRadius: '12px',
                        textTransform: 'uppercase'
                    }}>
                        {priority} Priority
                    </span>
                    <span style={{ color: 'var(--text-muted)', alignSelf: 'center' }}>
                        • {status} • Created on {created_at ? new Date(created_at).toLocaleDateString() : '—'}
                    </span>
                </div>
            </div>
        </GenUICard>
    )
}

export function KbArticleCard({ data }) {
    const { results, query } = data
    return (
        <GenUICard id={`kb-${query}`}>
            <div style={{ marginBottom: '16px', fontSize: '18px', fontWeight: 500 }}>
                Knowledge Base
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {(results || []).map((article, idx) => (
                    <div key={article.article_id || article.id || idx} style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span style={{ fontSize: '16px', fontWeight: 500, color: 'var(--text-primary)' }}>{article.title}</span>
                            {(article.category || article.id) && (
                                <span style={{
                                    background: 'rgba(255,255,255,0.05)',
                                    color: 'var(--text-muted)',
                                    padding: '2px 8px',
                                    borderRadius: '12px',
                                    fontSize: '11px'
                                }}>
                                    {article.category || article.id}
                                </span>
                            )}
                        </div>
                        <div style={{ color: 'var(--text-secondary)', fontSize: '13px', lineHeight: 1.5 }}>
                            "{article.snippet || article.content}"
                        </div>
                    </div>
                ))}
            </div>
        </GenUICard>
    )
}
