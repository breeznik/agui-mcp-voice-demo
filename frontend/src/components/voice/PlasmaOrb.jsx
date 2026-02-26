import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

export function PlasmaOrb({ phase = 'idle', audioLevel = 0 }) {
    const phaseConfig = {
        idle: { color1: "#3A3430", color2: "#2A2420", scale: 1.0, speed: 8 },
        listening: { color1: "#6E8FA8", color2: "#4A6878", scale: 1.05, speed: 4 },
        transcribing: { color1: "#9B7EC8", color2: "#6B5E98", scale: 1.02, speed: 6 },
        thinking: { color1: "#E8B86D", color2: "#C49040", scale: 1.0, speed: 3 },
        speaking: { color1: "#7AA88A", color2: "#5A8870", scale: 1.08, speed: 2 },
        error: { color1: "#C4704E", color2: "#944030", scale: 0.98, speed: 10 },
    };

    const config = phaseConfig[phase] || phaseConfig.idle;

    // Normalize audio level (0-255) to a subtle scale multiplier
    const dynamicScale = 1 + (Math.min(audioLevel, 255) / 255) * 0.15;

    return (
        <motion.div
            className="orb-container"
            animate={{ scale: config.scale * dynamicScale }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            style={{
                width: '240px',
                height: '240px',
                position: 'relative',
                margin: '0 auto',
            }}
        >
            {/* Core orb gradient */}
            <motion.div
                className="orb-core"
                animate={{
                    background: `radial-gradient(circle at 40% 35%, ${config.color1}, ${config.color2})`,
                }}
                transition={{ duration: 1.5, ease: "easeInOut" }}
                style={{
                    width: '100%',
                    height: '100%',
                    borderRadius: '50%',
                    position: 'absolute',
                }}
            />

            {/* Outer audio-reactive glow ring */}
            <motion.div
                className="orb-glow"
                animate={{
                    boxShadow: `0 0 ${40 + (audioLevel / 2)}px ${config.color1}40`,
                    opacity: 0.4 + (audioLevel / 255) * 0.6,
                }}
                transition={{ type: "tween", duration: 0.1 }}
                style={{
                    width: '140%',
                    height: '140%',
                    borderRadius: '50%',
                    position: 'absolute',
                    top: '-20%',
                    left: '-20%',
                    pointerEvents: 'none',
                }}
            />

            {/* SVG plasma turbulence filter overlay */}
            <div
                className="orb-shimmer"
                style={{
                    position: 'absolute',
                    inset: '-20%',
                    borderRadius: '50%',
                    filter: "url(#plasma)",
                    mixBlendMode: 'overlay',
                    opacity: 0.8
                }}
            />
        </motion.div>
    );
}
