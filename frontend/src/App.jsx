import { useState } from 'react'
import { AnimatePresence } from 'framer-motion'
import { DemoSelector, DEMOS } from './components/DemoSelector'
import { DemoView } from './components/DemoView'
import './styles/global.css'

export default function App() {
  const [activeDemo, setActiveDemo] = useState(null)

  return (
    <>
      <AnimatePresence mode="wait">
        {!activeDemo ? (
          <DemoSelector
            key="selector"
            onSelectDemo={(id) => setActiveDemo(id)}
          />
        ) : (
          <DemoView
            key="demo"
            demoId={activeDemo}
            demoConfig={DEMOS[activeDemo]}
            onBack={() => setActiveDemo(null)}
          />
        )}
      </AnimatePresence>
    </>
  )
}
