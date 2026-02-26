import { GenUICard } from '../GenUICard'

export function RecipeCard({ data }) {
    const { title, difficulty, time_min, ingredients, steps } = data
    return (
        <GenUICard id={`recipe-${title}`}>
            <div style={{ marginBottom: '24px' }}>
                <h3 style={{ fontSize: '24px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>
                    {title}
                </h3>
                <div style={{ display: 'flex', gap: '12px', fontSize: '13px', color: 'var(--text-secondary)' }}>
                    <span style={{
                        background: 'color-mix(in srgb, var(--accent-sage) 15%, transparent)',
                        color: 'var(--accent-sage)',
                        padding: '2px 8px',
                        borderRadius: '12px'
                    }}>
                        {difficulty}
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        ⏱️ {time_min} mins
                    </span>
                </div>
            </div>

            <div className="grid-1-2-col" style={{ gap: '24px' }}>
                {/* Ingredients Column */}
                <div>
                    <h4 style={{ fontSize: '14px', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '12px' }}>
                        Ingredients
                    </h4>
                    <ul style={{ listStyleType: 'none', padding: 0, margin: 0, fontSize: '14px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {ingredients.map((ing, idx) => (
                            <li key={idx} style={{ paddingBottom: '8px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                {ing}
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Steps Column */}
                <div>
                    <h4 style={{ fontSize: '14px', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)', marginBottom: '12px' }}>
                        Instructions
                    </h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        {steps.map((step, idx) => (
                            <div key={idx} style={{ display: 'flex', gap: '12px', fontSize: '15px' }}>
                                <div style={{
                                    color: 'var(--accent-sage)',
                                    fontWeight: 600,
                                    fontSize: '18px',
                                    fontFamily: 'JetBrains Mono',
                                    opacity: 0.8
                                }}>
                                    {idx + 1}.
                                </div>
                                <div style={{ lineHeight: 1.6 }}>
                                    {step}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </GenUICard>
    )
}

export function MealPlanCard({ data }) {
    const { days } = data
    return (
        <GenUICard id="meal-plan">
            <div style={{ marginBottom: '20px', fontSize: '18px', fontWeight: 500 }}>
                Weekly Meal Plan
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {days.map((day, dIdx) => (
                    <div key={dIdx} style={{
                        background: 'rgba(255,255,255,0.02)',
                        borderRadius: '8px',
                        padding: '16px',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '12px',
                        borderLeft: '2px solid var(--accent-sage)'
                    }}>
                        <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                            Day {day.day}
                        </div>

                        <div className="grid-3-col" style={{ gap: '16px' }}>
                            <div>
                                <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>BREAKFAST</div>
                                <div style={{ fontSize: '14px' }}>{day.meals.breakfast}</div>
                            </div>
                            <div>
                                <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>LUNCH</div>
                                <div style={{ fontSize: '14px' }}>{day.meals.lunch}</div>
                            </div>
                            <div>
                                <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>DINNER</div>
                                <div style={{ fontSize: '14px' }}>{day.meals.dinner}</div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </GenUICard>
    )
}

export function NutritionCard({ data }) {
    const { recipe_name, calories, protein_g, carbs_g, fat_g, fiber_g } = data

    const widthPct = (val, max) => `${Math.min((val / max) * 100, 100)}%`

    return (
        <GenUICard id={`nutrition-${recipe_name}`}>
            <div style={{ textAlign: 'center', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '18px', fontWeight: 500, marginBottom: '8px' }}>{recipe_name}</h3>
                <div style={{ fontSize: '48px', fontWeight: 600, color: 'var(--accent-sage)', lineHeight: 1 }}>{calories}</div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginTop: '4px' }}>CALORIES</div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ width: '60px', fontSize: '13px', color: 'var(--text-secondary)' }}>Protein</div>
                    <div style={{ flex: 1, background: 'rgba(255,255,255,0.05)', height: '12px', borderRadius: '6px', overflow: 'hidden' }}>
                        <div style={{ width: widthPct(protein_g, 100), height: '100%', background: 'var(--accent-slate)', borderRadius: '6px' }} />
                    </div>
                    <div style={{ width: '40px', fontSize: '13px', textAlign: 'right', fontWeight: 500 }}>{protein_g}g</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ width: '60px', fontSize: '13px', color: 'var(--text-secondary)' }}>Carbs</div>
                    <div style={{ flex: 1, background: 'rgba(255,255,255,0.05)', height: '12px', borderRadius: '6px', overflow: 'hidden' }}>
                        <div style={{ width: widthPct(carbs_g, 100), height: '100%', background: 'var(--accent-amber)', borderRadius: '6px' }} />
                    </div>
                    <div style={{ width: '40px', fontSize: '13px', textAlign: 'right', fontWeight: 500 }}>{carbs_g}g</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ width: '60px', fontSize: '13px', color: 'var(--text-secondary)' }}>Fat</div>
                    <div style={{ flex: 1, background: 'rgba(255,255,255,0.05)', height: '12px', borderRadius: '6px', overflow: 'hidden' }}>
                        <div style={{ width: widthPct(fat_g, 100), height: '100%', background: 'var(--accent-rust)', borderRadius: '6px' }} />
                    </div>
                    <div style={{ width: '40px', fontSize: '13px', textAlign: 'right', fontWeight: 500 }}>{fat_g}g</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ width: '60px', fontSize: '13px', color: 'var(--text-secondary)' }}>Fiber</div>
                    <div style={{ flex: 1, background: 'rgba(255,255,255,0.05)', height: '12px', borderRadius: '6px', overflow: 'hidden' }}>
                        <div style={{ width: widthPct(fiber_g, 100), height: '100%', background: 'var(--accent-sage)', borderRadius: '6px' }} />
                    </div>
                    <div style={{ width: '40px', fontSize: '13px', textAlign: 'right', fontWeight: 500 }}>{fiber_g}g</div>
                </div>
            </div>
        </GenUICard>
    )
}

export function ShoppingListCard({ data }) {
    const { shopping_list } = data
    return (
        <GenUICard id="shopping-list">
            <div style={{ marginBottom: '20px', fontSize: '18px', fontWeight: 500 }}>
                Grocery List
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                {shopping_list.map((category, idx) => (
                    <div key={idx}>
                        <div style={{
                            fontSize: '14px',
                            fontWeight: 600,
                            color: 'var(--accent-sage)',
                            textTransform: 'uppercase',
                            letterSpacing: '0.05em',
                            marginBottom: '12px',
                            borderBottom: '1px solid rgba(122, 168, 138, 0.2)',
                            paddingBottom: '4px'
                        }}>
                            {category.category}
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                            {category.items.map((item, id) => (
                                <label key={id} style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}>
                                    <input type="checkbox" style={{
                                        width: '16px', height: '16px', borderRadius: '4px', border: '1px solid var(--text-muted)'
                                    }} />
                                    <span style={{ fontSize: '14px', color: 'var(--text-primary)' }}>{item}</span>
                                </label>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </GenUICard>
    )
}
