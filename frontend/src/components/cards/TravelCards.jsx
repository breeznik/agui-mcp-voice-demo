import { GenUICard } from '../GenUICard'

export function FlightCard({ data }) {
    const flights = data.flights || []
    const passengers = data.passengers ?? 1
    // Tool returns duration_hours; guard against empty list for Math.min
    const minPrice = flights.length > 0 ? Math.min(...flights.map(f => f.price_usd || 0)) : null
    return (
        <GenUICard id={flights[0]?.flight_id || 'flight'}>
            <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '18px', fontWeight: 500 }}>Flights</span>
                <span style={{ color: 'var(--text-muted)' }}>{passengers} passenger{passengers > 1 && 's'}</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {flights.map(f => (
                    <div key={f.flight_id} style={{
                        display: 'flex',
                        alignItems: 'center',
                        padding: '12px',
                        background: 'rgba(255,255,255,0.03)',
                        borderRadius: '8px',
                        border: minPrice !== null && f.price_usd === minPrice
                            ? '1px solid var(--accent-amber)'
                            : '1px solid transparent'
                    }}>
                        <div style={{ flex: 1 }}>
                            <div style={{ fontWeight: 500 }}>{f.airline}</div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)', fontSize: '14px', marginTop: '4px' }}>
                                <span>{f.origin}</span>
                                <span>→</span>
                                <span>{f.destination}</span>
                            </div>
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
                            <div style={{ color: 'var(--accent-amber)', fontWeight: 600, fontSize: '18px' }}>
                                ${f.price_usd}
                            </div>
                            <div style={{ display: 'flex', gap: '6px', fontSize: '12px' }}>
                                <span style={{ background: 'rgba(255,255,255,0.08)', padding: '2px 6px', borderRadius: '4px' }}>
                                    {f.duration_h || f.duration_hours || '?'}h
                                </span>
                                <span style={{ background: 'rgba(255,255,255,0.08)', padding: '2px 6px', borderRadius: '4px' }}>
                                    {(f.stops ?? 0) === 0 ? 'Nonstop' : `${f.stops} stop${f.stops > 1 ? 's' : ''}`}
                                </span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </GenUICard>
    )
}

export function WeatherCard({ data }) {
    const city = data.city || ''
    const forecast = data.forecast || []
    return (
        <GenUICard id={`weather-${city}`}>
            <div style={{ marginBottom: '20px', fontSize: '18px', fontWeight: 500 }}>
                Forecast: {city}
            </div>

            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                overflowX: 'auto',
                gap: '12px',
                paddingBottom: '8px'
            }}>
                {forecast.map((day, i) => (
                    <div key={i} style={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        minWidth: '80px',
                        padding: '16px 12px',
                        background: 'rgba(255,255,255,0.03)',
                        borderRadius: '8px',
                    }}>
                        <div style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '8px' }}>
                            {day.date ? new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' }) : '—'}
                        </div>
                        <div style={{ fontSize: '28px', marginBottom: '8px' }}>{day.icon || '🌤️'}</div>
                        <div style={{ fontSize: '20px', fontWeight: 500, marginBottom: '4px' }}>{day.temp_c}°</div>
                        <div style={{ color: 'var(--text-muted)', fontSize: '11px', textAlign: 'center', lineHeight: 1.2 }}>
                            {day.condition || day.description}
                        </div>
                    </div>
                ))}
            </div>
        </GenUICard>
    )
}

export function HotelCard({ data }) {
    const hotels = data.hotels || []
    const city = data.city || ''
    return (
        <GenUICard id={`hotels-${city}`}>
            <div style={{ marginBottom: '16px', fontSize: '18px', fontWeight: 500 }}>
                Stays in {city}
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {hotels.map(h => {
                    const stars = Math.max(0, Math.min(5, h.stars || 0))
                    return (
                        <div key={h.hotel_id} style={{
                            padding: '12px',
                            background: 'rgba(255,255,255,0.03)',
                            borderRadius: '8px',
                        }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                <div>
                                    <div style={{ fontWeight: 500, fontSize: '16px' }}>{h.name}</div>
                                    <div style={{ color: 'var(--text-accent)', fontSize: '12px', marginTop: '4px' }}>
                                        {'★'.repeat(stars)}{'☆'.repeat(5 - stars)}
                                        <span style={{ color: 'var(--text-muted)', marginLeft: '8px' }}>{h.rating}/5 rating</span>
                                    </div>
                                </div>
                                <div style={{ textAlign: 'right' }}>
                                    <div style={{ fontWeight: 600, fontSize: '18px' }}>${h.price_per_night_usd}</div>
                                    <div style={{ color: 'var(--text-muted)', fontSize: '12px' }}>/ night</div>
                                </div>
                            </div>

                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '12px' }}>
                                {(h.amenities || []).map(item => (
                                    <span key={item} style={{
                                        fontSize: '11px',
                                        color: 'var(--text-secondary)',
                                        background: 'rgba(255,255,255,0.05)',
                                        padding: '2px 8px',
                                        borderRadius: '12px'
                                    }}>
                                        {item}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )
                })}
            </div>
        </GenUICard>
    )
}

export function ItineraryCard({ data }) {
    const itinerary = data.itinerary || []
    const destination = data.destination || 'Trip'
    return (
        <GenUICard id={`itinerary-${destination}`}>
            <div style={{ marginBottom: '20px', fontSize: '18px', fontWeight: 500 }}>
                Itinerary: {destination}
            </div>

            <div style={{ position: 'relative', paddingLeft: '16px' }}>
                {/* Timeline line */}
                <div style={{
                    position: 'absolute',
                    left: '27px',
                    top: '24px',
                    bottom: '24px',
                    width: '1px',
                    background: 'linear-gradient(to bottom, var(--text-muted) 0%, transparent 100%)',
                    opacity: 0.3
                }} />

                {itinerary.map((day, i) => (
                    <div key={i} style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
                        {/* Circle badge */}
                        <div style={{
                            width: '24px',
                            height: '24px',
                            borderRadius: '50%',
                            background: 'var(--bg-elevated)',
                            border: '1px solid var(--text-muted)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '12px',
                            fontWeight: 500,
                            zIndex: 2,
                            flexShrink: 0,
                            marginTop: '2px'
                        }}>
                            {day.day}
                        </div>

                        <div style={{ flex: 1 }}>
                            <div style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '8px', fontWeight: 500 }}>
                                Day {day.day}
                            </div>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                {(day.activities || []).map((act, idx) => (
                                    <div key={idx} style={{
                                        fontSize: '14px',
                                        padding: '8px 12px',
                                        background: 'rgba(255,255,255,0.02)',
                                        borderRadius: '6px',
                                        borderLeft: '2px solid var(--demo-color)'
                                    }}>
                                        {act}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </GenUICard>
    )
}
