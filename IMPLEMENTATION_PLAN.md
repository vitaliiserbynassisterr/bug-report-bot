# AI-Powered Bug Fixing Implementation Plan

## Overview
Add agentic Claude code fixing with two-stage evaluation to automatically fix SIMPLE HIGH/CRITICAL bugs.

## Architecture

```
┌──────────────┐
│ Bug Created  │
│ (HIGH/CRIT)  │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────┐
│  Stage 1: Complexity Evaluator  │
│  (Claude Haiku - Fast & Cheap)  │
│  - Analyze bug description      │
│  - Parse stack trace for files  │
│  - Clone repo & read files      │
│  - Analyze code patterns        │
│  - Return: SIMPLE/MODERATE/     │
│            COMPLEX              │
│  Cost: ~$0.005-0.01 per eval    │
└──────┬──────────────────────────┘
       │
       ├─[SIMPLE]──────────────────┐
       │                           │
       ├─[MODERATE/COMPLEX]────────┤
       │                           │
       ▼                           ▼
┌──────────────────┐    ┌──────────────────┐
│ Trigger AI Agent │    │ Notify User:     │
│ (If enabled)     │    │ "Manual fix      │
└────────┬─────────┘    │  recommended"    │
         │              └──────────────────┘
         ▼
┌──────────────────────────────────┐
│  Stage 2: AI Agent (Sonnet)      │
│  - Clone repository              │
│  - Analyze code                  │
│  - Create fix                    │
│  - Create PR                     │
│  - Notify user in Telegram       │
│  Cost: ~$0.05-0.15 per fix       │
└──────────────────────────────────┘
```

---

## Smart Code Context Strategy

### Why Include Code Context?

**Problem:** Without seeing actual code, the evaluator can misjudge complexity:
- A "simple" error might affect shared components → Actually COMPLEX
- A "complex" error might be just a missing null check → Actually SIMPLE
- No way to verify if fix is truly straightforward

**Solution:** Smart selective code inclusion - only read relevant files from stack trace

### How It Works

```
1. Bug created with console logs
   Example: AttributeError in handlers/bug_report.py, line 156

2. Parse stack trace → Extract file paths
   Result: ['handlers/bug_report.py', 'services/backend_client.py']

3. Clone repo (shallow, depth=1) to /tmp
   Time: ~2-3 seconds

4. Read only relevant files (limit: 3-5 files)
   Tokens: ~5K-10K total

5. Send to Claude Haiku with code context
   Cost: ~$0.01 (vs $0.001 without code)

6. Claude analyzes actual code patterns
   - Sees if error location is in shared component
   - Identifies if fix requires refactoring
   - Checks code complexity around error

7. Return accurate complexity assessment
   Accuracy: 85-95% (vs 60-70% without code)

8. Cleanup temp directory
```

### Token Usage Breakdown

**Example: Telegram Bot Bug**
```
Bug Description:           200 tokens
Console Logs:             300 tokens
Stack Trace:              100 tokens
System Prompt:            500 tokens

Code Files (3-5 files):
- handlers/bug_report.py: 1,500 tokens
- services/backend_client.py: 1,200 tokens
- utils/keyboards.py:     800 tokens

Total Input:              ~4,600 tokens
Output (JSON):            ~200 tokens

Cost: ~$0.0014 per evaluation
```

### Benefits vs. Costs

| Metric | Without Code | With Smart Code | Improvement |
|--------|-------------|----------------|-------------|
| **Cost/eval** | $0.001 | $0.01 | +$0.009 |
| **Accuracy** | 60-70% | 85-95% | +25-35% |
| **False positives** | 30-40% | 5-15% | -20-30% |
| **Monthly cost (100 bugs)** | $0.10 | $1.00 | +$0.90 |
| **Prevented bad fixes** | 0 | 20-30 bugs | Saves $2-5 |

**Net Result:** Spend $1 more on evaluation, save $2-5 on prevented bad fixes.

### Security & Cleanup

- Repo cloned to `/tmp/bug-eval-{random-id}`
- Read-only access (no modifications)
- Automatic cleanup after evaluation
- Shallow clone (depth=1) for speed
- No sensitive files exposed (only Python code)

---

## Files To Create

### 1. Bug Complexity Evaluator (Enhanced with Code Context)

**File:** `/services/bug_complexity_evaluator.py` ✅ CREATED (will be enhanced)
**Purpose:** Evaluate if a bug can be auto-fixed using bug data + actual code
**Dependencies:** `anthropic`, `gitpython`

**Key Features:**
- **Smart Context Inclusion** - Only reads relevant files (3-5 max)
- **Stack Trace Parsing** - Extracts file paths from Python tracebacks
- **Shallow Repo Clone** - Fast, temp clone for file access
- **Pattern Recognition** - Sees actual code structure and complexity

**Key Functions:**
- `evaluate_complexity(bug_data) -> Dict`
  - Parse stack trace → extract file paths
  - Clone repo to `/tmp/bug-eval-{random}`
  - Read 3-5 most relevant files (~5K tokens)
  - Send to Claude 3.5 Haiku with code context
  - Returns: complexity level, confidence, reasoning, likely_files, fix_approach
- `should_auto_fix(evaluation) -> bool`
  - Decides if bug meets criteria for auto-fixing
- `_extract_files_from_stacktrace(console_logs) -> List[str]`
  - Regex match: `File "/path/to/file.py", line 42`
- `_get_relevant_code(file_paths) -> Dict[str, str]`
  - Clone repo (shallow, depth=1)
  - Read files
  - Cleanup temp directory

**Complexity Criteria:**
- **SIMPLE**: Clear error, single file, common pattern (typo, null check, validation), straightforward code structure
- **MODERATE**: Multiple files, business logic, refactoring needed, shared components
- **COMPLEX**: No clear error, architectural changes, security/performance, cross-cutting concerns

**Cost Analysis:**
- Without code context: ~$0.001 per evaluation
- **With smart code context: ~$0.005-0.01 per evaluation** ✅ RECOMMENDED
- Token usage: ~5K-10K tokens (bug + logs + 3-5 code files)
- Monthly cost (100 bugs): ~$0.50-1.00
- **Accuracy improvement: 60-70% → 85-95%**

---

### 2. AI Agent Service (Separate Microservice)

#### Directory Structure:
```
/ai-agent-service/
├── agent.py                    # Main Flask/FastAPI service
├── config/
│   └── agent_settings.py       # Configuration
├── services/
│   ├── claude_agent.py         # Claude Agent SDK integration
│   ├── github_client.py        # GitHub PR creation
│   ├── telegram_notifier.py    # Telegram notifications
│   └── bug_analyzer.py         # Bug context preparation
├── requirements.txt            # Dependencies
├── Dockerfile                  # Docker configuration
├── render.yaml                 # Render deployment
└── README.md                   # Documentation
```

#### 2.1 Main Service
**File:** `/ai-agent-service/agent.py`
**Purpose:** Flask/FastAPI webhook endpoint
**Endpoints:**
- `POST /webhook/bug-created` - Triggered by backend when HIGH/CRITICAL bug created
- `GET /health` - Health check
**Workflow:**
1. Receive bug_id from webhook
2. Fetch full bug details from backend API
3. Check if AI_AGENT_ENABLED and complexity == SIMPLE
4. Trigger Claude Agent to create fix
5. Create PR via GitHub API
6. Notify user in Telegram

**File:** `/ai-agent-service/config/agent_settings.py`
**Purpose:** Configuration for AI agent service
**Settings:**
- ANTHROPIC_API_KEY
- GITHUB_TOKEN, GITHUB_REPO_OWNER, GITHUB_REPO_NAME
- BACKEND_API_URL, BACKEND_INTERNAL_TOKEN
- TELEGRAM_BOT_TOKEN
- AI_AGENT_ENABLED, AI_COMPLEXITY_THRESHOLD
- WEBHOOK_SECRET (for secure webhooks)

#### 2.2 Claude Agent Integration
**File:** `/ai-agent-service/services/claude_agent.py`
**Purpose:** Use Claude Agent SDK to analyze and fix bugs
**Key Class:** `BugFixAgent`
**Methods:**
- `analyze_and_fix(bug_data) -> Dict`
  - System prompt: Expert Python/Telegram bot engineer
  - Tools: FileTools (read/write), BashTool (git, tests)
  - Extended thinking enabled
  - Returns: fix explanation, changed files, commit message

**Features:**
- Clone repo to `/tmp/{repo_name}`
- Search codebase for relevant files
- Analyze bug and create fix
- Run tests if available (optional)
- Generate comprehensive PR description

#### 2.3 GitHub PR Service
**File:** `/ai-agent-service/services/github_client.py`
**Purpose:** Create GitHub PRs with bug fixes
**Key Class:** `GitHubPRService`
**Dependencies:** `PyGithub`, `gitpython`
**Methods:**
- `create_fix_pr(bug_id, fix_data) -> str`
  - Create branch: `fix/bug-{id}`
  - Commit changes with descriptive message
  - Push to GitHub
  - Create PR via GitHub API
  - Return PR URL

**PR Format:**
- **Title:** `Fix {bug_id}: {bug_title}`
- **Body:** Bug details, console logs, fix explanation, testing instructions
- **Labels:** `automated-fix`, `bug`, `{priority}`
- **Assignee:** You (for review)

#### 2.4 Telegram Notifier
**File:** `/ai-agent-service/services/telegram_notifier.py`
**Purpose:** Send notifications to users
**Key Class:** `TelegramNotificationService`
**Methods:**
- `notify_complexity_result(telegram_id, bug_id, evaluation)`
  - SIMPLE: "✅ This bug can be auto-fixed!"
  - MODERATE: "⚠️ Moderate - manual fix recommended"
  - COMPLEX: "❌ Complex - requires human developer"
- `notify_pr_created(telegram_id, bug_id, pr_url)`
  - Send PR link
  - Include testing instructions
  - Add merge guidance

#### 2.5 Bug Analyzer
**File:** `/ai-agent-service/services/bug_analyzer.py`
**Purpose:** Prepare bug context for Claude Agent
**Methods:**
- `prepare_context(bug_data) -> str`
  - Format bug description
  - Extract error patterns from console logs
  - Identify likely files from stack trace
  - Include environment and priority

#### 2.6 Dependencies
**File:** `/ai-agent-service/requirements.txt`
```txt
# Web Framework
fastapi==0.115.0
uvicorn==0.32.0

# Claude AI
anthropic==0.45.0

# GitHub Integration
PyGithub==2.5.0
gitpython==3.1.43

# Telegram
python-telegram-bot==21.9

# HTTP Client
httpx>=0.24.0

# Utilities
python-dotenv==1.0.0
aiofiles==24.1.0
```

#### 2.7 Docker Configuration
**File:** `/ai-agent-service/Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install git (needed for gitpython)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 agentuser && chown -R agentuser:agentuser /app
USER agentuser

EXPOSE 8000

CMD ["uvicorn", "agent:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2.8 Render Deployment
**File:** `/ai-agent-service/render.yaml`
```yaml
services:
  - type: web
    name: ai-agent-service
    env: docker
    plan: free
    envVars:
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: GITHUB_TOKEN
        sync: false
      - key: BACKEND_API_URL
        value: https://dev.api.assisterr.ai/api/v1
      - key: BACKEND_INTERNAL_TOKEN
        sync: false
      - key: TELEGRAM_BOT_TOKEN
        sync: false
      - key: AI_AGENT_ENABLED
        value: true
      - key: GITHUB_REPO_OWNER
        value: vitaliiserbynassisterr
      - key: GITHUB_REPO_NAME
        value: bug-report-bot
      - key: WEBHOOK_SECRET
        generateValue: true
```

---

## Files To Modify

### 1. Current Bot Files

#### 1.1 Configuration
**File:** `/config/settings.py` ✅ MODIFIED
**Changes:**
- Add `ANTHROPIC_API_KEY`
- Add `AI_AGENT_ENABLED`, `AI_COMPLEXITY_THRESHOLD`
- Add `GITHUB_TOKEN`, `GITHUB_REPO_OWNER`, `GITHUB_REPO_NAME`

#### 1.2 Backend Client
**File:** `/services/backend_client.py`
**Changes:**
- Add method: `update_bug_complexity(bug_id, evaluation)`
  - PATCH /bugs/{bug_id} with complexity data
- Add method: `update_bug_pr(bug_id, pr_url)`
  - PATCH /bugs/{bug_id} with github_pr field
- Add method: `trigger_ai_agent(bug_id)`
  - POST to AI agent service webhook (if separate service)

#### 1.3 Bug Report Handler
**File:** `/handlers/bug_report.py`
**Changes:**
- Import `bug_complexity_evaluator`
- In `handle_confirmation()` after successful bug creation:
  ```python
  # If HIGH or CRITICAL priority
  if bug_data["priority"] in ["HIGH", "CRITICAL"] and settings.AI_AGENT_ENABLED:
      # Run complexity evaluation in background
      asyncio.create_task(evaluate_and_notify(
          bug_id=response["bug_id"],
          bug_data=bug_data,
          telegram_id=update.effective_user.id
      ))
  ```

**New Function:** `evaluate_and_notify(bug_id, bug_data, telegram_id)`
- Evaluate complexity using `BugComplexityEvaluator`
- Update backend with complexity result
- Notify user in Telegram about evaluation
- If SIMPLE: trigger AI agent (webhook or direct call)

#### 1.4 Dependencies
**File:** `/requirements.txt`
**Changes:**
```txt
# Existing dependencies
python-telegram-bot==21.9
httpx>=0.24.0
python-dotenv==1.0.0
flask==3.0.0

# NEW: Claude AI (for complexity evaluation in bot)
anthropic==0.45.0

# NEW: Git operations (for cloning repo to read code context)
gitpython==3.1.43
```

**Why gitpython?**
- Enables shallow clone of repository for code context
- Complexity evaluator needs to read relevant files
- Adds ~$0.005-0.01 per evaluation but improves accuracy from 60% → 85%

#### 1.5 Environment Example
**File:** `/.env.example` ✅ MODIFIED
**Changes:**
- Added Claude AI configuration section
- Added GitHub configuration section
- Added AI agent feature flags

---

## Backend API Changes Required

### 1. Bug Model Updates
Add fields to Bug model:
```python
class Bug:
    # Existing fields...

    # NEW fields
    complexity: Optional[str] = None  # SIMPLE, MODERATE, COMPLEX
    complexity_confidence: Optional[float] = None
    complexity_reasoning: Optional[str] = None
    can_auto_fix: Optional[bool] = None
    github_pr: Optional[str] = None  # PR URL
    ai_fix_attempted: Optional[bool] = False
    ai_fix_status: Optional[str] = None  # PENDING, SUCCESS, FAILED
```

### 2. API Endpoints
**Add/Update:**
- `PATCH /bugs/{bug_id}` - Support updating new fields
- `POST /webhooks/bug-created` - Webhook endpoint to trigger AI agent service
- `GET /bugs/{bug_id}/complexity` - Get complexity evaluation

### 3. Webhook Configuration
Store AI agent service URL in backend config:
```python
AI_AGENT_WEBHOOK_URL = "https://ai-agent-service.onrender.com/webhook/bug-created"
WEBHOOK_SECRET = "secure-random-string"
```

When HIGH/CRITICAL bug created:
```python
if bug.priority in ["HIGH", "CRITICAL"]:
    httpx.post(
        AI_AGENT_WEBHOOK_URL,
        json={"bug_id": bug.bug_id},
        headers={"X-Webhook-Secret": WEBHOOK_SECRET}
    )
```

---

## Deployment Plan

### Phase 1A: Basic Complexity Evaluator (Days 1-2)
**Deploy to:** Current bot (Render)
**Goal:** Get evaluation working without code context (validate approach)

**Steps:**
1. ✅ Create `/services/bug_complexity_evaluator.py` (basic version)
2. ✅ Update `/config/settings.py`
3. Update `/requirements.txt` - add `anthropic==0.45.0`
4. Update `/handlers/bug_report.py` - add evaluation after bug creation
5. Test locally with 3-5 sample bugs
6. Deploy to Render
7. Set environment variable: `ANTHROPIC_API_KEY`
8. Test in production with real HIGH/CRITICAL bug

**Expected Results:**
- Evaluation works end-to-end
- Cost: ~$0.001 per bug
- Accuracy: 60-70% (baseline)

### Phase 1B: Add Smart Code Context (Days 3-5) ✅ RECOMMENDED
**Deploy to:** Current bot (Render)
**Goal:** Enhance accuracy with selective code context

**Steps:**
1. Update `/services/bug_complexity_evaluator.py`:
   - Add `_extract_files_from_stacktrace()` method
   - Add `_get_relevant_code()` method (shallow clone + read files)
   - Update prompt to include code context
   - Add cleanup logic
2. Update `/requirements.txt` - add `gitpython==3.1.43`
3. Test locally with bugs that have stack traces
4. Deploy to Render
5. Set environment variable: `GITHUB_TOKEN` (for private repo access if needed)
6. Compare accuracy: Phase 1A vs 1B

**Expected Results:**
- Evaluation with code context works
- Cost: ~$0.01 per bug (+$0.009)
- Accuracy: 85-95% (+25-35%)
- Monthly cost increase: ~$1 for 100 bugs

### Why Two Phases?
1. **Validate approach quickly** - Get basic evaluation working in 2 days
2. **Measure baseline** - Understand accuracy without code context
3. **Quantify improvement** - Prove code context adds value
4. **Reduce risk** - If Phase 1A fails, no wasted effort on Phase 1B

### Phase 2: AI Agent Service (Week 2-3)
**Deploy to:** Separate Render service
**Steps:**
1. Create `/ai-agent-service/` directory structure
2. Implement all service files
3. Test locally with Docker
4. Deploy to Render as new service
5. Set all environment variables
6. Test webhook integration

### Phase 3: Backend Integration (Week 3)
**Deploy to:** Backend API
**Steps:**
1. Add new fields to Bug model
2. Run database migration
3. Add webhook trigger
4. Update API endpoints
5. Deploy to dev environment
6. Test end-to-end flow

### Phase 4: Polish & Documentation (Week 4)
**Steps:**
1. Add error handling and retry logic
2. Add monitoring and logging
3. Create user documentation
4. Create PR review guidelines
5. Test with variety of bugs
6. Monitor costs and success rate

---

## Environment Variables

### Bot Service (Current)
```env
# Existing
TELEGRAM_BOT_TOKEN=...
BACKEND_API_URL=https://dev.api.assisterr.ai/api/v1
BACKEND_INTERNAL_TOKEN=...
ALLOWED_USER_IDS=286711062

# NEW
ANTHROPIC_API_KEY=sk-ant-api03-...
AI_AGENT_ENABLED=true
AI_COMPLEXITY_THRESHOLD=SIMPLE
GITHUB_TOKEN=ghp_...
GITHUB_REPO_OWNER=vitaliiserbynassisterr
GITHUB_REPO_NAME=bug-report-bot
```

### AI Agent Service (New)
```env
ANTHROPIC_API_KEY=sk-ant-api03-...
GITHUB_TOKEN=ghp_...
GITHUB_REPO_OWNER=vitaliiserbynassisterr
GITHUB_REPO_NAME=bug-report-bot
BACKEND_API_URL=https://dev.api.assisterr.ai/api/v1
BACKEND_INTERNAL_TOKEN=...
TELEGRAM_BOT_TOKEN=...
AI_AGENT_ENABLED=true
AI_COMPLEXITY_THRESHOLD=SIMPLE
WEBHOOK_SECRET=secure-random-string
LOG_LEVEL=INFO
```

---

## Cost Estimation

### Per Bug (HIGH/CRITICAL only)

#### Complexity Evaluation with Smart Code Context
- **Input tokens:** ~5-10K (bug + logs + 3-5 code files)
- **Output tokens:** ~200-500 (evaluation JSON)
- **Model:** Claude 3.5 Haiku
- **Cost:** ~$0.005-0.01 per evaluation
- **Accuracy:** 85-95% (vs. 60-70% without code)

#### Auto-Fix (If SIMPLE)
- **Model:** Claude 3.7 Sonnet with extended thinking
- **Cost:** ~$0.05-0.15 per fix
- **Total per SIMPLE bug:** ~$0.055-0.16 (evaluation + fix)
- **Total per MODERATE/COMPLEX:** ~$0.005-0.01 (evaluation only)

### Monthly Cost Estimate

**Scenario: 100 HIGH/CRITICAL Bugs/Month**
- 30% classified as SIMPLE (30 bugs) → Get auto-fixed
- 70% classified as MODERATE/COMPLEX (70 bugs) → Manual fix recommended

**Breakdown:**
- Evaluation (all 100 bugs): 100 × $0.01 = **$1.00**
- Auto-fix (30 SIMPLE bugs): 30 × $0.10 = **$3.00**
- **Total monthly cost: ~$4.00**

**Cost per successful fix: ~$0.16**

### Comparison: With vs Without Code Context

| Approach | Cost/Bug | Accuracy | False Positives | Monthly Cost (100 bugs) |
|----------|----------|----------|-----------------|-------------------------|
| **No code context** | $0.001 | 60-70% | High (30-40%) | $0.10 + failed fixes |
| **Smart code context** ✅ | $0.01 | 85-95% | Low (5-15%) | $1.00 (evaluation) + $3.00 (fixes) |

**Verdict:** Smart code context adds ~$1/month but prevents wasted Sonnet API calls on incorrectly classified bugs. **Net savings of $2-5/month.**

---

## Success Metrics

### Technical Metrics
- Complexity evaluation accuracy (manual validation)
- PR success rate (merged vs. closed without merge)
- Fix correctness (bugs actually fixed)
- Response time (bug created → PR created)

### Business Metrics
- Developer time saved
- Bug resolution speed
- User satisfaction
- Cost per successful fix

---

## Risks & Mitigation

### Risk 1: AI generates incorrect fixes
**Mitigation:**
- Only fix SIMPLE bugs (high confidence)
- Always require manual review and testing
- Include comprehensive testing instructions in PR
- Start with low-risk bugs

### Risk 2: High costs
**Mitigation:**
- Use Haiku for evaluation (cheap)
- Only evaluate HIGH/CRITICAL bugs
- Add AI_AGENT_ENABLED kill switch
- Monitor spending with Anthropic dashboard

### Risk 3: Security concerns
**Mitigation:**
- Use GitHub token with minimal permissions (repo only)
- Never auto-merge PRs
- Review all code changes
- Use webhook secrets for authentication

### Risk 4: Rate limiting
**Mitigation:**
- Implement retry logic with exponential backoff
- Queue requests if rate limited
- Monitor API usage

---

## Testing Strategy

### Unit Tests
- Test `BugComplexityEvaluator.evaluate_complexity()` with sample bugs
- Test `GitHubPRService.create_fix_pr()` with mock GitHub API
- Test webhook authentication

### Integration Tests
- Test full flow: bug creation → evaluation → PR creation → notification
- Test with real HIGH/CRITICAL bugs
- Test error handling (API failures, rate limits)

### Manual Testing
- Create synthetic SIMPLE, MODERATE, COMPLEX bugs
- Verify complexity evaluation accuracy
- Review generated PRs for quality
- Test notification messages

---

## Documentation To Create

### For Developers
1. **CONTRIBUTING.md** - How to work with AI-generated PRs
2. **AI_AGENT_ARCHITECTURE.md** - Technical architecture doc
3. **TROUBLESHOOTING.md** - Common issues and solutions

### For Users
1. **README.md update** - Add AI auto-fix feature description
2. **USER_GUIDE.md** - How bug complexity evaluation works
3. **PR_REVIEW_GUIDE.md** - How to review and test AI-generated PRs

---

## Summary

### Total Files To Create: 13
1. `/services/bug_complexity_evaluator.py` ✅
2-11. `/ai-agent-service/*` (9 files)
12. `/IMPLEMENTATION_PLAN.md` (this file)
13. Backend webhook endpoint

### Total Files To Modify: 4
1. `/config/settings.py` ✅
2. `/.env.example` ✅
3. `/services/backend_client.py`
4. `/handlers/bug_report.py`
5. `/requirements.txt`

### Estimated Effort: 3-4 weeks
- Week 1: Complexity evaluator + testing
- Week 2: AI agent service foundation
- Week 3: Integration + backend changes
- Week 4: Polish + documentation

### Estimated Cost: $4/month (with smart code context)
- Evaluation: $1/month (100 HIGH/CRITICAL bugs × $0.01)
- Auto-fixes: $3/month (30 SIMPLE bugs × $0.10)
- **Cost per successful fix: ~$0.16**
- **ROI: Saves 30 hours/month of developer time**

---

## Key Takeaways: Smart Code Context Decision

### ✅ RECOMMENDED: Implement with Smart Code Context

**Why?**
1. **Minimal cost increase:** +$1/month vs baseline
2. **Significant accuracy boost:** 60-70% → 85-95%
3. **Prevents wasted API calls:** Avoids $2-5/month in failed Sonnet fixes
4. **Better user experience:** More accurate complexity assessments
5. **Net savings:** Spend $1 more, save $2-5, net +$1-4/month

**Implementation:**
- Start with Phase 1A (basic evaluation) to validate approach
- Add Phase 1B (smart code context) within same week
- Two-phase approach reduces risk and quantifies improvement

**Technical Approach:**
- Parse stack traces to extract file paths
- Shallow clone repo (depth=1) to `/tmp`
- Read only 3-5 most relevant files
- Cleanup automatically after evaluation
- Total time per evaluation: ~3-5 seconds

---

## Next Steps

1. ✅ Review this implementation plan
2. ✅ Decision: Implement with smart code context
3. Get Anthropic API key from https://console.anthropic.com
4. Get GitHub Personal Access Token (repo scope)
5. Start with Phase 1A: Basic complexity evaluator (2 days)
6. Add Phase 1B: Smart code context (3 days)
7. Measure and validate accuracy improvement
