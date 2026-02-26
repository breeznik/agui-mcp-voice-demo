import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useCustomAgent } from '../hooks/useCustomAgent'
import { CARD_REGISTRY } from './ComponentRegistry'
import { ToolCallStamp } from './ToolCallStamp'
import { CanvasHUD } from './hud/CanvasHUD'
import { ToolDrawer } from './hud/ToolDrawer'
import { VoiceScene } from './voice/VoiceScene'

const BASE_URL = import.meta.env.VITE_AGENT_BASE_URL || 'http://localhost:8000'

const STARTER_PROMPTS = {
    travel: [
        "Plan a 7-day trip to Tokyo for 2 people in June",
        "Find flights from London to Bali next month",
        "What's the weather like in Paris this weekend?",
    ],
    trivia: [
        "Start a science trivia quiz on medium difficulty",
        "Give me 5 geography questions",
        "What categories are available?",
    ],
    shopping: [
        "Find me a mechanical keyboard under $150",
        "What's in my cart?",
        "Show me wireless headphones with the best ratings",
    ],
    chef: [
        "Find vegan Italian recipes I can make in 30 minutes",
        "Plan my meals for the next 5 days",
        "What are the macros for pasta carbonara?",
    ],
    support: [
        "Check the status of order ORD-A1B2C3",
        "I need a refund for my last order",
        "How do I return a damaged item?",
    ],
};

export function DemoView({ demoId, demoConfig, onBack }) {
    const [input, setInput] = useState('')
    const [isToolDrawerOpen, setIsToolDrawerOpen] = useState(false)
    const [isVoiceActive, setIsVoiceActive] = useState(false)

    const { messages, toolCalls, agentState, isRunning, activity, send } = useCustomAgent({
        baseUrl: BASE_URL,
        demoId: demoId
    })

    const handleSend = (e) => {
        e.preventDefault()
        if (!input.trim() || isRunning) return
        send(input)
        setInput('')
    }

    // Update body --demo-color
    useEffect(() => {
        document.documentElement.style.setProperty('--demo-color', demoConfig.color)
        return () => {
            document.documentElement.style.setProperty('--demo-color', 'var(--accent-amber)')
        }
    }, [demoConfig])

    return (
        <motion.div
            className="scene-demo"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            style={{
                position: 'fixed',
                inset: 0,
                display: 'flex',
                flexDirection: 'column',
            }}
        >
            {/* Huge Demo Watermark */}
            <motion.div
                className="demo-watermark"
                animate={{ opacity: [0.02, 0.05, 0.02] }}
                transition={{ repeat: Infinity, duration: 6, ease: "easeInOut" }}
                style={{
                    position: 'fixed',
                    inset: 0,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 'clamp(80px, 18vw, 200px)',
                    fontWeight: 600,
                    letterSpacing: '-0.04em',
                    color: 'var(--demo-color)',
                    pointerEvents: 'none',
                    userSelect: 'none',
                    textTransform: 'uppercase',
                    zIndex: -1,
                }}
            >
                {demoId}
            </motion.div>

            {/* Top HUD */}
            <div style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                padding: '24px 32px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                zIndex: 10,
            }}>
                {/* Left tabs (Demo Switcher) */}
                <div style={{ display: 'flex', gap: '24px' }}>
                    <button
                        onClick={onBack}
                        style={{ color: 'var(--text-muted)', fontSize: '14px', marginRight: '16px' }}
                    >
                        ← Back
                    </button>
                    <div style={{
                        color: 'var(--demo-color)',
                        fontSize: '14px',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                        borderBottom: '2px solid var(--demo-color)',
                        paddingBottom: '4px'
                    }}>
                        {demoId}
                    </div>
                </div>

                {/* Right controls */}
                <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                    {/* Tool Drawer trigger */}
                    <button
                        onClick={() => setIsToolDrawerOpen(true)}
                        style={{ color: 'var(--text-muted)', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.05em' }}
                    >
                        MCP ↗
                    </button>

                    {/* Voice Button */}
                    <button
                        onClick={() => setIsVoiceActive(true)}
                        style={{
                            width: '40px',
                            height: '40px',
                            borderRadius: '50%',
                            background: 'rgba(255,255,255,0.05)',
                            border: '1px solid rgba(255,255,255,0.1)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'var(--text-secondary)',
                            cursor: 'pointer'
                        }}
                    >
                        🎤
                    </button>
                </div>
            </div>

            {/* Chat Thread */}
            <div style={{
                flex: 1,
                overflowY: 'auto',
                overflowX: 'hidden',
                paddingTop: '100px',
                paddingBottom: '140px', // clearance for input
                scrollBehavior: 'smooth',
            }}>
                {/* Activity Strip */}
                <AnimatePresence>
                    {activity && (
                        <motion.div
                            initial={{ opacity: 0, y: -8 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -8 }}
                            style={{
                                position: 'fixed',
                                top: '90px',
                                left: '50%',
                                transform: 'translateX(-50%)',
                                background: 'rgba(255,255,255,0.06)',
                                backdropFilter: 'blur(8px)',
                                padding: '8px 16px',
                                borderRadius: '24px',
                                border: '1px solid rgba(255,255,255,0.1)',
                                display: 'flex',
                                gap: '12px',
                                alignItems: 'center',
                                fontSize: '13px',
                                zIndex: 15,
                                maxWidth: 'calc(100vw - 32px)',
                                width: 'fit-content'
                            }}
                        >
                            <span style={{
                                color: activity.phase === 'search' ? 'var(--accent-slate)' :
                                    activity.phase === 'mcp' ? 'var(--accent-amber)' :
                                        activity.phase === 'thinking' ? 'var(--text-secondary)' :
                                            activity.phase === 'done' ? 'var(--accent-sage)' : 'var(--text-secondary)',
                                fontWeight: 600,
                                textTransform: 'uppercase',
                                letterSpacing: '0.05em',
                                fontSize: '11px',
                                flexShrink: 0
                            }}>
                                {activity.phase}
                            </span>
                            <span style={{
                                color: 'var(--text-primary)',
                                whiteSpace: 'nowrap',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis'
                            }}>{activity.title}</span>
                            {activity.detail && <span style={{
                                color: 'var(--text-muted)',
                                whiteSpace: 'nowrap',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis'
                            }}>{activity.detail}</span>}
                        </motion.div>
                    )}
                </AnimatePresence>

                <div style={{
                    width: '100%',
                    maxWidth: '680px',
                    margin: '0 auto',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '24px',
                    padding: '0 24px',
                }}>
                    {messages.map((msg) => {
                        if (msg.role === 'tool_stamp') {
                            const tc = toolCalls[msg.toolCallId]
                            if (!tc) return null
                            return <ToolCallStamp key={msg.id} toolName={tc.name} args={tc.args} status={tc.status} />
                        }
                        if (msg.role === 'card') {
                            const Component = CARD_REGISTRY[msg.cardType]
                            if (!Component) {
                                console.warn('Unknown card type:', msg.cardType)
                                return null
                            }
                            // Pass a simulated onAnswer callback for Trivia cards
                            return <Component key={msg.id} data={msg.cardData} onAnswer={(ans) => send(ans)} />
                        }
                        return (
                            <div
                                key={msg.id}
                                className={`message-${msg.role}`}
                                style={{
                                    alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                                    textAlign: msg.role === 'user' ? 'right' : 'left',
                                    color: msg.role === 'user' ? 'var(--text-primary)' : 'var(--demo-color)',
                                    fontSize: 'var(--text-base)',
                                    maxWidth: msg.role === 'user' ? '520px' : '580px',
                                    padding: '12px 0',
                                    lineHeight: 1.7,
                                }}
                            >
                                {msg.role === 'assistant' ? (
                                    <ReactMarkdown
                                        remarkPlugins={[remarkGfm]}
                                        components={{
                                            p: ({ children }) => <p style={{ margin: '0 0 8px 0' }}>{children}</p>,
                                            strong: ({ children }) => <strong style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{children}</strong>,
                                            h1: ({ children }) => <h1 style={{ fontSize: '20px', fontWeight: 600, margin: '12px 0 8px', color: 'var(--text-primary)' }}>{children}</h1>,
                                            h2: ({ children }) => <h2 style={{ fontSize: '17px', fontWeight: 600, margin: '12px 0 6px', color: 'var(--text-primary)' }}>{children}</h2>,
                                            h3: ({ children }) => <h3 style={{ fontSize: '15px', fontWeight: 600, margin: '10px 0 4px', color: 'var(--text-primary)' }}>{children}</h3>,
                                            h4: ({ children }) => <h4 style={{ fontSize: '14px', fontWeight: 600, margin: '8px 0 4px', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{children}</h4>,
                                            ul: ({ children }) => <ul style={{ paddingLeft: '20px', margin: '4px 0 8px' }}>{children}</ul>,
                                            ol: ({ children }) => <ol style={{ paddingLeft: '20px', margin: '4px 0 8px' }}>{children}</ol>,
                                            li: ({ children }) => <li style={{ margin: '4px 0' }}>{children}</li>,
                                            code: ({ children }) => <code style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '12px', background: 'rgba(255,255,255,0.08)', padding: '1px 5px', borderRadius: '4px' }}>{children}</code>,
                                            hr: () => <hr style={{ border: 'none', borderTop: '1px solid rgba(255,255,255,0.08)', margin: '12px 0' }} />,
                                        }}
                                    >
                                        {msg.content}
                                    </ReactMarkdown>
                                ) : (
                                    msg.content
                                )}
                            </div>
                        )
                    })}

                    {isRunning && (
                        <motion.div
                            style={{ display: 'flex', gap: '4px', padding: '12px 0' }}
                        >
                            {[0, 1, 2].map(i => (
                                <motion.span
                                    key={i}
                                    animate={{ opacity: [0.3, 1, 0.3], y: [0, -4, 0] }}
                                    transition={{ repeat: Infinity, duration: 1.2, delay: i * 0.2 }}
                                    style={{
                                        width: '6px',
                                        height: '6px',
                                        borderRadius: '50%',
                                        backgroundColor: 'var(--demo-color)',
                                        display: 'inline-block'
                                    }}
                                />
                            ))}
                        </motion.div>
                    )}
                </div>
            </div>

            {/* Input Bar with Starter Prompts */}
            <div style={{
                position: 'fixed',
                bottom: '32px',
                left: '50%',
                transform: 'translateX(-50%)',
                width: 'min(680px, calc(100vw - 48px))',
                zIndex: 20,
            }}>
                {/* Starter Prompts - only show if no messages */}
                {messages.length === 0 && (
                    <div style={{
                        display: 'flex',
                        gap: '8px',
                        flexWrap: 'wrap',
                        marginBottom: '16px',
                        justifyContent: 'center'
                    }}>
                        {STARTER_PROMPTS[demoId]?.map((prompt, idx) => (
                            <motion.button
                                key={idx}
                                onClick={() => send(prompt)}
                                whileHover={{ background: 'rgba(255,255,255,0.1)' }}
                                style={{
                                    background: 'rgba(255,255,255,0.05)',
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    padding: '6px 16px',
                                    borderRadius: '16px',
                                    fontSize: '13px',
                                    color: 'var(--text-secondary)',
                                    cursor: 'pointer',
                                    backdropFilter: 'blur(8px)'
                                }}
                            >
                                {prompt}
                            </motion.button>
                        ))}
                    </div>
                )}

                <form onSubmit={handleSend} style={{ width: '100%' }}>
                    <input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type a message..."
                        style={{
                            width: '100%',
                            background: 'rgba(255,255,255,0.05)',
                            backdropFilter: 'blur(12px) saturate(180%)',
                            border: '1px solid rgba(255,255,255,0.1)',
                            borderRadius: '16px',
                            padding: '14px 20px',
                            color: 'var(--text-primary)',
                            fontSize: '15px',
                            outline: 'none',
                        }}
                    />
                </form>
            </div>

            {/* Floating Overlays */}
            <CanvasHUD agentState={agentState} />
            <ToolDrawer
                baseUrl={BASE_URL}
                demoId={demoId}
                isOpen={isToolDrawerOpen}
                onClose={() => setIsToolDrawerOpen(false)}
            />
            {/* Full-screen Voice Overlay */}
            <VoiceScene
                demoId={demoId}
                isActive={isVoiceActive}
                onEndCall={() => setIsVoiceActive(false)}
            />
        </motion.div>
    )
}
