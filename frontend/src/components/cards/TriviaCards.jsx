import { GenUICard } from '../GenUICard'
import { motion } from 'framer-motion'
import { useState } from 'react'

export function QuestionCard({ data, onAnswer }) {
    const [selected, setSelected] = useState(null)
    const { question_id, question, all_answers, difficulty, category } = data

    const handleSelect = (idx, ans) => {
        setSelected(idx)
        if (onAnswer) setTimeout(() => onAnswer(ans), 400) // fake delay
    }

    return (
        <GenUICard id={question_id}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                <span style={{ color: 'var(--text-accent)', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    {category}
                </span>
                <span style={{
                    fontSize: '11px',
                    padding: '2px 8px',
                    borderRadius: '12px',
                    background: difficulty === 'hard' ? 'rgba(196, 112, 78, 0.2)'
                        : difficulty === 'medium' ? 'rgba(232, 184, 109, 0.2)'
                            : 'rgba(122, 168, 138, 0.2)',
                    color: difficulty === 'hard' ? 'var(--accent-rust)'
                        : difficulty === 'medium' ? 'var(--accent-amber)'
                            : 'var(--accent-sage)',
                }}>
                    {difficulty}
                </span>
            </div>

            <h3 style={{ fontSize: '20px', fontWeight: 500, marginBottom: '24px', lineHeight: 1.4 }}>
                {question}
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {(all_answers || []).map((ans, idx) => (
                    <motion.button
                        key={idx}
                        whileHover={{ x: 4, background: 'rgba(255,255,255,0.06)' }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => handleSelect(idx, ans)}
                        style={{
                            textAlign: 'left',
                            padding: '14px 16px',
                            background: selected === idx ? 'var(--bg-elevated)' : 'rgba(255,255,255,0.03)',
                            border: selected === idx ? '1px solid var(--accent-violet)' : '1px solid rgba(255,255,255,0.05)',
                            borderRadius: '8px',
                            color: 'var(--text-primary)',
                            fontSize: '15px',
                            transition: 'border 0.2s',
                            cursor: selected !== null ? 'default' : 'pointer'
                        }}
                        disabled={selected !== null}
                    >
                        {ans}
                    </motion.button>
                ))}
            </div>
        </GenUICard>
    )
}

export function AnswerCard({ data }) {
    const { question_id, is_correct, correct_answer, points_earned, explanation } = data
    const color = is_correct ? 'var(--accent-sage)' : 'var(--accent-rust)'

    return (
        <GenUICard id={`ans-${question_id}`}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
                <div style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    background: `${color}20`,
                    border: `1px solid ${color}40`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: color,
                    fontSize: '20px'
                }}>
                    {is_correct ? '✓' : '✗'}
                </div>

                <div>
                    <div style={{ fontSize: '18px', fontWeight: 500, color: color }}>
                        {is_correct ? 'Correct!' : 'Incorrect'}
                    </div>
                    <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
                        +{points_earned} points
                    </div>
                </div>
            </div>

            {!is_correct && (
                <div style={{ marginBottom: '16px', fontSize: '14px' }}>
                    Correct answer: <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{correct_answer}</span>
                </div>
            )}

            {explanation && (
                <div style={{
                    padding: '12px',
                    background: 'rgba(255,255,255,0.02)',
                    borderRadius: '8px',
                    fontSize: '14px',
                    color: 'var(--text-secondary)',
                    lineHeight: 1.6
                }}>
                    {explanation}
                </div>
            )}
        </GenUICard>
    )
}

export function ScoreboardCard({ data }) {
    // Normalize field names: end_game returns final_score/correct_answers
    const score = data.score ?? data.final_score ?? 0
    const correct = data.correct ?? data.correct_answers ?? 0
    const questions_asked = data.questions_asked ?? 0
    const accuracy_pct = data.accuracy_pct ?? 0
    const performance_tier = data.performance_tier ?? ''

    return (
        <GenUICard id={`score-${score}`}>
            <div style={{ textAlign: 'center', marginBottom: '24px' }}>
                <div style={{ fontSize: '13px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>
                    Current Score
                </div>
                <div style={{ fontSize: '64px', fontWeight: 600, color: 'var(--accent-violet)', lineHeight: 1 }}>
                    {score}
                </div>
            </div>

            <div className="grid-2-col" style={{ gap: '16px', marginBottom: '24px' }}>
                <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '8px', textAlign: 'center' }}>
                    <div style={{ fontSize: '24px', fontWeight: 500 }}>{correct} <span style={{ color: 'var(--text-muted)', fontSize: '18px' }}>/ {questions_asked}</span></div>
                    <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>QUESTIONS CORRECT</div>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '8px', textAlign: 'center' }}>
                    <div style={{ fontSize: '24px', fontWeight: 500 }}>{accuracy_pct}%</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>ACCURACY</div>
                </div>
            </div>

            <div style={{ textAlign: 'center' }}>
                <span style={{
                    display: 'inline-block',
                    border: '2px solid var(--accent-violet)',
                    color: 'var(--accent-violet)',
                    padding: '4px 16px',
                    borderRadius: '100px',
                    fontSize: '14px',
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    letterSpacing: '0.1em'
                }}>
                    {performance_tier} Rank
                </span>
            </div>
        </GenUICard>
    )
}

export function CategoryCard({ data, onAnswer }) {
    return (
        <GenUICard id="categories">
            <div style={{ marginBottom: '20px', fontSize: '18px', fontWeight: 500 }}>
                Select a Category
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
                {(data.categories || []).map((cat) => (
                    <motion.button
                        key={cat.id}
                        onClick={() => onAnswer && onAnswer(`Let's play ${cat.name}`)}
                        whileHover={{ scale: 1.05, background: 'rgba(255,255,255,0.1)' }}
                        whileTap={{ scale: 0.95 }}
                        style={{
                            background: 'rgba(255,255,255,0.05)',
                            border: '1px solid rgba(255,255,255,0.1)',
                            padding: '12px 20px',
                            borderRadius: '24px',
                            color: 'var(--text-primary)',
                            fontSize: '14px',
                            cursor: 'pointer'
                        }}
                    >
                        {cat.name}
                    </motion.button>
                ))}
            </div>
        </GenUICard>
    )
}
