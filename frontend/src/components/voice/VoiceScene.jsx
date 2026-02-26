import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect } from 'react'
import { PlasmaOrb } from './PlasmaOrb'

const phaseLabels = {
    idle: "Ready",
    listening: "Listening...",
    transcribing: "Understanding...",
    thinking: "Thinking...",
    speaking: "Speaking",
    error: "Connection lost",
};

export function VoiceScene({ demoId, isActive, onEndCall }) {
    const [phase, setPhase] = useState('idle')
    const [muted, setMuted] = useState(false)
    const [lastTranscript, setLastTranscript] = useState({ role: 'agent', text: 'Hi, how can I help you today?' })
    const [audioLevel, setAudioLevel] = useState(0)

    // Fast fake audio level simulation
    useEffect(() => {
        if (!isActive || phase === 'thinking' || phase === 'error' || phase === 'idle') {
            setAudioLevel(0)
            return
        }
        const interval = setInterval(() => {
            setAudioLevel(Math.random() * 150 + 50)
        }, 100)
        return () => clearInterval(interval)
    }, [isActive, phase])

    // Fake phase progression for demonstration
    useEffect(() => {
        if (!isActive) return
        let timer1, timer2, timer3
        if (phase === 'listening') {
            timer1 = setTimeout(() => setPhase('transcribing'), 3000)
        } else if (phase === 'transcribing') {
            timer2 = setTimeout(() => {
                setLastTranscript({ role: 'user', text: "Can you help me plan a trip?" })
                setPhase('thinking')
            }, 1500)
        } else if (phase === 'thinking') {
            timer3 = setTimeout(() => {
                setLastTranscript({ role: 'agent', text: "I'd love to help you plan a trip! Where are you thinking of going?" })
                setPhase('speaking')
            }, 2500)
        } else if (phase === 'speaking') {
            timer1 = setTimeout(() => setPhase('idle'), 4000)
        }
        return () => { clearTimeout(timer1); clearTimeout(timer2); clearTimeout(timer3) }
    }, [isActive, phase])


    return (
        <AnimatePresence>
            {isActive && (
                <motion.div
                    initial={{ opacity: 0, backdropFilter: 'blur(0px)' }}
                    animate={{ opacity: 1, backdropFilter: 'blur(40px)' }}
                    exit={{ opacity: 0, backdropFilter: 'blur(0px)' }}
                    transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                    style={{
                        position: 'fixed',
                        inset: 0,
                        zIndex: 100,
                        background: 'var(--bg-overlay)',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                    }}
                >
                    {/* Grain overlay double intensity */}
                    <div style={{ position: 'absolute', inset: 0, filter: 'url(#grain)', opacity: 0.08, pointerEvents: 'none' }} />

                    {/* Top header */}
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 }}
                        style={{ position: 'absolute', top: '48px', textAlign: 'center' }}
                    >
                        <div style={{ color: 'var(--text-muted)', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                            Voice Mode
                        </div>
                        <div style={{ color: 'var(--demo-color)', fontSize: '16px', marginTop: '4px' }}>
                            {demoId}
                        </div>
                        <div className="mono" style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '12px', opacity: 0.5 }}>
                            00:00:24
                        </div>
                    </motion.div>

                    {/* Center Orb */}
                    <div style={{ transform: 'translateY(-40px)' }} onClick={() => setPhase('listening')}>
                        <PlasmaOrb phase={phase} audioLevel={audioLevel} />
                    </div>

                    {/* Phase Label */}
                    <div style={{ marginTop: '48px', height: '24px' }}>
                        <AnimatePresence mode="wait">
                            <motion.div
                                key={phase}
                                initial={{ opacity: 0, letterSpacing: "0.3em" }}
                                animate={{ opacity: 1, letterSpacing: "0.1em" }}
                                exit={{ opacity: 0, y: -8 }}
                                transition={{ duration: 0.4 }}
                                style={{
                                    color: phase === 'listening' ? 'var(--text-primary)' : 'var(--text-secondary)',
                                    fontSize: '14px',
                                    textTransform: 'uppercase',
                                    fontWeight: 500
                                }}
                            >
                                {phaseLabels[phase]}
                            </motion.div>
                        </AnimatePresence>
                    </div>

                    {/* Cinematic Subtitles */}
                    <div style={{
                        position: 'absolute',
                        bottom: '160px',
                        left: '50%',
                        transform: 'translateX(-50%)',
                        maxWidth: '600px',
                        width: '90%',
                        textAlign: 'center',
                    }}>
                        <AnimatePresence mode="wait">
                            <motion.div
                                key={lastTranscript.text}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                transition={{ duration: 0.4 }}
                            >
                                {lastTranscript.role === 'user' ? (
                                    <div style={{ fontSize: '16px', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                                        "{lastTranscript.text}"
                                    </div>
                                ) : (
                                    <div style={{ fontSize: '20px', color: 'var(--demo-color)', lineHeight: 1.5, textShadow: '0 2px 12px rgba(0,0,0,0.5)' }}>
                                        {lastTranscript.text}
                                    </div>
                                )}
                            </motion.div>
                        </AnimatePresence>
                    </div>

                    {/* Call Controls */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.6 }}
                        style={{
                            position: 'absolute',
                            bottom: '48px',
                            left: '50%',
                            transform: 'translateX(-50%)',
                            display: 'flex',
                            gap: '24px',
                            alignItems: 'center',
                        }}
                    >
                        <button
                            onClick={() => setMuted(!muted)}
                            style={{
                                width: '52px', height: '52px', borderRadius: '50%',
                                background: muted ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.1)',
                                border: '1px solid rgba(255,255,255,0.2)',
                                color: 'var(--text-primary)',
                                cursor: 'pointer'
                            }}
                        >
                            {muted ? '🔇' : '🎤'}
                        </button>
                        <button
                            onClick={onEndCall}
                            style={{
                                padding: '12px 32px', borderRadius: '100px',
                                background: 'var(--accent-rust)', color: 'white',
                                fontWeight: 600, border: 'none',
                                cursor: 'pointer',
                                boxShadow: '0 4px 16px rgba(196, 112, 78, 0.4)'
                            }}
                        >
                            End Call
                        </button>
                    </motion.div>

                </motion.div>
            )}
        </AnimatePresence>
    )
}
