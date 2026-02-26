import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'

export function CanvasHUD({ agentState }) {
    const [isExpanded, setIsExpanded] = useState(false)

    return (
        <div style={{
            position: 'fixed',
            bottom: '100px',
            right: '32px',
            zIndex: 50,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'flex-end',
            pointerEvents: 'none' // allow clicking through empty space
        }}>
            <AnimatePresence>
                {isExpanded && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.9, y: 20 }}
                        transition={{ type: "spring", stiffness: 400, damping: 30 }}
                        style={{
                            width: '320px',
                            maxHeight: '60vh',
                            overflowY: 'auto',
                            background: '#00000060',
                            backdropFilter: 'blur(24px) saturate(150%)',
                            border: '1px solid #ffffff0D',
                            borderRadius: '16px',
                            padding: '16px',
                            marginBottom: '16px',
                            fontFamily: 'JetBrains Mono, monospace',
                            fontSize: '11px',
                            color: 'var(--text-secondary)',
                            pointerEvents: 'auto', // enable interactions inside
                            boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
                        }}
                    >
                        <div style={{ marginBottom: '12px', color: 'var(--text-primary)', fontWeight: 600, fontSize: '12px', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '8px' }}>
                            STATE.CANVAS
                        </div>
                        <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                            {agentState?.canvas ? (
                                // Simple syntax highlight via basic string replacement
                                JSON.stringify(agentState.canvas, null, 2)
                                    .replace(/"(.*?)":/g, '<span style="color:var(--accent-amber)">"$1"</span>:')
                            ) : (
                                <span style={{ color: 'var(--text-muted)' }}>No state defined</span>
                            )}
                        </pre>
                    </motion.div>
                )}
            </AnimatePresence>

            <motion.button
                onClick={() => setIsExpanded(!isExpanded)}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                style={{
                    width: '36px',
                    height: '36px',
                    borderRadius: '50%',
                    background: 'rgba(255,255,255,0.05)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    color: 'var(--text-primary)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '16px',
                    cursor: 'pointer',
                    pointerEvents: 'auto',
                    backdropFilter: 'blur(8px)',
                }}
                title="Toggle State Canvas"
            >
                ⊞
            </motion.button>
        </div>
    )
}
