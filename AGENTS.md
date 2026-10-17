# AGENTS.md — Universal CRO & Checkout Funnel Audit (Codex/Cowork/Antigravity Entry Point)

This file enables autonomous, rigorous, zero-hallucination CRO and Checkout Funnel Audits.
**`SKILL_CRO_CHECKOUT_AUDIT.md` in this directory is the single source of truth.**

## When to activate
When the user asks to:
- Audit checkout flow or cart friction (*فحص صفحة الدفع*, *تدقيق السلة*)
- Optimize conversion rate (*تحسين معدل التحويل*, *CRO Audit*)
- Diagnose checkout abandonment (*تشخيص أسباب إلغاء الشراء*, *Cart Abandonment*)
- Audit lead capture or booking funnels (*فحص نماذج العملاء أو الحجز*)
- Inspect forms, input fields, autocomplete, or payment gateways
→ **Open `SKILL_CRO_CHECKOUT_AUDIT.md` in this folder and follow it step by step.**

## Non-negotiables
- **NEVER hallucinate data.** Use ONLY live numbers from the scripts (`scripts/audit_checkout.py`) or user-provided screenshots.
- Move **one phase at a time**. Complete each phase, show results with verified evidence, and enforce mechanical locks (17 Locks).
- Enforce **LOCK 55 (Devil's Advocate Court):** Self-interrogate assumptions and verify regional legal mandates before finalizing report.
- Enforce **LOCK 56 (Dual Delivery):** Deliver production code for custom stacks, and click-by-click dashboard instructions for page builders / SaaS (Salla, Zid, Shopify, WooCommerce).
- Enforce **LOCK 57 (Proof-by-Quote):** Direct verbatim DOM tag citations for all claims.
- Zero generic fluff advice (no "make buttons red" or "improve design").

## Quick Start
```powershell
# 1. Audit checkout or website funnel (Stealth Mode)
$env:PYTHONIOENCODING="utf-8"; py scripts/audit_checkout.py <URL>

# 2. For SPA / React / Next.js / Cloudflare-protected sites
$env:PYTHONIOENCODING="utf-8"; py scripts/audit_checkout.py <URL> --playwright

# 3. Calculate friction drop-off and generate developer code
$env:PYTHONIOENCODING="utf-8"; py scripts/funnel_analyzer.py --fields 12 --traffic 30000 --aov 150
```

Read `SCRIPTS_GUIDE.md` for complete CLI arguments and failure handling.
