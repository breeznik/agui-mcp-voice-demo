import { GenUICard } from '../GenUICard'
import { motion } from 'framer-motion'

export function ProductCard({ data }) {
    const { products, category } = data
    return (
        <GenUICard id={`products-${category}`}>
            <div style={{ marginBottom: '16px', fontSize: '18px', fontWeight: 500 }}>
                Shopping: {category}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                {products.map(p => (
                    <div key={p.product_id} style={{
                        display: 'flex',
                        flexDirection: 'column',
                        padding: '16px',
                        background: 'rgba(255,255,255,0.02)',
                        borderRadius: '8px',
                        border: '1px solid rgba(255,255,255,0.05)',
                        position: 'relative',
                        opacity: p.in_stock ? 1 : 0.6
                    }}>
                        <div style={{
                            width: '100%',
                            aspectRatio: '1',
                            background: 'rgba(255,255,255,0.05)',
                            borderRadius: '6px',
                            marginBottom: '12px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '48px'
                        }}>
                            {p.icon || '🛍️'}
                        </div>

                        <div style={{ flex: 1 }}>
                            <div style={{ fontWeight: 500, fontSize: '15px', marginBottom: '4px', lineHeight: 1.3 }}>
                                {p.name}
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                                <span style={{ color: 'var(--accent-rust)', fontWeight: 600, fontSize: '16px' }}>
                                    ${p.price}
                                </span>
                                <span style={{ color: 'var(--accent-amber)', fontSize: '10px' }}>
                                    {'★'.repeat(Math.round(p.rating))}
                                </span>
                            </div>
                        </div>

                        {p.in_stock ? (
                            <motion.button
                                whileHover={{ background: 'rgba(255,255,255,0.1)' }}
                                whileTap={{ scale: 0.95 }}
                                style={{
                                    width: '100%',
                                    padding: '8px',
                                    background: 'rgba(255,255,255,0.05)',
                                    color: 'var(--text-primary)',
                                    border: 'none',
                                    borderRadius: '6px',
                                    fontSize: '13px',
                                    fontWeight: 500,
                                    marginTop: 'auto'
                                }}
                            >
                                Add to Cart
                            </motion.button>
                        ) : (
                            <div style={{
                                position: 'absolute',
                                top: 24, right: -8,
                                background: 'var(--accent-rust)',
                                color: 'white',
                                padding: '2px 8px',
                                fontSize: '10px',
                                fontWeight: 600,
                                textTransform: 'uppercase',
                                transform: 'rotate(12deg)'
                            }}>
                                Sold Out
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </GenUICard>
    )
}

export function CartCard({ data }) {
    const { items, item_count, total } = data
    return (
        <GenUICard id={`cart-${total}`}>
            <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                <h3 style={{ fontSize: '20px', fontWeight: 500 }}>Your Cart</h3>
                <span style={{ color: 'var(--text-muted)', fontSize: '14px' }}>{item_count} items</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '24px' }}>
                {items.map(item => (
                    <div key={item.product_id} style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '16px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                        <div>
                            <div style={{ fontSize: '15px', fontWeight: 500 }}>{item.name}</div>
                            <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginTop: '4px' }}>
                                {item.quantity} × ${item.unit_price.toFixed(2)}
                            </div>
                        </div>
                        <div style={{ fontSize: '16px', color: 'var(--text-primary)' }}>
                            ${item.subtotal.toFixed(2)}
                        </div>
                    </div>
                ))}
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <span style={{ fontSize: '16px', color: 'var(--text-secondary)' }}>Total</span>
                <span style={{ fontSize: '24px', fontWeight: 600, color: 'var(--accent-rust)' }}>
                    ${total.toFixed(2)}
                </span>
            </div>

            <motion.button
                whileHover={{ filter: 'brightness(1.1)' }}
                whileTap={{ scale: 0.98 }}
                style={{
                    width: '100%',
                    padding: '16px',
                    background: 'var(--accent-rust)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '16px',
                    fontWeight: 600,
                    cursor: 'pointer'
                }}
            >
                Proceed to Checkout
            </motion.button>
        </GenUICard>
    )
}

export function CheckoutCard({ data }) {
    const { order_id, status, items, total, estimated_delivery } = data
    return (
        <GenUICard id={`checkout-${order_id}`}>
            <div style={{ textAlign: 'center', marginBottom: '32px' }}>
                <div style={{
                    width: '64px', height: '64px', borderRadius: '50%',
                    background: 'var(--accent-sage)', color: 'white',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '32px', margin: '0 auto 16px auto',
                    boxShadow: '0 0 32px rgba(122, 168, 138, 0.3)'
                }}>
                    ✓
                </div>
                <h2 style={{ fontSize: '24px', fontWeight: 500, marginBottom: '8px' }}>Order {status}</h2>
                <div style={{ fontFamily: 'JetBrains Mono', color: 'var(--text-secondary)', fontSize: '14px' }}>
                    ID: {order_id}
                </div>
            </div>

            <div style={{ background: 'rgba(255,255,255,0.02)', padding: '20px', borderRadius: '8px', marginBottom: '24px' }}>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>
                    Estimated Delivery
                </div>
                <div style={{ fontSize: '18px', fontWeight: 500, color: 'var(--text-primary)' }}>
                    {new Date(estimated_delivery).toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric' })}
                </div>
            </div>

            <div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>
                    Order Summary
                </div>
                <div style={{ fontSize: '13px', color: 'var(--text-secondary)', display: 'flex', justifyContent: 'space-between' }}>
                    <span>{items.length} items</span>
                    <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>${total.toFixed(2)}</span>
                </div>
            </div>
        </GenUICard>
    )
}
