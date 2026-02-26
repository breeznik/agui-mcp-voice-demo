import { motion } from 'framer-motion'

// Seeded rotation generator based on a string input
function seedRotation(str, min = -1.5, max = 1.5) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    const random = Math.abs(Math.sin(hash))
    return min + random * (max - min)
}

export function ToolCallStamp({ toolName, args, status }) {
    // Rotate slightly to look like a hand-pressed stamp
    const rotateAttr = seedRotation(toolName, -1.5, 1.5)

    return (
        <motion.div
            className="tool-stamp"
            initial={{ opacity: 0, scale: 0.92, rotate: -1 }}
            animate={{ opacity: 1, scale: 1, rotate: rotateAttr }}
            style={{
                display: 'inline-flex',
                flexDirection: 'column',
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(255,255,255,0.05)',
                borderRadius: '8px',
                padding: '8px 12px',
                margin: '4px 0',
                maxWidth: '420px',
                fontSize: 'var(--text-sm)',
                color: 'var(--text-secondary)',
            }}
        >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ color: 'var(--text-muted)' }}>⬡</span>
                <span className="mono">{toolName}</span>
                <span style={{
                    marginLeft: 'auto',
                    color: status === "done" ? 'var(--accent-sage)' : 'var(--text-muted)'
                }}>
                    {status === "done" ? "✓" : "..."}
                </span>
            </div>

            {args && (
                <motion.pre
                    className="mono"
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    style={{
                        fontSize: 'var(--text-xs)',
                        color: 'var(--text-muted)',
                        overflow: 'hidden',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-all',
                        marginTop: '8px',
                        paddingTop: '8px',
                        borderTop: '1px solid rgba(255,255,255,0.05)'
                    }}
                >
                    {typeof args === 'string' ? args : JSON.stringify(args, null, 2)}
                </motion.pre>
            )}
        </motion.div>
    )
}
