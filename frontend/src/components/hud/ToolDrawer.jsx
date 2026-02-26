import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect } from 'react'

export function ToolDrawer({ baseUrl, demoId, isOpen, onClose }) {
    const [tools, setTools] = useState([])
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        if (isOpen && tools.length === 0) {
            setLoading(true)
            // Fake fetch since we don't know the exact endpoint response format yet
            // Replace with actual: fetch(`${baseUrl}/agent/${demoId}/tools`)
            setTimeout(() => {
                setTools([
                    { name: 'search_flights', description: 'Search for live flights by origin, destination, and dates.' },
                    { name: 'book_hotel', description: 'Complete a booking transaction for a specific hotel ID.' },
                    { name: 'get_weather_forecast', description: 'Retrieve 5-day weather data for a location.' },
                    { name: 'calendar_availability', description: 'Check user calendar for trip planning.' }
                ])
                setLoading(false)
            }, 800)
        }
    }, [isOpen, tools.length, baseUrl, demoId])

    return (
        <>
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        style={{
                            position: 'fixed',
                            inset: 0,
                            background: 'rgba(0,0,0,0.4)',
                            backdropFilter: 'blur(2px)',
                            zIndex: 40,
                        }}
                    />
                )}
            </AnimatePresence>

            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ x: '100%' }}
                        animate={{ x: 0 }}
                        exit={{ x: '100%' }}
                        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                        style={{
                            position: 'fixed',
                            top: 0,
                            bottom: 0,
                            right: 0,
                            width: '360px',
                            background: 'var(--bg-elevated)',
                            borderLeft: '1px solid rgba(255,255,255,0.05)',
                            zIndex: 50,
                            display: 'flex',
                            flexDirection: 'column',
                            boxShadow: '-8px 0 32px rgba(0,0,0,0.5)',
                        }}
                    >
                        {/* Grain overlay */}
                        <div style={{ position: 'absolute', inset: 0, filter: 'url(#grain)', opacity: 0.05, pointerEvents: 'none' }} />

                        <div style={{ padding: '24px', borderBottom: '1px solid rgba(255,255,255,0.1)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', zIndex: 1 }}>
                            <div style={{ fontSize: '18px', fontWeight: 500, letterSpacing: '0.05em', textTransform: 'uppercase' }}>MCP Catalog</div>
                            <button onClick={onClose} style={{ color: 'var(--text-muted)' }}>✕</button>
                        </div>

                        <div style={{ flex: 1, overflowY: 'auto', padding: '24px', zIndex: 1, display: 'flex', flexDirection: 'column', gap: '16px' }}>
                            {loading ? (
                                <div style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Loading tools...</div>
                            ) : (
                                tools.map((t, idx) => (
                                    <div key={idx} style={{
                                        padding: '16px',
                                        background: 'rgba(255,255,255,0.03)',
                                        borderRadius: '8px',
                                        border: '1px solid rgba(255,255,255,0.05)'
                                    }}>
                                        <div className="mono" style={{ color: 'var(--accent-amber)', fontSize: '13px', marginBottom: '8px' }}>
                                            {t.name}
                                        </div>
                                        <div style={{ color: 'var(--text-secondary)', fontSize: '13px', lineHeight: 1.5 }}>
                                            {t.description}
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    )
}
