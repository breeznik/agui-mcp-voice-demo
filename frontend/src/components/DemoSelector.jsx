import { motion } from 'framer-motion'
import { useState } from 'react'

export const DEMOS = {
    travel: { label: "Travel Concierge", color: "#6E8FA8", icon: "✈", tagline: "Plan trips with AI + live data" },
    trivia: { label: "Trivia Host", color: "#9B7EC8", icon: "🎯", tagline: "Interactive quiz with score tracking" },
    shopping: { label: "Shopping Assistant", color: "#C4704E", icon: "◈", tagline: "Search products, manage cart" },
    chef: { label: "Personal Chef", color: "#7AA88A", icon: "◉", tagline: "Recipes, nutrition, meal planning" },
    support: { label: "Customer Support", color: "#A89E92", icon: "◎", tagline: "Orders, refunds, live escalation" },
}

export function DemoSelector({ onSelectDemo }) {
    const [hoveredDemo, setHoveredDemo] = useState(null)

    const activeColor = hoveredDemo ? DEMOS[hoveredDemo].color : 'var(--accent-amber)'

    return (
        <motion.div
            className="scene-landing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.8 }}
            style={{
                position: 'fixed',
                inset: 0,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 10,
            }}
        >
            {/* Ambient background glow */}
            <motion.div
                className="ambient-glow"
                animate={{
                    background: `radial-gradient(circle at 50% 50%, ${activeColor}15 0%, transparent 60%)`,
                }}
                transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                style={{
                    position: 'absolute',
                    inset: 0,
                    pointerEvents: 'none',
                    zIndex: -1,
                }}
            />

            <div style={{ marginBottom: '64px', textAlign: 'center' }}>
                <h1 style={{ fontSize: '24px', fontWeight: 500, letterSpacing: '0.05em', color: 'var(--text-secondary)' }}>
                    agui · mcp · voice
                </h1>
            </div>

            <div className="grid-2-col" style={{
                gap: '24px',
                maxWidth: '800px',
            }}>
                {Object.entries(DEMOS).map(([id, demo]) => (
                    <motion.button
                        key={id}
                        onClick={() => onSelectDemo(id)}
                        onHoverStart={() => setHoveredDemo(id)}
                        onHoverEnd={() => setHoveredDemo(null)}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '16px',
                            textAlign: 'left',
                            padding: '12px 24px',
                            borderRadius: '8px',
                            color: hoveredDemo === id ? demo.color : 'var(--text-primary)',
                            transition: 'color 0.3s ease',
                        }}
                        whileHover={{ x: 8 }}
                    >
                        <span style={{ fontSize: '20px', opacity: 0.8 }}>{demo.icon}</span>
                        <div>
                            <div style={{ fontSize: '18px', fontWeight: 500 }}>{demo.label}</div>
                            <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>
                                {demo.tagline}
                            </div>
                        </div>
                    </motion.button>
                ))}
            </div>

            <div style={{ marginTop: '80px', color: 'var(--text-muted)', fontSize: '14px', fontStyle: 'italic' }}>
                [Select a world to enter →]
            </div>
        </motion.div>
    )
}
