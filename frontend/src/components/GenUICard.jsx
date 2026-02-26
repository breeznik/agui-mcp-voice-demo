import { motion } from 'framer-motion'

// Seeded rotation generator based on a string input
function seedRotation(str, min = -1.5, max = 1.5) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    const random = Math.abs(Math.sin(hash))
    return min + random * (max - min)
}

export function GenUICard({ id, children }) {
    // Polaroid "developing" effect
    const cardVariants = {
        hidden: {
            opacity: 0,
            scale: 0.96,
            filter: "brightness(2) blur(4px) saturate(0)",
            rotate: seedRotation(id) * 2,
        },
        visible: {
            opacity: 1,
            scale: 1,
            filter: "brightness(1) blur(0px) saturate(1)",
            rotate: seedRotation(id),
            transition: {
                duration: 0.7,
                ease: [0.16, 1, 0.3, 1],
                filter: { duration: 1.2 },
            },
        },
    }

    return (
        <motion.div
            variants={cardVariants}
            initial="hidden"
            animate="visible"
            style={{
                width: '100%',
                maxWidth: '600px',
                background: 'var(--bg-surface)',
                borderRadius: '12px',
                padding: '20px',
                boxShadow: 'var(--shadow-card)',
                position: 'relative',
                transformOrigin: 'center center',
            }}
        >
            {/* Local Grain Overlay */}
            <div
                aria-hidden="true"
                style={{
                    position: 'absolute',
                    inset: 0,
                    borderRadius: 'inherit',
                    filter: 'url(#grain)',
                    opacity: 0.08,
                    pointerEvents: 'none',
                    zIndex: 1,
                }}
            />

            {/* Content Container (above grain) */}
            <div style={{ position: 'relative', zIndex: 2 }}>
                {children}
            </div>
        </motion.div>
    )
}
