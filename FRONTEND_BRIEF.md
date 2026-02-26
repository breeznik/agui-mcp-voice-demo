# Frontend Implementation Brief
## agui-mcp-voice-demo — Immersive Edition

This document is the complete specification for a frontend AI to implement the React frontend. The backend is fully built — your job is to create an immersive, cinematic UI that connects to it.

---

## 0. Design Philosophy

**No panels. No borders. No grids.**

This is not a dashboard. It is an environment. The user steps into it.

- **Texture is structure** — a sandpaper-grain background replaces borders and cards. Elements float on the surface, not inside boxes.
- **Motion is meaning** — every state change is felt. Agent thinking pulses. Tool calls stamp in. Cards develop like Polaroids.
- **Voice is cinematic** — entering a call is a scene change, not a modal. The whole world shifts.
- **The agent's mind is ambient** — state canvas and tool activity appear as peripheral glows and watermarks, not panels.

The closest reference points: a designer's mood board, a darkroom table under amber light, a film editing suite.

---

## 1. Stack

```
React 19 (or 18)
Vite 6
Framer Motion 12
@ag-ui/client  ^0.0.44
@ag-ui/core    ^0.0.44
@copilotkit/react ^1.50+    ← useAgent hook (latest)
Web Audio API (built-in)
```

**No UI component libraries.** Everything is hand-crafted to match the design language. No MUI, no shadcn, no Chakra.

---

## 2. Design System: Sandpaper

### 2.1 Color Tokens

```css
:root {
  /* Backgrounds — warm dark, like aged paper under amber light */
  --bg-base:        #1E1B18;   /* deepest — body background */
  --bg-surface:     #252119;   /* cards, chat bubbles */
  --bg-elevated:    #2E2A25;   /* hover state, lifted cards */
  --bg-overlay:     #0E0C0Aee; /* voice call dark overlay */

  /* Text */
  --text-primary:   #F0EBE3;   /* main readable text */
  --text-secondary: #A89E92;   /* metadata, labels */
  --text-muted:     #685F55;   /* disabled, placeholder */
  --text-accent:    #E8B86D;   /* amber — agent speech, highlights */

  /* Accent — warm amber and muted earth tones */
  --accent-amber:   #E8B86D;
  --accent-rust:    #C4704E;
  --accent-sage:    #7AA88A;
  --accent-slate:   #6E8FA8;
  --accent-violet:  #9B7EC8;

  /* Demo-specific accent colors (used to tint the whole experience) */
  --demo-travel:    #6E8FA8;   /* sky blue-gray */
  --demo-trivia:    #9B7EC8;   /* violet */
  --demo-shopping:  #C4704E;   /* rust */
  --demo-chef:      #7AA88A;   /* sage green */
  --demo-support:   #A89E92;   /* warm gray */

  /* Grain texture — applied via SVG filter on ::before pseudo */
  --grain-opacity:  0.06;
  --grain-intensity: 65;       /* SVG feTurbulence baseFrequency */

  /* Depth */
  --shadow-card:    0 4px 24px #00000060, 0 1px 0 #ffffff08;
  --shadow-lifted:  0 12px 48px #00000080, 0 2px 0 #ffffff10;
  --shadow-ambient: 0 0 120px #E8B86D18;   /* warm ambient glow */
}
```

### 2.2 Grain Texture

Apply the grain texture globally using an SVG filter. This is the single most important visual element.

```html
<!-- Injected once into document body -->
<svg aria-hidden="true" style="position:fixed;width:0;height:0">
  <filter id="grain">
    <feTurbulence
      type="fractalNoise"
      baseFrequency="0.65"
      numOctaves="3"
      stitchTiles="stitch"
    />
    <feColorMatrix type="saturate" values="0" />
  </filter>
</svg>
```

```css
/* Global grain overlay */
body::before {
  content: '';
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  background: transparent;
  filter: url(#grain);
  opacity: var(--grain-opacity);
  pointer-events: none;
  z-index: 9999;
}
```

### 2.3 Typography

```css
/* Import in index.html */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

body {
  font-family: 'Space Grotesk', system-ui, sans-serif;
  background-color: var(--bg-base);
  color: var(--text-primary);
}

/* Monospace for tool call args, JSON, IDs */
.mono { font-family: 'JetBrains Mono', monospace; }

/* Scale */
--text-xs:   11px;
--text-sm:   13px;
--text-base: 15px;
--text-lg:   18px;
--text-xl:   24px;
--text-2xl:  32px;
--text-3xl:  48px;
```

### 2.4 Element Language

**No hard borders.** Instead:
- Cards use `box-shadow` with 2-3px gaussian blur for a "physical object" feel
- Active elements glow with the demo's accent color (`box-shadow: 0 0 32px var(--demo-color)30`)
- Separators are 1px gradients fading from transparent → color → transparent

**Rotation.** Cards appear at ±1–3° random rotation (seeded per card ID) to feel hand-placed.

**Grain on cards.** Individual cards have a subtle local grain via `mix-blend-mode: overlay` pseudo-element.

---

## 3. Application Layout

### 3.1 The Scene

There are no panels. The viewport is a single textured surface. Elements are layered on it:

```
┌──────────────────────────────────────────────────────────┐
│  [GRAIN TEXTURE — full viewport]                         │
│                                                          │
│  [Demo name watermark — huge, faded, center]            │
│                                                          │
│        [Chat thread — centered, max-w 680px]            │
│        Messages and generative UI cards float here      │
│                                                          │
│  [HUD — floating ambient overlays]                      │
│  ├─ Top-left: Demo selector (minimal text tabs)         │
│  ├─ Top-right: Voice call button + mic level            │
│  └─ Bottom ambient: tool activity watermark             │
│                                                          │
│  [Input bar — bottom, minimal, nearly invisible]        │
│                                                          │
│  [Voice Scene — full viewport takeover on call]        │
│  [State Canvas — floating HUD panel, collapsible]      │
│  [Tool Catalog — slide-in drawer from right]           │
└──────────────────────────────────────────────────────────┘
```

### 3.2 Demo Watermark

The current demo name renders as a massive, barely-visible watermark centered in the viewport. It shifts with each demo selection.

```css
.demo-watermark {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: clamp(80px, 18vw, 200px);
  font-weight: 600;
  letter-spacing: -0.04em;
  color: var(--demo-color);
  opacity: 0.04;
  pointer-events: none;
  user-select: none;
  text-transform: uppercase;
}
```

Animate the watermark with Framer Motion: `opacity: [0.02, 0.05, 0.02]` pulse on a 6s loop.

### 3.3 Chat Thread

- Max-width: `680px`, centered
- Messages appear from bottom, push content up (natural scroll)
- No visible scrollbar (custom styled or hidden)
- Bottom padding: `140px` (clearance for input bar)

### 3.4 Input Bar

Floats at the bottom, barely there. No visible border — only a subtle inner glow when focused.

```css
.input-bar {
  position: fixed;
  bottom: 32px;
  left: 50%;
  transform: translateX(-50%);
  width: min(680px, calc(100vw - 48px));
  background: #ffffff08;
  backdrop-filter: blur(12px) saturate(180%);
  border: 1px solid #ffffff10;
  border-radius: 16px;
  padding: 14px 20px;
  /* Grain texture on the input surface */
  &::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: inherit;
    background: url("data:image/svg+xml,...");  /* noise SVG */
    opacity: 0.04;
    pointer-events: none;
  }
}

.input-bar:focus-within {
  border-color: var(--accent-amber)40;
  box-shadow: 0 0 0 1px var(--accent-amber)20, 0 8px 32px #00000040;
}
```

### 3.5 HUD Overlays

**Demo selector** — top left, text-only tabs with the demo's accent color underline

```
travel   trivia   shopping   chef   support
                 ────────
```

**Voice button** — top right, minimal circle with mic icon. When mic is live, outer ring animates.

**Canvas HUD** — a semi-transparent floating panel (not a sidebar). Toggle with a small button. It appears as a glass-morphism card with sandpaper texture, positioned bottom-right, about 320px wide.

**Tool drawer** — slides in from the right edge. Triggered by a subtle "tools" button. Shows current demo's MCP tool catalog (name + description + last-called timestamp).

---

## 4. AG-UI Integration (Latest — v0.0.44)

### 4.1 Installation

```bash
npm install @ag-ui/client @ag-ui/core @copilotkit/react
```

### 4.2 useAgent Hook (CopilotKit v1.50+)

Use the `useAgent` hook — this is the modern approach as of 2026, not the older `HttpAgent` subscription pattern.

```jsx
import { CopilotKit } from "@copilotkit/react-core";
import { useAgent } from "@copilotkit/react";

// Wrap your app
function App() {
  return (
    <CopilotKit runtimeUrl={`${BASE_URL}/agent/${demo}`}>
      <DemoView />
    </CopilotKit>
  );
}

// Inside DemoView
function DemoView() {
  const { messages, state, isRunning, run } = useAgent({
    agent: {
      name: demo,
      url: `${BASE_URL}/agent/${demo}`,
    },
    onCustomEvent: (event) => handleCustomEvent(event),
    onStateChanged: ({ state }) => handleStateUpdate(state),
    onNewToolCall: ({ toolCall }) => handleToolCall(toolCall),
  });
}
```

### 4.3 Fallback: Direct @ag-ui/client HttpAgent

If you prefer direct control without CopilotKit:

```javascript
import { HttpAgent } from "@ag-ui/client";

const agent = new HttpAgent({
  url: `${BASE_URL}/agent/${demo}`,
});

const result = await agent.runAgent(
  {
    threadId,
    runId: crypto.randomUUID(),
    messages: currentMessages,
    state: agentState,
  },
  {
    // ── Lifecycle ─────────────────────────────────────────────────
    onRunStarted: () => setIsRunning(true),
    onRunFinished: () => setIsRunning(false),
    onRunError: ({ error }) => handleError(error),

    // ── Text streaming ────────────────────────────────────────────
    onTextMessageStart: ({ messageId }) => startStreamingMessage(messageId),
    onTextMessageContent: ({ messageId, delta }) => appendChunk(messageId, delta),
    onTextMessageEnd: ({ messageId }) => finalizeMessage(messageId),

    // ── Tool calls (stream args as they arrive) ───────────────────
    onToolCallStart: ({ toolCallId, toolName, parentMessageId }) =>
      addToolCallBubble({ toolCallId, toolName }),
    onToolCallArgs: ({ toolCallId, delta }) =>
      appendToolArgs(toolCallId, delta),
    onToolCallEnd: ({ toolCallId }) =>
      collapseToolCallBubble(toolCallId),

    // ── State sync ────────────────────────────────────────────────
    onStateSnapshot: ({ snapshot }) => setAgentState(snapshot),
    onStateDelta: ({ delta }) => applyJsonPatchDelta(delta),   // RFC6902 patch
    onMessagesSnapshot: ({ messages }) => setMessages(messages),

    // ── Custom events (generative UI) ────────────────────────────
    onCustomEvent: ({ name, value }) => handleCustomEvent(name, value),
  }
);
```

### 4.4 The 17 AG-UI Event Types

Your subscriber must handle all of these:

| Category | Event | Your handler |
|----------|-------|-------------|
| Lifecycle | `RUN_STARTED` | show thinking indicator |
| Lifecycle | `RUN_FINISHED` | hide indicator, enable input |
| Lifecycle | `RUN_ERROR` | show error state |
| Lifecycle | `STEP_STARTED` | (optional) fine-grained progress |
| Lifecycle | `STEP_FINISHED` | (optional) |
| Text | `TEXT_MESSAGE_START` | create streaming message bubble |
| Text | `TEXT_MESSAGE_CONTENT` | append delta to bubble |
| Text | `TEXT_MESSAGE_END` | finalize, enable TTS |
| Tool | `TOOL_CALL_START` | create tool call stamp (see §6) |
| Tool | `TOOL_CALL_ARGS` | stream args into stamp |
| Tool | `TOOL_CALL_END` | collapse stamp |
| Tool | `TOOL_CALL_RESULT` | show result badge on stamp |
| State | `STATE_SNAPSHOT` | full state replace |
| State | `STATE_DELTA` | apply JSON Patch (RFC6902) |
| State | `MESSAGES_SNAPSHOT` | replace message history |
| Special | `RAW` | passthrough (log only) |
| Special | `CUSTOM` | generative UI events (see §7) |

### 4.5 STATE_DELTA — Apply JSON Patch

```javascript
import { applyPatch } from "fast-json-patch"; // npm install fast-json-patch

function applyJsonPatchDelta(delta) {
  setAgentState(prev => {
    const result = applyPatch(structuredClone(prev), delta);
    return result.newDocument;
  });
}
```

---

## 5. Demo Selector — Landing Scene

The initial view is a full-screen scene. Not a modal or a hero section — a complete environment.

```
[Full-bleed grain background]
[Large ambient glow — warm amber center]

          agui · mcp · voice

   ◦ Travel Concierge    ◦ Trivia Host
   ◦ Shopping Assistant  ◦ Personal Chef
   ◦ Customer Support

   [Select a world to enter →]
```

### Interaction

- Each demo option shows a one-line description on hover
- Hovering tints the background glow with the demo's accent color (smooth 800ms transition)
- Clicking triggers a "scene transition": the background shifts color, the watermark fades in, and the chat view slides up from below

```jsx
// Scene transition on demo select
const demoTransition = {
  background: {
    type: "tween",
    duration: 0.8,
    ease: [0.16, 1, 0.3, 1],   // expo out
  }
}
```

### Demo metadata

```javascript
const DEMOS = {
  travel:   { label: "Travel Concierge",    color: "#6E8FA8", icon: "✈",  tagline: "Plan trips with AI + live data" },
  trivia:   { label: "Trivia Host",         color: "#9B7EC8", icon: "🎯", tagline: "Interactive quiz with score tracking" },
  shopping: { label: "Shopping Assistant",  color: "#C4704E", icon: "◈",  tagline: "Search products, manage cart" },
  chef:     { label: "Personal Chef",       color: "#7AA88A", icon: "◉",  tagline: "Recipes, nutrition, meal planning" },
  support:  { label: "Customer Support",    color: "#A89E92", icon: "◎",  tagline: "Orders, refunds, live escalation" },
}
```

---

## 6. Chat Thread & Message Design

### 6.1 Message Bubbles

No chat bubble "tails." Messages are text blocks, floating on the texture.

**User message:**
```css
.message-user {
  text-align: right;
  color: var(--text-primary);
  font-size: var(--text-base);
  max-width: 520px;
  margin-left: auto;
  padding: 12px 0;
  /* No background — pure text floating on texture */
}
```

**Agent message:**
```css
.message-agent {
  color: var(--text-accent);   /* amber for agent voice */
  font-size: var(--text-base);
  max-width: 580px;
  padding: 12px 0;
  line-height: 1.7;
}
```

**Streaming cursor:** A 2px amber vertical bar that blinks while content streams in.

### 6.2 Thinking Indicator

While the agent is running (between `RUN_STARTED` and first `TEXT_MESSAGE_CONTENT`):

Three dots in the demo's accent color, staggered animation, no background.

```jsx
<motion.div className="thinking">
  {[0, 1, 2].map(i => (
    <motion.span
      key={i}
      animate={{ opacity: [0.3, 1, 0.3], y: [0, -4, 0] }}
      transition={{ repeat: Infinity, duration: 1.2, delay: i * 0.2 }}
    />
  ))}
</motion.div>
```

### 6.3 Tool Call Stamps

When a tool call fires, a "stamp" appears in the chat — like a rubber stamp impression on paper.

**Lifecycle:**
1. `TOOL_CALL_START` → stamp appears (name only, faded in)
2. `TOOL_CALL_ARGS` → args stream in below the name (monospace, small)
3. `TOOL_CALL_END` → stamp gets a ✓ mark, slightly darker
4. After custom event fires → stamp collapses to a single chip

```jsx
function ToolCallStamp({ toolName, args, status }) {
  return (
    <motion.div
      className="tool-stamp"
      initial={{ opacity: 0, scale: 0.92, rotate: -1 }}
      animate={{ opacity: 1, scale: 1, rotate: 0 }}
      style={{ rotate: seedRotation(toolName, -1.5, 1.5) }}
    >
      <div className="stamp-header">
        <span className="stamp-icon">⬡</span>
        <span className="stamp-name mono">{toolName}</span>
        <span className="stamp-status">{status === "done" ? "✓" : "..."}</span>
      </div>
      {args && (
        <motion.pre
          className="stamp-args mono"
          initial={{ height: 0 }}
          animate={{ height: "auto" }}
        >
          {formatArgs(args)}
        </motion.pre>
      )}
    </motion.div>
  );
}
```

```css
.tool-stamp {
  display: inline-flex;
  flex-direction: column;
  background: #ffffff06;
  border: 1px solid #ffffff0A;
  border-radius: 8px;
  padding: 8px 12px;
  margin: 4px 0;
  max-width: 420px;
  font-size: var(--text-sm);
  color: var(--text-secondary);
}
.stamp-args {
  font-size: var(--text-xs);
  color: var(--text-muted);
  overflow: hidden;
  white-space: pre-wrap;
  word-break: break-all;
}
```

---

## 7. Generative UI Cards

Cards appear in-line with the chat thread, between agent messages. They feel like physical objects placed on the sandpaper surface.

### 7.1 Base Card Style

```css
.gen-card {
  width: 100%;
  max-width: 600px;
  background: var(--bg-surface);
  border-radius: 12px;
  padding: 20px;
  box-shadow: var(--shadow-card);
  /* Random slight rotation: seeded from card ID */
  transform: rotate(var(--card-rotation));
  /* Grain overlay on card surface */
  &::after {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: inherit;
    filter: url(#grain);
    opacity: 0.08;
    pointer-events: none;
  }
}
```

### 7.2 Card Entrance Animation (Polaroid develop)

Cards don't slide or fade. They *develop* — like a Polaroid photo emerging.

```jsx
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
};
```

### 7.3 Custom Event Handler → ComponentRegistry

```javascript
// Component registry — maps card_type → React component
const CARD_REGISTRY = {
  // Travel
  flight_card:      FlightCard,
  weather_card:     WeatherCard,
  hotel_card:       HotelCard,
  itinerary_card:   ItineraryCard,

  // Trivia
  question_card:    QuestionCard,
  answer_card:      AnswerCard,
  scoreboard_card:  ScoreboardCard,
  category_card:    CategoryCard,

  // Shopping
  product_card:     ProductCard,
  cart_card:        CartCard,
  checkout_card:    CheckoutCard,

  // Chef
  recipe_card:      RecipeCard,
  nutrition_card:   NutritionCard,
  meal_plan_card:   MealPlanCard,
  shopping_list_card: ShoppingListCard,

  // Support
  order_card:       OrderCard,
  ticket_card:      TicketCard,
  kb_article_card:  KbArticleCard,
  escalation_card:  EscalationCard,
};

function handleCustomEvent(name, value) {
  switch (name) {
    case "render_card": {
      const { card_type, data, message_id } = value;
      const Component = CARD_REGISTRY[card_type];
      if (!Component) return;
      insertCardIntoThread(message_id, <Component data={data} />);
      break;
    }
    case "agent_activity": {
      const { title, detail, phase } = value;
      showActivityIndicator(title, detail, phase);
      break;
    }
    case "canvas_update": {
      setCanvasState(prev => ({ ...prev, ...value.canvas }));
      break;
    }
    case "navigate": {
      handleNavigate(value.route);
      break;
    }
  }
}
```

### 7.4 Agent Activity Indicator

When `agent_activity` fires, a subtle activity strip appears near the top of the chat (not inline). It shows the phase and title, then fades after 3s.

```jsx
function AgentActivity({ title, detail, phase }) {
  const phaseColors = {
    search: "--accent-slate",
    mcp: "--accent-amber",
    thinking: "--text-secondary",
    done: "--accent-sage",
  };

  return (
    <motion.div
      className="activity-strip"
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
    >
      <span className="activity-phase" style={{ color: `var(${phaseColors[phase]})` }}>
        {phase}
      </span>
      <span className="activity-title">{title}</span>
      {detail && <span className="activity-detail">{detail}</span>}
    </motion.div>
  );
}
```

---

## 8. Generative UI Card Specs

### 8.1 Travel Cards

#### `flight_card`
```typescript
interface FlightCardData {
  flights: Array<{
    flight_id: string;       // "FL-LON-TYO-001"
    airline: string;
    origin: string;
    destination: string;
    departure: string;       // ISO datetime
    arrival: string;
    duration_h: number;
    stops: number;
    price_usd: number;
    class: string;
  }>;
  passengers: number;
  searched_at: string;
}
```

**Visual:** List of flight rows. Each row: airline name, route arrow, duration pill, stops badge, price right-aligned in amber. Cheapest flight has a subtle amber left-border accent.

#### `weather_card`
```typescript
interface WeatherCardData {
  city: string;
  forecast: Array<{
    date: string;
    condition: string;      // "Partly cloudy"
    temp_c: number;
    humidity_pct: number;
    icon: string;           // emoji or icon key
  }>;
}
```

**Visual:** 5-day horizontal strip. Each day: date, temp in large text, condition in small text, humidity pill. No chart — just typography.

#### `hotel_card`
```typescript
interface HotelCardData {
  hotels: Array<{
    hotel_id: string;
    name: string;
    stars: number;
    price_per_night_usd: number;
    rating: number;         // 0-5
    amenities: string[];
    address: string;
  }>;
  city: string;
  check_in: string;
  check_out: string;
  guests: number;
}
```

**Visual:** Stacked hotel rows. Name + stars + rating left, price right. Amenity pills below each.

#### `itinerary_card`
```typescript
interface ItineraryCardData {
  itinerary: Array<{
    day: number;
    activities: string[];
  }>;
  destination: string;
}
```

**Visual:** Day-by-day timeline. Each day has a number badge and an activity list. Vertical line connecting days.

---

### 8.2 Trivia Cards

#### `question_card`
```typescript
interface QuestionCardData {
  question_id: string;
  question: string;
  all_answers: string[];   // shuffled, includes correct
  difficulty: "easy" | "medium" | "hard";
  category: string;
}
```

**Visual:** Question text large + bold. Four answer options as clickable buttons (styled as rough paper rectangles). Difficulty badge top-right. Clicking an answer emits user message with the chosen text.

#### `answer_card`
```typescript
interface AnswerCardData {
  question_id: string;
  is_correct: boolean;
  correct_answer: string;
  points_earned: number;
  explanation?: string;
}
```

**Visual:** Big ✓ or ✗ in the demo's accent color. Correct answer revealed. Points earned in large amber text. Explanation below in muted text.

#### `scoreboard_card`
```typescript
interface ScoreboardCardData {
  score: number;
  questions_asked: number;
  correct: number;
  accuracy_pct: number;
  performance_tier: string;  // "Expert", "Apprentice", etc.
}
```

**Visual:** Score dominates — large number, amber, centered. Below: accuracy percentage bar (animated fill). Performance tier as a stamp-style badge.

#### `category_card`
```typescript
interface CategoryCardData {
  categories: Array<{ id: number; name: string }>;
}
```

**Visual:** Grid of category pills the user can click to start a quiz in that category.

---

### 8.3 Shopping Cards

#### `product_card`
```typescript
interface ProductCardData {
  results: Array<{
    product_id: string;
    name: string;
    category: string;
    price: number;
    rating: number;
    in_stock: boolean;
    description: string;
  }>;
  total_found: number;
  query?: string;
}
```

**Visual:** Product grid (2 columns). Each: name, price in amber, rating stars, "Add to Cart" button. Out-of-stock items have a muted overlay + "Sold Out" stamp.

#### `cart_card`
```typescript
interface CartCardData {
  items: Array<{
    product_id: string;
    name: string;
    quantity: number;
    unit_price: number;
    subtotal: number;
  }>;
  item_count: number;
  total: number;
}
```

**Visual:** Line items list. Total in large amber text bottom-right. Checkout button as a full-width amber button.

#### `checkout_card`
```typescript
interface CheckoutCardData {
  order_id: string;
  status: "Confirmed";
  items: CartCardData["items"];
  total: number;
  estimated_delivery: string;
}
```

**Visual:** Confirmation screen — large ✓, order ID in mono, items summary, delivery date. Feels like a paper receipt.

---

### 8.4 Chef Cards

#### `recipe_card`
```typescript
interface RecipeCardData {
  results: Array<{
    recipe_id: string;
    name: string;
    cuisine: string;
    dietary: string[];
    prep_time_min: number;
    cook_time_min: number;
    servings: number;
    difficulty: string;
    ingredients: string[];
    steps: string[];
  }>;
  total_found: number;
}
```

**Visual:** Recipe name large + cuisine pill + dietary badges. Time stats in a row (prep + cook). Collapsed by default — click to expand steps + ingredients.

#### `nutrition_card`
```typescript
interface NutritionCardData {
  recipe_id: string;
  recipe_name: string;
  calories: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  fiber_g: number;
}
```

**Visual:** Macro bars — horizontal bars for protein, carbs, fat, fiber. Calories centered above. Clean, no decorations.

#### `meal_plan_card`
```typescript
interface MealPlanCardData {
  plan_id: string;
  days: Array<{
    day_label: string;  // "Monday"
    breakfast: { recipe_id: string; name: string };
    lunch:     { recipe_id: string; name: string };
    dinner:    { recipe_id: string; name: string };
  }>;
}
```

**Visual:** Grid by day. Each cell: meal label + recipe name. Tappable cells expand to recipe detail.

#### `shopping_list_card`
```typescript
interface ShoppingListCardData {
  plan_id: string;
  shopping_list: Array<{
    category: string;      // "Produce", "Dairy", etc.
    items: string[];
  }>;
}
```

**Visual:** Grouped by category. Category headers bold + accent color. Items as text list with checkbox-style prefixes.

---

### 8.5 Support Cards

#### `order_card`
```typescript
interface OrderCardData {
  order_id: string;
  status: string;
  items: Array<{ name: string; quantity: number; price: number }>;
  total: number;
  placed_at: string;
}
```

**Visual:** Order ID in mono top-right. Status badge (color-coded). Items list. Total bottom.

#### `ticket_card`
```typescript
interface TicketCardData {
  ticket_id: string;
  issue: string;
  priority: "low" | "medium" | "high" | "urgent";
  status: "Open" | "Escalated";
  created_at: string;
}
```

**Visual:** Ticket looks like a physical support ticket — slightly off-white background, ticket ID stamped top-right, priority as a colored left border. Status badge.

#### `kb_article_card`
```typescript
interface KbArticleCardData {
  results: Array<{
    article_id: string;
    title: string;
    snippet: string;
    category: string;
  }>;
  query: string;
}
```

**Visual:** Search result style — title bold, snippet in muted text, category pill. No borders between items.

#### `escalation_card`
```typescript
interface EscalationCardData {
  ticket_id: string;
  status: "Escalated";
  message: string;    // "A human agent will contact you within 2 hours."
}
```

**Visual:** Amber-tinted card — different from all others. Human icon. Status prominent. Message in large text. Feels urgent but calm.

---

## 9. State Canvas HUD

The state canvas is not a sidebar. It's a floating glass panel — collapsible, draggable.

**Position:** fixed, bottom-right, `32px` from edges. `320px` wide.

**Toggle:** A small ambient button (⊞) fixed bottom-right corner. When collapsed, only this button shows.

**Design:**
```css
.canvas-hud {
  position: fixed;
  bottom: 100px;
  right: 32px;
  width: 320px;
  max-height: 60vh;
  overflow-y: auto;
  background: #00000060;
  backdrop-filter: blur(24px) saturate(150%);
  border: 1px solid #ffffff0D;
  border-radius: 16px;
  padding: 16px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: var(--text-secondary);
}
```

**Content:** JSON tree view of `agentState.canvas`. Keys in amber, values in off-white. Updated live on `STATE_DELTA` / `canvas_update` events.

Animate changes: when a key's value changes, it flashes amber briefly (Framer Motion `backgroundColor` animation).

---

## 10. MCP Tool Catalog Drawer

Slides in from the right edge when the user triggers it.

**Trigger:** A small text tab on the right edge of the viewport reading "MCP ↗" rotated 90°.

**Content:** Fetched from `GET /agent/{demo}/tools` on mount.

```typescript
interface ToolCatalogEntry {
  name: string;
  description: string;
  last_called?: string;     // ISO timestamp, from client tracking
  call_count?: number;
}
```

**Design:** Full-height panel, `360px` wide. Dark background with grain. Tool entries are cards inside — name in mono + amber, description in muted text, last-called timestamp in tiny text.

When a tool call fires in the chat (via `TOOL_CALL_START`), the corresponding entry in the catalog briefly lights up (amber glow).

---

## 11. Voice Call — Cinematic Scene

This is the most important UI moment. Entering a call is a **scene change**.

### 11.1 The Cinematic Sequence

**Entering the call:**
1. User taps the voice button → 800ms transition begins
2. The entire viewport gets a slow, heavy blur (`backdrop-filter: blur(40px)`)
3. A dark overlay fades in from below (`background: var(--bg-overlay)`) — like a theater going dark
4. The voice scene components bloom into existence from center
5. Audio capture begins

**The Call Scene:**
```
[Full-viewport dark overlay]
[Grain at 2x intensity]

        [Demo name — small, muted, top-center]
        [Session timer — mono, fading]

        [PLASMA ORB — center, large, animated]

        [Phase label — below orb]
        [Last transcript — below, cinematic subtitle style]

[Controls — bottom: Mute | End Call]
```

### 11.2 Plasma Orb

Not a simple circle. The orb is a layered CSS + SVG animation that responds to audio level and call phase.

```jsx
function PlasmaOrb({ phase, audioLevel }) {
  const phaseConfig = {
    idle:          { color1: "#3A3430", color2: "#2A2420", scale: 1.0,   speed: 8 },
    listening:     { color1: "#6E8FA8", color2: "#4A6878", scale: 1.05,  speed: 4 },
    transcribing:  { color1: "#9B7EC8", color2: "#6B5E98", scale: 1.02,  speed: 6 },
    thinking:      { color1: "#E8B86D", color2: "#C49040", scale: 1.0,   speed: 3 },
    speaking:      { color1: "#7AA88A", color2: "#5A8870", scale: 1.08,  speed: 2 },
    error:         { color1: "#C4704E", color2: "#944030", scale: 0.98,  speed: 10 },
  };

  const config = phaseConfig[phase];
  const dynamicScale = 1 + (audioLevel / 255) * 0.12;

  return (
    <motion.div
      className="orb-container"
      animate={{ scale: config.scale * dynamicScale }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
    >
      {/* Core orb */}
      <motion.div
        className="orb-core"
        animate={{
          background: `radial-gradient(circle at 40% 35%, ${config.color1}, ${config.color2})`,
        }}
        transition={{ duration: 1.5, ease: "easeInOut" }}
      />
      {/* Outer glow ring */}
      <motion.div
        className="orb-glow"
        animate={{
          boxShadow: `0 0 ${60 + audioLevel / 2}px ${config.color1}60`,
          opacity: 0.6 + (audioLevel / 255) * 0.4,
        }}
      />
      {/* Plasma shimmer — SVG turbulence filter on the orb */}
      <div className="orb-shimmer" style={{ filter: "url(#plasma)" }} />
    </motion.div>
  );
}
```

```css
.orb-container {
  width: 200px;
  height: 200px;
  position: relative;
}
.orb-core {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  position: absolute;
}
.orb-glow {
  width: 140%;
  height: 140%;
  border-radius: 50%;
  position: absolute;
  top: -20%;
  left: -20%;
  pointer-events: none;
}
```

**SVG plasma filter (injected alongside grain):**
```html
<filter id="plasma">
  <feTurbulence type="turbulence" baseFrequency="0.015 0.01"
    numOctaves="2" seed="2" result="turb">
    <animate attributeName="baseFrequency"
      from="0.015 0.01" to="0.02 0.015" dur="4s" repeatCount="indefinite"/>
  </feTurbulence>
  <feDisplacementMap in="SourceGraphic" in2="turb" scale="12" />
</filter>
```

### 11.3 Phase Label

Below the orb, the current phase label animates with a letterpress-style entrance.

```jsx
const phaseLabels = {
  idle:         "Ready",
  listening:    "Listening...",
  transcribing: "Understanding...",
  thinking:     "Thinking...",
  speaking:     "Speaking",
  error:        "Connection lost",
};

<AnimatePresence mode="wait">
  <motion.span
    key={phase}
    className="phase-label"
    initial={{ opacity: 0, letterSpacing: "0.3em" }}
    animate={{ opacity: 1, letterSpacing: "0.1em" }}
    exit={{ opacity: 0, y: -8 }}
    transition={{ duration: 0.4 }}
  >
    {phaseLabels[phase]}
  </motion.span>
</AnimatePresence>
```

### 11.4 Cinematic Subtitles

The last transcript (user speech and agent response) appears in cinematic subtitle style at the bottom third of the screen.

```css
.subtitle-area {
  position: absolute;
  bottom: 140px;
  left: 50%;
  transform: translateX(-50%);
  max-width: 600px;
  text-align: center;
}
.subtitle-user {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  font-style: italic;
}
.subtitle-agent {
  font-size: var(--text-lg);
  color: var(--text-accent);
  margin-top: 8px;
  line-height: 1.5;
}
```

Subtitles appear with a cinematic fade (opacity 0→1, 300ms) and linger for 4s before fading. Each new turn replaces the previous.

### 11.5 Controls

Minimal. Two buttons only.

```jsx
<motion.div className="call-controls" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
  <button className="ctrl-mute" onClick={toggleMute}>
    {muted ? <MicOffIcon /> : <MicIcon />}
  </button>
  <button className="ctrl-end" onClick={endCall}>
    End Call
  </button>
</motion.div>
```

```css
.call-controls {
  position: absolute;
  bottom: 48px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 24px;
  align-items: center;
}
.ctrl-mute {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: #ffffff10;
  border: 1px solid #ffffff20;
  color: var(--text-primary);
}
.ctrl-end {
  padding: 12px 28px;
  border-radius: 100px;
  background: var(--accent-rust);
  color: white;
  font-weight: 500;
  border: none;
}
```

### 11.6 Exiting the Call

The reverse of entrance — the scene lifts, the blur eases away, the chat re-emerges.

---

## 12. Voice Pipeline Integration

### 12.1 REST Pipeline (Primary)

```
User speech → MediaRecorder → Blob
→ POST /api/voice/stt (multipart)
→ { transcript } → send as AG-UI message
→ agent runs → TEXT_MESSAGE_END
→ POST /api/voice/tts/stream { text }
→ StreamingResponse(audio/pcm)
→ Web Audio API (PCM → AudioContext → AudioBufferSource)
```

**Streaming PCM to Web Audio:**
```javascript
async function playStreamingTTS(text) {
  const response = await fetch(`${BASE_URL}/api/voice/tts/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });

  const sampleRate = parseInt(response.headers.get("X-Voice-Sample-Rate") ?? "24000");
  const ctx = new AudioContext({ sampleRate });
  const reader = response.body.getReader();
  let startTime = ctx.currentTime + 0.1;   // 100ms initial buffer

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    if (cancelRef.current) { reader.cancel(); break; }

    // PCM int16 → float32
    const int16 = new Int16Array(value.buffer);
    const float32 = Float32Array.from(int16, x => x / 32768);
    const buffer = ctx.createBuffer(1, float32.length, sampleRate);
    buffer.copyToChannel(float32, 0);

    const source = ctx.createBufferSource();
    source.buffer = buffer;
    source.connect(ctx.destination);
    source.start(startTime);
    startTime += buffer.duration;
    activeSources.push(source);
  }
}
```

### 12.2 WebRTC Pipeline (Optional — OpenAI Realtime)

```
POST /api/voice/realtime/session → { client_secret, session_id }
→ RTCPeerConnection
→ addTrack(localStream) + createDataChannel("oai-events")
→ createOffer → POST OpenAI /realtime → setRemoteDescription(answer)
→ dc.onopen → send session.update (transcription + VAD config)
→ conversation.item.input_audio_transcription.completed
→ forward transcript to AG-UI agent
→ agent response → POST /api/voice/tts/stream → play PCM
```

Bridge mode: `create_response: false` on the Realtime session — OpenAI only does STT, your LangGraph agent handles the response.

### 12.3 Phase State Machine

```javascript
const PHASE_TRANSITIONS = {
  idle:         ["listening"],
  listening:    ["transcribing", "idle"],
  transcribing: ["thinking", "idle"],
  thinking:     ["speaking", "idle"],
  speaking:     ["listening", "idle"],
  error:        ["idle"],
};

function transitionPhase(from, to) {
  if (!PHASE_TRANSITIONS[from].includes(to)) {
    console.warn(`Invalid phase transition: ${from} → ${to}`);
    return;
  }
  setPhase(to);
}
```

---

## 13. Example Starter Prompts

Display these in the input bar as ghost text / pill suggestions when the thread is empty:

```javascript
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
```

---

## 14. Environment Variables

```bash
VITE_AGENT_BASE_URL=http://localhost:8000
VITE_DEFAULT_DEMO=travel
```

---

## 15. File Structure Suggestion

```
frontend/
├── index.html
├── vite.config.js
├── package.json
└── src/
    ├── main.jsx
    ├── App.jsx
    ├── styles/
    │   ├── global.css         ← tokens, grain, typography
    │   ├── layout.css         ← scene, input bar, HUD
    │   └── voice.css          ← call scene
    ├── hooks/
    │   ├── useAgentStream.js  ← AG-UI integration
    │   ├── useVoiceCall.js    ← REST pipeline
    │   ├── useWebRTC.js       ← WebRTC pipeline
    │   └── useAudioLevel.js   ← mic level monitoring
    ├── components/
    │   ├── scene/
    │   │   ├── DemoSelector.jsx
    │   │   ├── DemoWatermark.jsx
    │   │   └── GrainOverlay.jsx
    │   ├── chat/
    │   │   ├── ChatThread.jsx
    │   │   ├── MessageBubble.jsx
    │   │   ├── ToolCallStamp.jsx
    │   │   ├── AgentActivity.jsx
    │   │   └── InputBar.jsx
    │   ├── cards/
    │   │   ├── CardBase.jsx   ← polaroid entrance, rotation
    │   │   ├── travel/        ← FlightCard, WeatherCard, HotelCard, ItineraryCard
    │   │   ├── trivia/        ← QuestionCard, AnswerCard, ScoreboardCard, CategoryCard
    │   │   ├── shopping/      ← ProductCard, CartCard, CheckoutCard
    │   │   ├── chef/          ← RecipeCard, NutritionCard, MealPlanCard, ShoppingListCard
    │   │   └── support/       ← OrderCard, TicketCard, KbArticleCard, EscalationCard
    │   ├── hud/
    │   │   ├── CanvasHUD.jsx  ← floating state panel
    │   │   └── ToolDrawer.jsx ← MCP catalog slide-in
    │   └── voice/
    │       ├── VoiceScene.jsx ← full-screen cinematic
    │       ├── PlasmaOrb.jsx
    │       ├── PhaseLabel.jsx
    │       ├── Subtitles.jsx
    │       └── CallControls.jsx
    ├── registry/
    │   └── cards.js           ← CARD_REGISTRY map
    └── lib/
        ├── agui.js            ← HttpAgent wrapper + event dispatch
        ├── audio.js           ← PCM streaming + AudioContext
        └── patch.js           ← JSON Patch (fast-json-patch)
```

---

## Summary Checklist

- [ ] Sandpaper grain overlay active on all surfaces
- [ ] Demo-tinted watermark fades in on selection
- [ ] No borders anywhere — depth via shadow + blur only
- [ ] Chat is full-bleed, centered column, no panel wrappers
- [ ] All 17 AG-UI event types handled
- [ ] STATE_DELTA applied via JSON Patch
- [ ] Tool calls render as stamps with streaming args
- [ ] Cards enter with Polaroid develop animation + random rotation
- [ ] All 20 card types implemented (4-6 per demo)
- [ ] Canvas HUD is floating glass panel, not a sidebar
- [ ] MCP Tool Catalog is a right-edge drawer
- [ ] Voice call is full-screen scene change (not a modal)
- [ ] Plasma orb responds to audio level + phase
- [ ] Cinematic subtitle rendering for transcript
- [ ] Streaming PCM TTS via Web Audio API (~400ms TTFA)
- [ ] WebRTC bridge mode supported (optional)
- [ ] Phase state machine with valid transition guards
- [ ] Demo-specific accent color applied throughout on selection
