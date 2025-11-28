"""
Code-aware tags for bug reporting - Assisterr Web Frontend.

Each tag maps to specific files/directories in the assisterr-web codebase,
enabling AI agents to focus on relevant code when fixing bugs.

Based on: Next.js 14 + React 18 + TypeScript + Solana Web3
"""

from typing import List, Dict, Optional

# ============================================================================
# MAIN TAGS (6-8) - Primary user-facing features
# ============================================================================

MAIN_TAGS = [
    {
        "id": "slm-models",
        "label": "🤖 SLM Models",
        "description": "Small Language Model creation, configuration, chat, and management",
        "files": [
            "src/components/slm/**",
            "src/features/**",
            "src/app/(app)/model/**",
            "src/app/(app)/ailab/**",
            "src/store/slm-*-slice.ts",
            "src/services/slm-agents.service.ts"
        ],
        "keywords": ["model", "chat", "agent", "slm", "ai model", "conversation"]
    },
    {
        "id": "auth",
        "label": "🔐 Authentication",
        "description": "Wallet connection, user registration, token management, session handling",
        "files": [
            "src/app/auth/**",
            "src/components/wallet/**",
            "src/services/auth*.ts",
            "src/middleware.ts",
            "src/hooks/useAutoAuth.ts"
        ],
        "keywords": ["login", "signup", "wallet", "connect", "authentication", "session", "token"]
    },
    {
        "id": "token-marketplace",
        "label": "💰 Token Marketplace",
        "description": "Token creation, tokenization, token trading, launch pools",
        "files": [
            "src/app/(app)/tokenize-launch/**",
            "src/components/tokenize/**",
            "src/components/create-token/**",
            "src/components/tokens/**"
        ],
        "keywords": ["token", "marketplace", "launch", "create token", "tokenize"]
    },
    {
        "id": "ai-lab",
        "label": "🧪 AI Lab",
        "description": "Community contributions (data, validation, model creation), roles/tasks",
        "files": [
            "src/app/(app)/ailab/**",
            "src/components/ailab/**",
            "src/store/ai-lab-slice.ts",
            "src/services/ai-lab.service.ts"
        ],
        "keywords": ["ai lab", "contribution", "validation", "community", "data contribution"]
    },
    {
        "id": "dashboard",
        "label": "📊 Dashboard",
        "description": "User overview, rewards, referrals, tasks, daily rewards, user verification",
        "files": [
            "src/app/(app)/dashboard/**",
            "src/components/dashboard/**",
            "src/store/tasks-v3-slice.ts",
            "src/components/tasks-v3/**"
        ],
        "keywords": ["dashboard", "rewards", "tasks", "referral", "daily reward", "overview"]
    },
    {
        "id": "trading",
        "label": "📈 Trading & Charts",
        "description": "DEX swap interface, price charts, pool analytics, volume data",
        "files": [
            "src/components/jup-studio/**",
            "src/hooks/use-pool-*",
            "src/services/coingecko.service.ts",
            "src/services/pool-events.service.ts"
        ],
        "keywords": ["swap", "trade", "dex", "chart", "price", "volume", "pool"]
    },
    {
        "id": "query-credits",
        "label": "⚡ Query Credits",
        "description": "Credit system, payment modal, credit balance management, boost mechanics",
        "files": [
            "src/components/query-credits/**",
            "src/store/query-credits-slice.ts",
            "src/services/query-credits.service.ts"
        ],
        "keywords": ["credits", "payment", "balance", "boost", "purchase"]
    },
    {
        "id": "data-market",
        "label": "📡 Data Market",
        "description": "Marketplace for data and services, airdrop management",
        "files": [
            "src/app/(app)/data-market/**",
            "src/app/(app)/airdrop/**",
            "src/services/data-market.service.ts"
        ],
        "keywords": ["data market", "marketplace", "airdrop", "services"]
    }
]

# ============================================================================
# ADDITIONAL TAGS (10-15) - Technical & edge cases
# ============================================================================

ADDITIONAL_TAGS = [
    {
        "id": "wallet-integration",
        "label": "💳 Wallet Integration",
        "description": "Solana wallet connection, balance checking, account verification",
        "files": [
            "src/components/wallet/**",
            "src/providers/AppWalletProvider.tsx",
            "src/services/balance.service.ts"
        ],
        "keywords": ["wallet", "solana", "balance", "phantom", "web3"]
    },
    {
        "id": "blockchain-rpc",
        "label": "⛓️ Blockchain RPC",
        "description": "RPC endpoints, network configuration, pool events, on-chain interactions",
        "files": [
            "src/config/network.config.ts",
            "src/services/rpc.service.ts",
            "src/services/pool-events.service.ts"
        ],
        "keywords": ["rpc", "blockchain", "network", "on-chain", "solana"]
    },
    {
        "id": "ui-components",
        "label": "🎨 UI Components",
        "description": "Shared UI library, buttons, modals, forms, tooltips",
        "files": [
            "src/shared/ui/**",
            "src/components/*/index.tsx"
        ],
        "keywords": ["button", "modal", "dialog", "tooltip", "ui", "component"]
    },
    {
        "id": "forms-validation",
        "label": "✅ Forms & Validation",
        "description": "Form handling, input validation, error messages, ZOD schemas",
        "files": [
            "src/features/**",
            "src/components/**Form**",
            "src/app/(app)/**/page.tsx"
        ],
        "keywords": ["form", "input", "validation", "error", "submit"]
    },
    {
        "id": "state-management",
        "label": "🗂️ State Management",
        "description": "Zustand store slices, state persistence, cache management",
        "files": [
            "src/store/**"
        ],
        "keywords": ["state", "zustand", "store", "cache", "persistence"]
    },
    {
        "id": "api-integration",
        "label": "🔌 API Integration",
        "description": "Backend API clients, interceptors, error handling, request/response",
        "files": [
            "src/api/**",
            "src/services/*.service.ts"
        ],
        "keywords": ["api", "fetch", "request", "response", "endpoint", "backend"]
    },
    {
        "id": "navigation-routing",
        "label": "🧭 Navigation & Routing",
        "description": "Page routing, sidebars, menus, breadcrumbs, route guards",
        "files": [
            "src/app/**layout.tsx",
            "src/components/navigation/**",
            "src/components/sidebars/**"
        ],
        "keywords": ["navigation", "menu", "sidebar", "route", "link"]
    },
    {
        "id": "performance",
        "label": "⚙️ Performance",
        "description": "Loading states, skeletons, optimization, caching, websockets",
        "files": [
            "src/hooks/use-*",
            "src/components/*/Loader.tsx",
            "src/components/monitoring/**"
        ],
        "keywords": ["slow", "loading", "performance", "lag", "freeze", "cache"]
    },
    {
        "id": "error-handling",
        "label": "🚨 Error Handling",
        "description": "Error boundaries, error messages, logging, sentry integration",
        "files": [
            "src/api/error.ts",
            "src/api/interceptors.ts",
            "sentry.*.config.ts"
        ],
        "keywords": ["error", "crash", "exception", "failed", "error message"]
    },
    {
        "id": "responsive-design",
        "label": "📱 Responsive Design",
        "description": "Mobile/tablet/desktop layouts, breakpoints, adaptive UI",
        "files": [
            "src/components/**/module.scss",
            "src/shared/ui/**"
        ],
        "keywords": ["mobile", "tablet", "responsive", "layout", "screen size"]
    },
    {
        "id": "accessibility",
        "label": "♿ Accessibility",
        "description": "Keyboard navigation, ARIA labels, screen readers, a11y compliance",
        "files": [
            "src/shared/ui/**",
            "src/components/**"
        ],
        "keywords": ["accessibility", "a11y", "keyboard", "aria", "screen reader"]
    },
    {
        "id": "real-time-data",
        "label": "📡 Real-time Data",
        "description": "WebSocket connections, live price updates, pool monitoring",
        "files": [
            "src/hooks/use-pool-websocket.ts",
            "src/hooks/use-candles-websocket.ts"
        ],
        "keywords": ["websocket", "real-time", "live", "update", "stream"]
    },
    {
        "id": "third-party",
        "label": "🔗 Third-party Integrations",
        "description": "Intercom widget, GTM, Meta Pixel, Twitter embed",
        "files": [
            "src/components/intercom/**",
            "src/app/layout.tsx",
            "src/components/marque/**"
        ],
        "keywords": ["intercom", "analytics", "gtm", "pixel", "twitter"]
    },
    {
        "id": "leaderboard",
        "label": "🏆 Leaderboard",
        "description": "Ranking system, user stats, competition mechanics",
        "files": [
            "src/app/(app)/leaderboard/**",
            "src/components/leaderboard-*/**"
        ],
        "keywords": ["leaderboard", "ranking", "score", "competition"]
    },
    {
        "id": "admin",
        "label": "👨‍💼 Admin Features",
        "description": "Commission management, admin panels, moderation",
        "files": [
            "src/app/(app)/admin/**",
            "src/services/commission.service.ts"
        ],
        "keywords": ["admin", "commission", "management", "moderation"]
    }
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_all_tags() -> List[Dict]:
    """Get all tags (main + additional)."""
    return MAIN_TAGS + ADDITIONAL_TAGS


def get_tag_by_id(tag_id: str) -> Optional[Dict]:
    """Get tag by ID."""
    all_tags = get_all_tags()
    return next((tag for tag in all_tags if tag["id"] == tag_id), None)


def get_tag_by_label(label: str) -> Optional[Dict]:
    """Get tag by label (removes emoji first)."""
    # Remove emoji and trim
    clean_label = label.split(" ", 1)[-1] if " " in label else label
    all_tags = get_all_tags()
    return next(
        (tag for tag in all_tags if tag["label"].split(" ", 1)[-1] == clean_label),
        None
    )


def get_files_for_tags(tags: List[str]) -> List[str]:
    """
    Get list of file patterns for given tags.

    Used by AI agent to focus on relevant code.

    Args:
        tags: List of tag IDs or labels

    Returns:
        List of file patterns (glob format)
    """
    files = []
    all_tags = get_all_tags()

    for tag in tags:
        # Try to find by ID first, then by label
        matching_tag = get_tag_by_id(tag.lower())
        if not matching_tag:
            matching_tag = get_tag_by_label(tag)

        if matching_tag and "files" in matching_tag:
            files.extend(matching_tag["files"])

    return list(set(files))  # Remove duplicates


def suggest_tags_from_description(description: str, console_logs: str = "") -> List[str]:
    """
    Suggest tags based on bug description and console logs.

    Uses keyword matching to suggest relevant tags.

    Args:
        description: Bug description
        console_logs: Console logs/stack trace

    Returns:
        List of suggested tag IDs
    """
    combined_text = f"{description} {console_logs}".lower()
    suggestions = []
    all_tags = get_all_tags()

    for tag in all_tags:
        if "keywords" in tag:
            for keyword in tag["keywords"]:
                if keyword.lower() in combined_text:
                    suggestions.append(tag["id"])
                    break  # Only add once per tag

    # Return unique suggestions, prioritize main tags
    main_tag_ids = [t["id"] for t in MAIN_TAGS]
    main_suggestions = [s for s in suggestions if s in main_tag_ids]
    other_suggestions = [s for s in suggestions if s not in main_tag_ids]

    return main_suggestions + other_suggestions


# ============================================================================
# CONSTANTS FOR EXPORT
# ============================================================================

# For quick access
MAIN_TAG_COUNT = len(MAIN_TAGS)
ADDITIONAL_TAG_COUNT = len(ADDITIONAL_TAGS)
TOTAL_TAG_COUNT = MAIN_TAG_COUNT + ADDITIONAL_TAG_COUNT

__all__ = [
    "MAIN_TAGS",
    "ADDITIONAL_TAGS",
    "get_all_tags",
    "get_tag_by_id",
    "get_tag_by_label",
    "get_files_for_tags",
    "suggest_tags_from_description",
]
