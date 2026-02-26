import { useState, useRef, useCallback } from 'react'
import { HttpAgent } from '@ag-ui/client'
import { applyPatch } from 'fast-json-patch'

/**
 * Hook that bridges React rendering state with the AG-UI HttpAgent protocol.
 *
 * Two separate message stores:
 *   1. agentRef.current.messages — AG-UI protocol messages (user + assistant).
 *      Owned by HttpAgent, sent to backend. Updated internally by HttpAgent's
 *      apply() from SSE events (TEXT_MESSAGE_START, MESSAGES_SNAPSHOT, etc.).
 *   2. React `messages` state — UI rendering messages. Includes cards, tool
 *      stamps, and other display-only entries the backend doesn't know about.
 */
export function useCustomAgent({ baseUrl, demoId, onCustomEvent }) {
    const [messages, setMessages] = useState([])          // UI messages (includes cards, tool stamps)
    const [agentState, setAgentState] = useState({})
    const [isRunning, setIsRunning] = useState(false)
    const [toolCalls, setToolCalls] = useState({})         // toolId -> { name, args, status }
    const [activity, setActivity] = useState(null)          // { phase, title, detail }

    const runIdRef = useRef(null)
    const agentRef = useRef(null)
    const threadIdRef = useRef(`${demoId}-${crypto.randomUUID()}`)

    const initAgent = useCallback(() => {
        if (!agentRef.current) {
            agentRef.current = new HttpAgent({
                url: `${baseUrl}/agent/${demoId}`,
                threadId: threadIdRef.current,
            })
        }
    }, [baseUrl, demoId])

    const send = useCallback(async (content) => {
        initAgent()

        const newUserMsg = { id: crypto.randomUUID(), role: 'user', content }

        // 1. Add to UI messages for rendering
        setMessages(prev => [...prev, newUserMsg])
        setIsRunning(true)
        setActivity(null)

        // 2. Add to HttpAgent's protocol-layer messages so it actually
        //    gets included in the POST body to the backend.
        //    (HttpAgent.runAgent reads from this.messages, NOT from params.)
        agentRef.current.messages.push(newUserMsg)

        const runId = crypto.randomUUID()
        runIdRef.current = runId

        try {
            // runAgent() only accepts { runId, tools, context, forwardedProps }.
            // threadId, messages, and state are read from HttpAgent internal state.
            await agentRef.current.runAgent(
                { runId },
                {
                    onRunStartedEvent: () => setIsRunning(true),
                    onRunFinishedEvent: () => {
                        setIsRunning(false)
                        setActivity(null)
                    },
                    onRunErrorEvent: ({ event }) => {
                        console.error('Agent run error:', event)
                        setIsRunning(false)
                    },

                    // --- Text messages ------------------------------------------------
                    onTextMessageStartEvent: ({ event }) => {
                        setMessages(prev => [...prev, {
                            id: event.messageId,
                            role: 'assistant',
                            content: ''
                        }])
                    },
                    onTextMessageContentEvent: ({ event }) => {
                        setMessages(prev => prev.map(m =>
                            m.id === event.messageId
                                ? { ...m, content: m.content + event.delta }
                                : m
                        ))
                    },
                    onTextMessageEndEvent: () => { },

                    // --- Tool calls ---------------------------------------------------
                    onToolCallStartEvent: ({ event }) => {
                        setToolCalls(prev => ({
                            ...prev,
                            [event.toolCallId]: {
                                name: event.toolCallName,
                                args: '',
                                status: 'running'
                            }
                        }))
                        // Insert a UI-only "tool_stamp" into the chat for inline rendering.
                        // Using 'tool_stamp' (not 'tool') to avoid collision with the
                        // AG-UI protocol's 'tool' role.
                        setMessages(prev => [...prev, {
                            id: event.toolCallId,
                            role: 'tool_stamp',
                            toolCallId: event.toolCallId
                        }])
                    },
                    onToolCallArgsEvent: ({ event }) => {
                        setToolCalls(prev => {
                            const current = prev[event.toolCallId]
                            if (!current) return prev
                            return {
                                ...prev,
                                [event.toolCallId]: { ...current, args: current.args + event.delta }
                            }
                        })
                    },
                    onToolCallEndEvent: ({ event }) => {
                        setToolCalls(prev => {
                            const current = prev[event.toolCallId]
                            if (!current) return prev
                            return {
                                ...prev,
                                [event.toolCallId]: { ...current, status: 'done' }
                            }
                        })
                    },

                    // --- State --------------------------------------------------------
                    onStateSnapshotEvent: ({ event }) => setAgentState(event.snapshot),
                    onStateDeltaEvent: ({ event }) => {
                        setAgentState(prev => {
                            try {
                                return applyPatch(structuredClone(prev), event.delta).newDocument
                            } catch (e) {
                                console.warn('JSON Patch failed', e)
                                return prev
                            }
                        })
                    },

                    // Don't replace local UI messages with backend snapshots — our
                    // React state has UI entries (cards, tool stamps) the backend
                    // doesn't know about. HttpAgent's internal this.messages IS
                    // updated by apply() for protocol correctness.
                    onMessagesSnapshotEvent: () => {},

                    // --- Custom events ------------------------------------------------
                    onCustomEvent: ({ event }) => {
                        const { name, value } = event
                        if (name === 'agent_activity') {
                            setActivity(value)
                        } else if (name === 'render_card') {
                            setMessages(prev => [...prev, {
                                id: crypto.randomUUID(),
                                role: 'card',
                                cardType: value.card_type,
                                cardData: value.data
                            }])
                        } else if (onCustomEvent) {
                            onCustomEvent(name, value)
                        }
                    }
                }
            )
        } catch (error) {
            console.error("Agent execution failed:", error)
            setIsRunning(false)
        }
    }, [initAgent, onCustomEvent])

    return {
        messages,
        toolCalls,
        agentState,
        isRunning,
        activity,
        send
    }
}
