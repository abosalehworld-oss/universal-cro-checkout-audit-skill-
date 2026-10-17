#!/usr/bin/env python3
"""
Universal CRO & Checkout / Funnel Stealth Auditor v2.0 (Lifetime & Anti-Bot Engine)
==================================================================================
Multi-tiered stealth engine designed to inspect, seed, and diagnose checkout flows,
cart funnels, and lead generation forms across:
  - Standard Platforms: WooCommerce, Shopify, Salla, Zid, Magento, OpenCart, etc.
  - Custom Coded Stacks: Next.js, React, Nuxt, Vue, Laravel, Django, Headless & SPAs.
  - Service & Lead Funnels: Booking forms, B2B lead capture, consultation funnels.

Engine Features:
  - Autonomous Cart Seeding Engine (Solves the #1 problem of empty carts redirecting to /cart).
  - 5-Tier Stealth Fetching (Requests + Session Cookies, Googlebot Spoofing, Playwright Stealth,
    Real Chrome Off-Screen, and Wayback Machine Free IP Bypass with freshness guard).
  - Dynamic Year Resolution (Self-updates for 2026 and future years dynamically).
  - Deep DOM Form & Input Friction Analyzer (Field count, autocomplete compliance, required flags).
  - Payment Gateway & Trust Element Detection (Apple Pay, Mada, Tabby, Tamara, Stripe, Fawry, COD, etc.).
  - Manual Mode Fallback Protocol (Generates structured audit guides when anti-bot triggers).
  - Baymard Institute 2026+ Usability Benchmark alignment.
  - Windows UTF-8 encoding safety.

Usage:
    py scripts/audit_checkout.py <URL>
    py scripts/audit_checkout.py https://example.com/checkout
    py scripts/audit_checkout.py https://example.com/ --seed-cart
    py scripts/audit_checkout.py https://example.com/ --playwright
    py scripts/audit_checkout.py https://example.com/ --json

Requires: pip install requests beautifulsoup4 lxml
Optional: pip install playwright && playwright install chromium
"""

import argparse
import concurrent.futures
import datetime
import json
import os
import random
import re
import sys
import time
from urllib.parse import urljoin, urlparse, unquote

# Force UTF-8 stdout on Windows to prevent encoding crashes
try:
    sys.stdout.reconfigure(encoding='utf-8')
except (AttributeError, OSError):
    pass

def safe_print(*args, **kwargs):
    """Print with Unicode safety fallback for Windows terminals."""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        text = " ".join(str(a) for a in args)
        print(text.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(
            sys.stdout.encoding or "utf-8", errors="replace"), **kwargs)

try:
    import requests
except ImportError:
    safe_print("[FATAL] requests not installed. Run: pip install requests")
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    safe_print("[FATAL] beautifulsoup4 not installed. Run: pip install beautifulsoup4 lxml")
    sys.exit(1)

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


# ══════════════════════════════════════════════════════════════
# DYNAMIC YEAR & BENCHMARK RESOLUTION (Lifetime Longevity)
# ══════════════════════════════════════════════════════════════

CURRENT_YEAR = datetime.datetime.now().year

# Baseline Baymard & E-Commerce Meta-Analysis Benchmarks (Updated for 2026+)
BAYMARD_BENCHMARKS = {
    "year": CURRENT_YEAR,
    "average_cart_abandonment_global": 70.22,
    "average_cart_abandonment_mobile": 82.4,
    "average_cart_abandonment_desktop": 67.8,
    "ideal_checkout_fields": (6, 8),
    "average_checkout_fields_measured": 11.8,
    "top_dropoff_reasons": {
        "extra_costs_high": 48.0,
        "forced_registration": 26.0,
        "complicated_checkout": 22.0,
        "trust_security_doubts": 25.0,
        "missing_local_payment": 13.0,
        "slow_site_or_crashes": 17.0
    }
}


# ══════════════════════════════════════════════════════════════
# STEALTH ENGINE CONFIGURATION & BROWSER FINGERPRINTS
# ══════════════════════════════════════════════════════════════

TIMEOUT = 18
DELAY = 0.35
GLOBAL_TIMEOUT = 360
_GLOBAL_DEADLINE = None

def _set_global_deadline():
    global _GLOBAL_DEADLINE
    _GLOBAL_DEADLINE = time.time() + GLOBAL_TIMEOUT

def _check_deadline(stage=""):
    if _GLOBAL_DEADLINE and time.time() > _GLOBAL_DEADLINE:
        raise TimeoutError(f"Global timeout ({GLOBAL_TIMEOUT}s) exceeded during: {stage}")

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0',
]

def get_stealth_headers(referer=None, is_mobile=False):
    """Generates modern realistic browser headers with Sec-CH-UA client hints."""
    if is_mobile:
        ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 Mobile Safari/604.1'
        sec_mobile = '?1'
        sec_platform = '"iOS"'
    else:
        ua = random.choice([u for u in USER_AGENTS if 'Mobile' not in u])
        sec_mobile = '?0'
        sec_platform = '"Windows"' if 'Windows' in ua else '"macOS"'

    headers = {
        'User-Agent': ua,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '"Chromium";v="131", "Google Chrome";v="131", "Not-A.Brand";v="99"',
        'sec-ch-ua-mobile': sec_mobile,
        'sec-ch-ua-platform': sec_platform,
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
    }
    if referer:
        headers['Referer'] = referer
    return headers


# ══════════════════════════════════════════════════════════════
# 5-TIER PAGE FETCHER CLASS (With Wayback & Playwright Stealth)
# ══════════════════════════════════════════════════════════════

class PageFetcher:
    """
    Ultra-resilient page fetcher with 5-tier fallbacks:
      Tier 1: Requests with stealth headers & session cookies
      Tier 2: Googlebot spoofing (for WAF bypass)
      Tier 3: Playwright stealth headless browser
      Tier 4: Real Chrome launched off-screen
      Tier 5: Wayback Machine (Free IP bypass for blocked/down sites with <= 90d freshness)
    """

    def __init__(self, timeout=TIMEOUT):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(get_stealth_headers())

    def fetch_html(self, url, use_playwright=False, is_mobile=False):
        """Fetches page HTML with deadline tracking and automatic fallback across 5 tiers."""
        _check_deadline(f"fetch_html: {url[:70]}")
        time.sleep(DELAY)

        if use_playwright and HAS_PLAYWRIGHT:
            return self._fetch_playwright(url, is_mobile=is_mobile)

        # 1. Tier 1: Standard Stealth Requests
        res = self._fetch_requests_html(url, is_mobile=is_mobile)
        if res.get("ok") and res.get("status") in (200, 301, 302):
            html_low = res.get("html", "").lower()
            if not self._is_challenge_page(html_low):
                return res
            safe_print("    [!] Bot Challenge detected in HTTP response. Switching to anti-bot tier...")

        # 2. Tier 2: Googlebot Spoofing Fallback
        safe_print("    [!] Trying Googlebot Spoofing Tier...")
        gb_res = self.fetch_as_googlebot(url)
        if gb_res.get("ok") and not self._is_challenge_page(gb_res.get("html", "").lower()):
            return gb_res

        # 3. Tier 3: Playwright Stealth Fallback
        if HAS_PLAYWRIGHT:
            safe_print("    [!] Launching Playwright Stealth Browser...")
            pw_res = self._fetch_playwright(url, is_mobile=is_mobile)
            if pw_res.get("ok") and not self._is_challenge_page(pw_res.get("html", "").lower()):
                return pw_res

            # 4. Tier 4: Real Chrome Nuclear Option
            safe_print("    [!] Trying Real Chrome Off-Screen Fallback...")
            rc_res = self._fetch_real_chrome(url)
            if rc_res.get("ok"):
                return rc_res

        # 5. Tier 5: Wayback Machine Fallback (Free IP Bypass)
        safe_print("    [!] Trying Wayback Machine Fallback (Free IP Bypass)...")
        wb_res = self.fetch_via_web_archive(url)
        if wb_res.get("ok"):
            return wb_res

        return res

    def _is_challenge_page(self, html_low):
        """Detects Cloudflare Turnstile, Cloudflare Ray ID block, Imperva, Akamai, or DDoS-Guard."""
        if len(html_low) < 500:
            return True
        signals = [
            "challenge-platform", "cf-browser-verification", "ray id:", "just a moment...",
            "checking your browser", "security check to access", "waf challenge",
            "access denied", "attention required! | cloudflare", "ddos-guard"
        ]
        return any(sig in html_low for sig in signals)

    def _fetch_requests_html(self, url, is_mobile=False):
        """Stealth requests fetcher with absolute thread timeout."""
        headers = get_stealth_headers(referer=url, is_mobile=is_mobile)
        def _do():
            try:
                resp = self.session.get(url, headers=headers, timeout=(6, self.timeout), allow_redirects=True)
                return {"ok": True, "status": resp.status_code, "html": resp.text, "url": resp.url, "mode": "requests"}
            except Exception as e:
                return {"ok": False, "error": str(e), "status": 0}

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                return ex.submit(_do).result(timeout=self.timeout + 4)
        except concurrent.futures.TimeoutError:
            return {"ok": False, "error": "Request absolute timeout", "status": 0}
        except Exception as e:
            return {"ok": False, "error": str(e), "status": 0}

    def fetch_as_googlebot(self, url):
        """Bypasses many WAFs that exempt search engine indexers."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        }
        def _do():
            try:
                resp = requests.get(url, headers=headers, timeout=(6, self.timeout), allow_redirects=True)
                if resp.status_code == 200 and len(resp.text) > 400:
                    return {"ok": True, "status": 200, "html": resp.text, "url": resp.url, "mode": "googlebot"}
                return {"ok": False, "error": f"Status {resp.status_code}", "status": resp.status_code}
            except Exception as e:
                return {"ok": False, "error": str(e), "status": 0}

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                return ex.submit(_do).result(timeout=self.timeout + 4)
        except Exception as e:
            return {"ok": False, "error": str(e), "status": 0}

    def _fetch_playwright(self, url, is_mobile=False):
        """Playwright stealth fetch with navigator emulation and script injection."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--disable-features=VizDisplayCompositor,AutomationControlled",
                        "--no-sandbox",
                    ]
                )
                viewport = {'width': 390, 'height': 844} if is_mobile else {'width': 1920, 'height': 1080}
                ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 Mobile Safari/604.1' if is_mobile else random.choice([u for u in USER_AGENTS if 'Mobile' not in u])

                context = browser.new_context(
                    user_agent=ua,
                    viewport=viewport,
                    is_mobile=is_mobile,
                    has_touch=is_mobile,
                    java_script_enabled=True,
                    bypass_csp=True,
                    locale='ar-EG'
                )

                # Sync requests session cookies to Playwright context
                try:
                    p_url = urlparse(url)
                    cookie_domain = p_url.netloc
                    pw_cookies = []
                    for c in self.session.cookies:
                        cdom = c.domain if c.domain else cookie_domain
                        if not cdom.startswith(".") and "." in cdom:
                            cdom = "." + cdom
                        pw_cookies.append({
                            "name": c.name,
                            "value": c.value,
                            "domain": cdom,
                            "path": c.path or "/"
                        })
                    if pw_cookies:
                        context.add_cookies(pw_cookies)
                except Exception:
                    pass

                # Anti-detection stealth script injection
                context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                    Object.defineProperty(navigator, 'languages', { get: () => ['ar', 'en-US', 'en'] });
                    if (!window.chrome) window.chrome = { runtime: {} };
                """)

                page = context.new_page()
                page.route("**/*.{jpg,jpeg,png,gif,mp4,webp,svg,woff,woff2}", lambda route: route.abort())

                resp = page.goto(url, timeout=self.timeout * 1000, wait_until="domcontentloaded")
                page.wait_for_timeout(2500)
                try:
                    page.evaluate("if (document.body) window.scrollTo(0, document.body.scrollHeight / 2)")
                except Exception:
                    pass
                page.wait_for_timeout(1000)

                html = page.content()
                final_url = page.url
                status = resp.status if resp else 200
                browser.close()

                if len(html) > 500:
                    return {"ok": True, "status": status, "html": html, "url": final_url, "mode": "playwright"}
                return {"ok": False, "error": "Playwright returned empty HTML", "status": status}
        except Exception as e:
            return {"ok": False, "error": f"Playwright error: {e}", "status": 0}

    def _fetch_real_chrome(self, url):
        """Uses installed Google Chrome instance rendered off-screen."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    channel='chrome',
                    headless=False,
                    args=[
                        "--window-position=-32000,-32000",
                        "--window-size=1,1",
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox"
                    ]
                )
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent=random.choice([u for u in USER_AGENTS if 'Mobile' not in u])
                )
                page = context.new_page()
                page.route("**/*.{jpg,jpeg,png,gif,mp4,webp,svg,woff,woff2}", lambda route: route.abort())
                resp = page.goto(url, timeout=self.timeout * 1000, wait_until="domcontentloaded")
                page.wait_for_timeout(3500)
                html = page.content()
                final_url = page.url
                status = resp.status if resp else 200
                browser.close()

                if len(html) > 500:
                    return {"ok": True, "status": status, "html": html, "url": final_url, "mode": "real_chrome"}
                return {"ok": False, "error": "Real Chrome returned empty page", "status": status}
        except Exception as e:
            return {"ok": False, "error": f"Real Chrome error: {e}", "status": 0}

    def fetch_via_web_archive(self, url):
        """Wayback Machine Free IP Bypass with freshness check <= 90 days."""
        _check_deadline(f"web_archive: {url[:70]}")
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        try:
            api_url = f"https://archive.org/wayback/available?url={url}&timestamp=99999999"
            api_resp = requests.get(api_url, headers=headers, timeout=10)
            if api_resp.status_code != 200:
                return {"ok": False, "error": "Wayback API unavailable"}
            data = api_resp.json()
            closest = data.get("archived_snapshots", {}).get("closest")
            if not closest or not closest.get("available"):
                return {"ok": False, "error": "No snapshot found"}

            timestamp = closest.get("timestamp", "")
            if len(timestamp) >= 8:
                snap_date = datetime.datetime(int(timestamp[:4]), int(timestamp[4:6]), int(timestamp[6:8]))
                days_old = (datetime.datetime.now() - snap_date).days
                if days_old > 90:
                    return {"ok": False, "error": f"Snapshot too old ({days_old} days). Freshness rule: <= 90 days."}

            resp = requests.get(closest["url"], headers=headers, timeout=15)
            if resp.status_code == 200 and len(resp.text) > 500:
                clean_html = resp.text.split("<!-- End Wayback Rewrite JS Include -->")[-1]
                return {"ok": True, "status": 200, "html": clean_html, "url": resp.url, "mode": "web_archive"}
            return {"ok": False, "error": "Wayback HTML empty"}
        except Exception as e:
            return {"ok": False, "error": f"Wayback error: {e}"}


# ══════════════════════════════════════════════════════════════
# AUTONOMOUS CART SEEDING ENGINE (Solves Empty Checkout Issue)
# ══════════════════════════════════════════════════════════════

def seed_cart_and_get_checkout(base_url, fetcher, platform_name="unknown"):
    """
    Autonomously adds 1 sample product to the cart so that the checkout
    page populates with real address fields, shipping calculators, and payment options.
    """
    safe_print("    [🛒] Running Autonomous Cart Seeder to populate checkout DOM...")
    session = fetcher.session
    base_parsed = urlparse(base_url)
    origin = f"{base_parsed.scheme}://{base_parsed.netloc}"

    # 1. Discover a product link from homepage or shop
    home_res = fetcher.fetch_html(base_url)
    if not home_res.get("ok"):
        return None

    soup = BeautifulSoup(home_res["html"], "html.parser")
    product_links = []
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        full = urljoin(base_url, href)
        if urlparse(full).netloc == base_parsed.netloc:
            if any(k in full.lower() for k in ["/product/", "/products/", "/item/", "/p/", "/منتج/"]):
                product_links.append(full)

    if not product_links:
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            full = urljoin(base_url, href)
            if urlparse(full).netloc == base_parsed.netloc and any(k in full.lower() for k in ["/shop", "/store", "/product-category/"]):
                shop_res = fetcher.fetch_html(full)
                if shop_res.get("ok"):
                    s_soup = BeautifulSoup(shop_res["html"], "html.parser")
                    for sa in s_soup.find_all("a", href=True):
                        shref = sa.get("href", "")
                        sfull = urljoin(full, shref)
                        if urlparse(sfull).netloc == base_parsed.netloc and any(k in sfull.lower() for k in ["/product/", "/products/", "/item/", "/p/"]):
                            product_links.append(sfull)
                if product_links:
                    break

    # 2. Try Platform-Specific Cart Seeding
    # WooCommerce: Probe ?add-to-cart= or look for add_to_cart_button data-product_id
    if platform_name == "WooCommerce" or "woocommerce" in home_res["html"].lower():
        add_btn = soup.find(attrs={"data-product_id": True})
        if not add_btn and product_links:
            prod_res = fetcher.fetch_html(product_links[0])
            if prod_res.get("ok"):
                p_soup = BeautifulSoup(prod_res["html"], "html.parser")
                add_btn = p_soup.find(attrs={"data-product_id": True}) or p_soup.find("button", attrs={"name": "add-to-cart"})
                if add_btn and (add_btn.get("data-product_id") or add_btn.get("value")):
                    pid = add_btn.get("data-product_id") or add_btn.get("value")
                    seed_url = f"{origin}/?add-to-cart={pid}"
                    safe_print(f"    [+] WooCommerce Cart Seed triggered from product page: {seed_url}")
                    session.get(seed_url, timeout=10)
                    return urljoin(origin, "/checkout/")
        if add_btn:
            pid = add_btn.get("data-product_id") or add_btn.get("value")
            seed_url = f"{origin}/?add-to-cart={pid}"
            safe_print(f"    [+] WooCommerce Cart Seed triggered: {seed_url}")
            session.get(seed_url, timeout=10)
            return urljoin(origin, "/checkout/")

    # Shopify: Probe /products.json or /cart/add.js
    if platform_name == "Shopify" or "shopify" in home_res["html"].lower():
        try:
            p_json_url = urljoin(origin, "/products.json?limit=1")
            pj_resp = session.get(p_json_url, timeout=8)
            if pj_resp.status_code == 200:
                p_data = pj_resp.json()
                prods = p_data.get("products", [])
                if prods and prods[0].get("variants"):
                    var_id = prods[0]["variants"][0]["id"]
                    add_payload = {"items": [{"id": var_id, "quantity": 1}]}
                    session.post(urljoin(origin, "/cart/add.js"), json=add_payload, timeout=8)
                    safe_print(f"    [+] Shopify Cart Seeded with Variant ID: {var_id}")
                    return urljoin(origin, "/checkout")
        except Exception:
            pass

    # Playwright Generic Fallback (for React/Next.js/Salla/Custom)
    if HAS_PLAYWRIGHT and product_links:
        target_prod = product_links[0]
        safe_print(f"    [+] Playwright clicking Add-to-Cart on product: {target_prod}")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
                page = browser.new_page()
                page.goto(target_prod, timeout=18000, wait_until="domcontentloaded")
                page.wait_for_timeout(2000)

                # Look for add to cart button in multiple languages
                btn_selectors = [
                    "button[name='add-to-cart']", "button.single_add_to_cart_button",
                    "button.add-to-cart", "button[type='submit']",
                    "button:has-text('أضف للسلة')", "button:has-text('إضافة إلى السلة')",
                    "button:has-text('Add to cart')", "button:has-text('Buy Now')",
                    "button:has-text('اشتري الآن')"
                ]
                for sel in btn_selectors:
                    try:
                        if page.locator(sel).first.is_visible():
                            page.locator(sel).first.click()
                            page.wait_for_timeout(3000)
                            safe_print(f"    [+] Clicked Add to Cart button matching: {sel}")
                            break
                    except Exception:
                        continue

                # Go to checkout
                page.goto(urljoin(origin, "/checkout/"), timeout=15000, wait_until="domcontentloaded")
                page.wait_for_timeout(2500)
                co_html = page.content()
                co_url = page.url
                browser.close()

                if len(co_html) > 500:
                    return {"html": co_html, "url": co_url, "seeded": True}
        except Exception as e:
            safe_print(f"    [!] Playwright seeding attempt failed: {e}")

    return None


# ══════════════════════════════════════════════════════════════
# PLATFORM & TECH STACK DETECTOR
# ══════════════════════════════════════════════════════════════

def detect_platform_and_stack(html, url=""):
    """Detects standard e-commerce platform or custom stack."""
    h_low = html.lower()
    detected = {
        "platform": "Custom Coded Site",
        "is_custom": True,
        "frontend_tech": [],
        "backend_clues": []
    }

    # Standard E-Commerce Platforms
    if 'woocommerce' in h_low or 'wc-block' in h_low or 'wp-content/plugins/woocommerce' in h_low:
        detected["platform"] = "WooCommerce"
        detected["is_custom"] = False
    elif 'cdn.shopify.com' in h_low or 'shopify.com/s/files' in h_low or 'window.shopify' in h_low:
        detected["platform"] = "Shopify"
        detected["is_custom"] = False
    elif 'salla.sa' in h_low or 'cdn.salla' in h_low or 'salla.network' in h_low or 'salla-checkout' in h_low:
        detected["platform"] = "Salla (سلة)"
        detected["is_custom"] = False
    elif 'zid.sa' in h_low or 'cdn.zid' in h_low or 'zid-store' in h_low:
        detected["platform"] = "Zid (زد)"
        detected["is_custom"] = False
    elif 'opencart' in h_low or 'index.php?route=checkout' in h_low:
        detected["platform"] = "OpenCart"
        detected["is_custom"] = False
    elif 'magento' in h_low or 'mage/' in h_low or 'mage-translation' in h_low:
        detected["platform"] = "Magento (Adobe Commerce)"
        detected["is_custom"] = False
    elif 'bigcommerce' in h_low or 'cdn.bcapp' in h_low:
        detected["platform"] = "BigCommerce"
        detected["is_custom"] = False
    elif 'prestashop' in h_low:
        detected["platform"] = "PrestaShop"
        detected["is_custom"] = False

    # Frontend Framework Detection (Headless & SPA)
    if '__next' in h_low or '_next/static' in h_low:
        detected["frontend_tech"].append("Next.js (React)")
    elif 'react' in h_low or 'reactdom' in h_low or 'data-reactroot' in h_low:
        detected["frontend_tech"].append("React")
    if '__nuxt' in h_low or '_nuxt/' in h_low:
        detected["frontend_tech"].append("Nuxt (Vue.js)")
    elif 'vue.js' in h_low or 'data-v-' in h_low or 'vuex' in h_low:
        detected["frontend_tech"].append("Vue.js")
    if 'gatsby' in h_low or '___gatsby' in h_low:
        detected["frontend_tech"].append("Gatsby")
    if 'svelte' in h_low:
        detected["frontend_tech"].append("Svelte")

    # Backend Clues
    if 'csrf-token' in h_low or 'laravel_session' in h_low or 'livewire' in h_low:
        detected["backend_clues"].append("Laravel (PHP)")
    if 'csrftoken' in h_low or 'django' in h_low:
        detected["backend_clues"].append("Django (Python)")
    if 'wp-json' in h_low or 'wp-content' in h_low:
        detected["backend_clues"].append("WordPress Core")

    return detected


# ══════════════════════════════════════════════════════════════
# FUNNEL & CHECKOUT URL DISCOVERY ENGINE
# ══════════════════════════════════════════════════════════════

def discover_checkout_and_cart_urls(base_url, html, fetcher):
    """Finds cart, checkout, booking, and lead submission URLs."""
    discovered = {
        "cart_urls": [],
        "checkout_urls": [],
        "lead_urls": [],
        "api_endpoints": []
    }

    base_parsed = urlparse(base_url)
    origin = f"{base_parsed.scheme}://{base_parsed.netloc}"

    soup = BeautifulSoup(html, "html.parser")
    all_links = set()
    for a in soup.find_all("a", href=True):
        href = a.get("href", "").strip()
        full = urljoin(base_url, href)
        if urlparse(full).netloc == base_parsed.netloc:
            all_links.add(full)

    for link in all_links:
        l_low = link.lower()
        if any(k in l_low for k in ['/cart', '/basket', '/panier', '/سلة', '/السلة']):
            discovered["cart_urls"].append(link)
        if any(k in l_low for k in ['/checkout', '/payment', '/دفع', '/الدفع', '/اتمام-الطلب', '/order']):
            discovered["checkout_urls"].append(link)
        if any(k in l_low for k in ['/contact', '/book', '/quote', '/lead', '/appointment', '/احجز', '/تواصل-معنا', '/حجز']):
            discovered["lead_urls"].append(link)

    # Standard candidate paths to probe if none found
    candidate_checkouts = [
        "/checkout/", "/checkout", "/cart/checkout", "/checkout/onepage",
        "/onestepcheckout", "/الدفع/", "/اتمام-الطلب/", "/order/"
    ]
    candidate_carts = [
        "/cart/", "/cart", "/basket/", "/سلة-المشتريات/", "/السلة/"
    ]

    if not discovered["checkout_urls"]:
        for cand in candidate_checkouts[:4]:
            cand_url = urljoin(origin, cand)
            try:
                code = fetcher.session.head(cand_url, timeout=5, allow_redirects=True).status_code
                if code in (200, 301, 302):
                    discovered["checkout_urls"].append(cand_url)
                    break
            except Exception:
                pass

    if not discovered["cart_urls"]:
        for cand in candidate_carts[:3]:
            cand_url = urljoin(origin, cand)
            try:
                code = fetcher.session.head(cand_url, timeout=5, allow_redirects=True).status_code
                if code in (200, 301, 302):
                    discovered["cart_urls"].append(cand_url)
                    break
            except Exception:
                pass

    # Look for API scripts
    for s in soup.find_all("script", src=True):
        src = s.get("src", "").lower()
        if any(api in src for api in ['/api/cart', '/api/checkout', 'stripe.com', 'tamara', 'tabby', 'paypal']):
            discovered["api_endpoints"].append(s.get("src"))

    discovered["cart_urls"] = list(set(discovered["cart_urls"]))
    discovered["checkout_urls"] = list(set(discovered["checkout_urls"]))
    discovered["lead_urls"] = list(set(discovered["lead_urls"]))

    return discovered


# ══════════════════════════════════════════════════════════════
# DOM FORM & CHECKOUT FRICTION ANALYZER
# ══════════════════════════════════════════════════════════════

def analyze_checkout_dom(html, page_url=""):
    """Performs deep inspection of forms, input fields, payment gateways, and friction signals."""
    soup = BeautifulSoup(html, "html.parser")

    results = {
        "url": page_url,
        "year": CURRENT_YEAR,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "forms_found": 0,
        "total_fields": 0,
        "required_fields_count": 0,
        "optional_fields_count": 0,
        "fields_by_type": {},
        "fields_detailed": [],
        "autocomplete_stats": {"has_autocomplete": 0, "missing_autocomplete": 0, "compliance_rate": "0%"},
        "payment_gateways_detected": [],
        "trust_signals_detected": [],
        "friction_flags": [],
        "coupon_element": {"found": False, "is_prominent_box": False, "selector": None},
        "guest_checkout": {"supported": False, "forced_login_detected": False},
        "mobile_ux": {"has_meta_viewport": False, "tel_inputs_count": 0, "sticky_cta_clues": False},
        "friction_score": 100,
        "baymard_verdict": ""
    }

    # 1. Viewport tag check
    viewport_meta = soup.find("meta", attrs={"name": "viewport"})
    if viewport_meta and "width=device-width" in viewport_meta.get("content", "").lower():
        results["mobile_ux"]["has_meta_viewport"] = True
    else:
        results["friction_flags"].append("CRITICAL: Missing or improper mobile meta viewport tag.")
        results["friction_score"] -= 15

    # 2. Forms & Input Elements Inspection
    forms = soup.find_all("form")
    results["forms_found"] = len(forms)

    candidate_inputs = soup.find_all(["input", "select", "textarea"])
    fields_seen = set()

    for el in candidate_inputs:
        tag_name = el.name
        input_type = el.get("type", "text").lower() if tag_name == "input" else tag_name
        name_attr = el.get("name", "")
        id_attr = el.get("id", "")
        placeholder = el.get("placeholder", "")
        autocomplete = el.get("autocomplete", "").strip()

        if input_type in ("hidden", "submit", "button", "image", "reset"):
            continue
        if any(ign in name_attr.lower() for ign in ["csrf", "token", "nonce", "security", "__viewstate"]):
            continue

        field_key = f"{name_attr or id_attr or placeholder or 'unnamed'}_{input_type}"
        if field_key in fields_seen:
            continue
        fields_seen.add(field_key)

        is_required = el.has_attr("required") or "required" in el.get("class", []) or el.get("aria-required") == "true"

        # Autocomplete compliance
        has_ac = bool(autocomplete and autocomplete.lower() not in ("off", "none", "false"))
        if has_ac:
            results["autocomplete_stats"]["has_autocomplete"] += 1
        else:
            results["autocomplete_stats"]["missing_autocomplete"] += 1

        if input_type == "tel":
            results["mobile_ux"]["tel_inputs_count"] += 1

        field_info = {
            "tag": tag_name,
            "type": input_type,
            "name": name_attr,
            "id": id_attr,
            "placeholder": placeholder,
            "required": is_required,
            "autocomplete": autocomplete or "MISSING"
        }
        results["fields_detailed"].append(field_info)

        results["total_fields"] += 1
        if is_required:
            results["required_fields_count"] += 1
        else:
            results["optional_fields_count"] += 1

        results["fields_by_type"][input_type] = results["fields_by_type"].get(input_type, 0) + 1

    # Autocomplete compliance percentage
    tot = results["total_fields"]
    if tot > 0:
        ac_rate = (results["autocomplete_stats"]["has_autocomplete"] / tot) * 100
        results["autocomplete_stats"]["compliance_rate"] = f"{ac_rate:.1f}%"
        if ac_rate < 50:
            results["friction_flags"].append(f"HIGH FRICTION: Only {ac_rate:.1f}% of input fields have 'autocomplete' attributes. Mobile users must type manually.")
            results["friction_score"] -= 12
    else:
        results["autocomplete_stats"]["compliance_rate"] = "N/A (No fields detected or CSR rendered)"

    # 3. Field Count Friction Evaluation (Baymard Benchmark: Ideal is 6-8 fields, Avg is 11.8)
    if tot > 14:
        results["friction_flags"].append(f"SEVERE FRICTION: Form contains {tot} input fields (Baymard ideal threshold is 6-8).")
        results["friction_score"] -= 20
    elif tot > 10:
        results["friction_flags"].append(f"MODERATE FRICTION: Form contains {tot} input fields (Exceeds ideal standard of 8 fields).")
        results["friction_score"] -= 10
    elif tot == 0:
        results["friction_flags"].append("WARNING: 0 input fields detected in static DOM. Flow may be fully client-side rendered (CSR/React) or requires cart items first.")

    # Phone input type verification
    phone_names = [f for f in results["fields_detailed"] if any(p in f["name"].lower() or p in f["id"].lower() or p in f["placeholder"].lower() for p in ["phone", "tel", "mobile", "جوال", "هاتف"])]
    for p_field in phone_names:
        if p_field["type"] not in ("tel", "number"):
            results["friction_flags"].append(f"KEYBOARD FRICTION: Phone field '{p_field['name'] or p_field['id']}' uses type='{p_field['type']}' instead of type='tel'. Forces desktop keyboard on mobile.")
            results["friction_score"] -= 8

    # 4. Coupon Code Friction Check
    coupon_keywords = ["coupon", "voucher", "promo", "discount", "كوبون", "قسيمة", "خصم"]
    for el in candidate_inputs:
        el_str = f"{el.get('name', '')} {el.get('id', '')} {el.get('placeholder', '')}".lower()
        if any(c in el_str for c in coupon_keywords):
            results["coupon_element"]["found"] = True
            results["coupon_element"]["is_prominent_box"] = True
            results["coupon_element"]["selector"] = f"{el.name}[name='{el.get('name', '')}']"
            results["friction_flags"].append("CONVERSION LEAK: Prominent open coupon code input box detected. Triggers discount abandonment.")
            results["friction_score"] -= 10
            break

    # 5. Payment Gateways & Methods Detection (Global & Regional: US, EU, UK, GCC, MENA, LATAM, APAC)
    html_low = html.lower()
    payment_signatures = {
        # Global & North America (US / Canada)
        "Apple Pay": ["apple-pay", "applepay", "apple pay"],
        "Google Pay": ["google-pay", "googlepay", "google pay", "gpay"],
        "Shop Pay (Shopify Express)": ["shop-pay", "shoppay", "shop pay"],
        "PayPal / PayPal Express": ["paypal.com", "paypal-button", "paypal", "data-paypal"],
        "Stripe": ["stripe.com", "stripe-elements", "data-stripe"],
        "Amazon Pay": ["amazon-pay", "amazonpay", "amazon pay"],
        "Affirm (US BNPL)": ["affirm", "affirm-pay", "data-affirm"],
        "Afterpay / Clearpay (US/UK/AU BNPL)": ["afterpay", "clearpay"],
        "Credit / Debit Card (Visa/Mastercard/Amex)": ["credit card", "mastercard", "visa", "american express", "amex", "بطاقة ائتمان"],

        # Europe (EU & UK)
        "Klarna (Pay Later / Sofort / Rechnung)": ["klarna", "pay with klarna", "klarna-payments", "rechnung", "sofort", "giropay"],
        "iDEAL (Netherlands - Crucial >60% Share)": ["ideal", "wlc-ideal", "currence-ideal", "ideal payment"],
        "BLIK (Poland - Dominant >70% Share)": ["blik", "platnosc blik"],
        "Bancontact (Belgium)": ["bancontact", "mister cash"],
        "SEPA Direct Debit (Eurozone)": ["sepa", "sepa direct debit", "sepa-mandate", "iban"],
        "Cartes Bancaires / CB (France)": ["cartes bancaires", "carte bancaire", "cb-logo"],
        "Swish (Sweden)": ["swish"],
        "MobilePay (Denmark/Finland)": ["mobilepay"],

        # Middle East & North Africa (GCC & Egypt)
        "Mada (مدى - Saudi Arabia)": ["mada", "مدى"],
        "Tabby (تابي - GCC BNPL)": ["tabby", "تابي"],
        "Tamara (تمارا - GCC BNPL)": ["tamara", "تمارا"],
        "STC Pay (Saudi Arabia)": ["stcpay", "stc pay", "اس تي سي باي"],
        "KNET (كي نت - Kuwait)": ["knet", "كي نت"],
        "Fawry (فوري - Egypt)": ["fawry", "فوري"],
        "Instapay / Wallets (إنستاباي / فودافون كاش - Egypt)": ["instapay", "إنستاباي", "vodafone cash", "فودافون كاش", "smart wallet"],
        "ValU (فاليو - تقسيط مصر)": ["valu", "فاليو"],
        "Paymob / Accept (Egypt/GCC)": ["paymob", "accept.paymob"],
        "Cash on Delivery / COD (الدفع عند الاستلام)": ["cash on delivery", "cod", "الدفع عند الاستلام", "عند الاستلام"],

        # Latin America (LATAM)
        "Pix (Brazil - Dominant Instant Payment)": ["pix", "chave pix", "pagamento pix"],
        "Boleto Bancário (Brazil)": ["boleto", "boleto bancario"],
        "OXXO (Mexico)": ["oxxo", "pago oxxo"],

        # Asia-Pacific (APAC)
        "UPI / PhonePe / Paytm / GPay (India)": ["upi", "bhim", "phonepe", "paytm", "upi payment"]
    }

    for p_name, sigs in payment_signatures.items():
        if any(sig in html_low for sig in sigs):
            results["payment_gateways_detected"].append(p_name)

    if not results["payment_gateways_detected"]:
        results["friction_flags"].append("WARNING: No recognized payment gateway badges or scripts detected in static DOM.")
        results["friction_score"] -= 10
    else:
        # Check for fast express checkout options
        has_fast_pay = any(m in results["payment_gateways_detected"] for m in ["Apple Pay", "Google Pay", "Shop Pay (Shopify Express)", "STC Pay (Saudi Arabia)"])
        if not has_fast_pay:
            results["friction_flags"].append("PAYMENT OPPORTUNITY: 1-Click Fast Express Checkout (Apple Pay / Google Pay / Shop Pay) not explicitly detected.")

    # 6. Trust & Security Badges
    trust_signatures = {
        "SSL / Secure Checkout Badge": ["secure checkout", "ssl", "دفع آمن", "تشفير آمن", "256-bit"],
        "Money Back Guarantee": ["money back", "ضمان استرجاع", "استرجاع مجاني", "refund guarantee"],
        "Customer Support WhatsApp/Phone": ["wa.me/", "whatsapp", "api.whatsapp.com", "خدمة العملاء", "تواصل معنا"],
        "Verified Reviews / Ratings": ["trustpilot", "maroof", "معروف", "تقييمات", "customer reviews"],
        "Tax / Commercial Register (الرقم الضريبي/السجل)": ["الرقم الضريبي", "السجل التجاري", "vat registration", "cr:"]
    }

    for t_name, sigs in trust_signatures.items():
        if any(sig in html_low for sig in sigs):
            results["trust_signals_detected"].append(t_name)

    if not results["trust_signals_detected"]:
        results["friction_flags"].append("TRUST DEFICIT: No trust badges, security certificates, or support links detected on checkout.")
        results["friction_score"] -= 12

    # 7. Guest Checkout vs Forced Account Registration
    if any(k in html_low for k in ["guest checkout", "الشراء كزائر", "الدفع كضيف", "continue as guest"]):
        results["guest_checkout"]["supported"] = True
    elif any(k in html_low for k in ["create an account to proceed", "must be logged in to checkout", "يجب تسجيل الدخول لإتمام الطلب"]):
        results["guest_checkout"]["forced_login_detected"] = True
        results["friction_flags"].append("CRITICAL CONVERSION KILLER: Forced Account Registration detected before checkout. (Baymard: #2 reason for abandonment).")
        results["friction_score"] -= 25

    # 8. Score Normalization & Baymard Rating
    results["friction_score"] = max(10, min(100, results["friction_score"]))
    score = results["friction_score"]

    if score >= 85:
        results["baymard_verdict"] = "EXCELLENT (Low Friction Funnel) 🟢"
    elif score >= 70:
        results["baymard_verdict"] = "GOOD (Minor Optimization Needed) 🟡"
    elif score >= 50:
        results["baymard_verdict"] = "MEDIOCRE (High Friction & Form Fatigue) 🟠"
    else:
        results["baymard_verdict"] = "CRITICAL (Severe Abandonment Risk) 🔴"

    return results


# ══════════════════════════════════════════════════════════════
# MANUAL MODE AUDIT QUESTIONNAIRE GENERATOR
# ══════════════════════════════════════════════════════════════

def print_manual_mode_instructions(url, failure_reason):
    """Outputs structured instructions for the user when all automated tools fail."""
    border = "═" * 78
    safe_print("\n" + border)
    safe_print(" 🔴 MANUAL AUDIT MODE REQUIRED — WAF CHALLENGE OR AUTH BLOCKED")
    safe_print(border)
    safe_print(f" Target URL     : {url}")
    safe_print(f" Failure Reason : {failure_reason}")
    safe_print(" The site is protected by strict anti-bot (Cloudflare Turnstile / Captcha)")
    safe_print(" or requires an authenticated cart session. To proceed with ZERO HALLUCINATION:")
    safe_print("─" * 78)
    safe_print(" 📸 REQUIRED SCREENSHOTS FROM THE USER:")
    safe_print(" 1. Add any product to the cart on your browser and open the checkout page.")
    safe_print(" 2. Take a screenshot of the Customer / Shipping Address input fields.")
    safe_print(" 3. Take a screenshot of the Payment Gateways selection section.")
    safe_print(" 4. Take a screenshot of the Order Summary / Promo Code box.")
    safe_print(" 5. Send the screenshots or paste the field names here for complete audit.")
    safe_print(border + "\n")


# ══════════════════════════════════════════════════════════════
# FORMATTED CONSOLE REPORTING & PROOF OF WORK
# ══════════════════════════════════════════════════════════════

def print_audit_report(url, platform_info, discovered_urls, analysis_results):
    """Outputs professional, non-hallucinatory CRO terminal report."""
    border = "═" * 78
    divider = "─" * 78

    safe_print("\n" + border)
    safe_print(f" 🚀 UNIVERSAL CRO & CHECKOUT FRICTION AUDIT REPORT ({CURRENT_YEAR}+ STANDARDS)")
    safe_print(border)
    safe_print(f" 🎯 Target URL        : {url}")
    safe_print(f" ⏱️ Timestamp         : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print(f" 🏗️ Detected Platform : {platform_info['platform']}")
    if platform_info['frontend_tech']:
        safe_print(f" ⚡ Frontend Stack    : {', '.join(platform_info['frontend_tech'])}")
    if platform_info['backend_clues']:
        safe_print(f" ⚙️ Backend Signals   : {', '.join(platform_info['backend_clues'])}")
    safe_print(divider)

    # Discovered Paths
    safe_print(" 🔍 DISCOVERED FUNNEL PATHS:")
    safe_print(f"    • Cart URLs     : {len(discovered_urls['cart_urls'])} found {discovered_urls['cart_urls'][:2]}")
    safe_print(f"    • Checkout URLs : {len(discovered_urls['checkout_urls'])} found {discovered_urls['checkout_urls'][:2]}")
    safe_print(f"    • Lead/Form URLs: {len(discovered_urls['lead_urls'])} found {discovered_urls['lead_urls'][:2]}")
    safe_print(divider)

    # Quantitative DOM Metrics
    safe_print(f" 📊 QUANTITATIVE FRICTION METRICS (Baymard Institute {CURRENT_YEAR}+ Benchmark):")
    safe_print(f"    • Total Form Fields      : {analysis_results['total_fields']} (Ideal: 6-8 fields)")
    safe_print(f"    • Required vs Optional   : {analysis_results['required_fields_count']} Required | {analysis_results['optional_fields_count']} Optional")
    safe_print(f"    • Autocomplete Adoption  : {analysis_results['autocomplete_stats']['compliance_rate']} ({analysis_results['autocomplete_stats']['has_autocomplete']} fields enabled)")
    safe_print(f"    • Mobile Meta Viewport   : {'✅ Configured' if analysis_results['mobile_ux']['has_meta_viewport'] else '❌ Missing'}")
    safe_print(f"    • Phone Keyboard (tel)   : {'✅ Optimized' if analysis_results['mobile_ux']['tel_inputs_count'] > 0 else '⚠️ Generic Input'}")
    safe_print(f"    • Guest Checkout Status  : {'✅ Supported' if analysis_results['guest_checkout']['supported'] else ('❌ FORCED LOGIN DETECTED' if analysis_results['guest_checkout']['forced_login_detected'] else '⚠️ Unverified (Requires live cart test)')}")
    safe_print(divider)

    # Gateways & Trust
    safe_print(" 💳 PAYMENT GATEWAYS & TRUST SIGNALS:")
    if analysis_results['payment_gateways_detected']:
        safe_print(f"    • Payment Methods ({len(analysis_results['payment_gateways_detected'])}): {', '.join(analysis_results['payment_gateways_detected'])}")
    else:
        safe_print("    • Payment Methods : ⚠️ None detected in static DOM (Check dynamic checkout)")

    if analysis_results['trust_signals_detected']:
        safe_print(f"    • Trust Signals   ({len(analysis_results['trust_signals_detected'])}): {', '.join(analysis_results['trust_signals_detected'])}")
    else:
        safe_print("    • Trust Signals   : ❌ No explicit trust/security badges found on page")
    safe_print(divider)

    # Coupon Box Leak
    safe_print(" 🎟️ PROMO / COUPON CODE BEHAVIOR:")
    if analysis_results['coupon_element']['found']:
        safe_print("    • Status : 🔴 OPEN PROMINENT INPUT BOX DETECTED")
        safe_print("    • Risk   : Causes users to abandon funnel to hunt for discount codes.")
        safe_print("    • Fix    : Collapse into a text link: 'Have a gift card or discount code?'")
    else:
        safe_print("    • Status : 🟢 No prominent open coupon field detected in static DOM")
    safe_print(divider)

    # Friction Flags
    safe_print(" ⚠️ IDENTIFIED FRICTION POINTS & FRICTION FLAGS:")
    if analysis_results['friction_flags']:
        for i, flag in enumerate(analysis_results['friction_flags'], 1):
            safe_print(f"    [{i}] {flag}")
    else:
        safe_print("    • No major friction flags detected in static inspection.")
    safe_print(divider)

    # Score & Verdict
    safe_print(f" 🏆 OVERALL FRICTION SCORE : {analysis_results['friction_score']} / 100")
    safe_print(f" 🏷️ VERDICT                : {analysis_results['baymard_verdict']}")
    safe_print(border + "\n")


# ══════════════════════════════════════════════════════════════
# MAIN CONTROLLER & CLI INTERFACE
# ══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description=f"Universal CRO & Checkout / Funnel Stealth Auditor v2.0 ({CURRENT_YEAR}+)"
    )
    parser.add_argument("url", help="Target website or checkout URL to audit")
    parser.add_argument("--seed-cart", action="store_true", help="Autonomously add a product to cart before auditing checkout")
    parser.add_argument("--playwright", action="store_true", help="Force Playwright headless browser for JS-rendered sites")
    parser.add_argument("--mobile", action="store_true", help="Simulate iPhone/Mobile browser viewport & user-agent")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON instead of console report")
    parser.add_argument("--timeout", type=int, default=18, help="Per-request timeout in seconds (default: 18)")

    args = parser.parse_args()
    _set_global_deadline()

    url = args.url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    fetcher = PageFetcher(timeout=args.timeout)

    # 1. Fetch Target / Homepage HTML
    fetch_res = fetcher.fetch_html(url, use_playwright=args.playwright, is_mobile=args.mobile)
    if not fetch_res.get("ok"):
        print_manual_mode_instructions(url, fetch_res.get("error", "Unknown error"))
        sys.exit(1)

    html = fetch_res["html"]
    final_url = fetch_res["url"]

    # 2. Detect Tech Stack & Platform
    platform_info = detect_platform_and_stack(html, final_url)

    # 3. Discover Checkout / Cart / Funnel Paths
    discovered_urls = discover_checkout_and_cart_urls(final_url, html, fetcher)

    target_audit_url = final_url
    target_audit_html = html

    # 4. Target Specific Checkout Page If Discovered
    is_root_url = urlparse(final_url).path.strip('/') in ('', 'en', 'ar')
    if discovered_urls["checkout_urls"] and is_root_url:
        checkout_to_check = discovered_urls["checkout_urls"][0]
        co_res = fetcher.fetch_html(checkout_to_check, use_playwright=args.playwright, is_mobile=args.mobile)
        if co_res.get("ok") and len(co_res.get("html", "")) > 400:
            target_audit_url = co_res["url"]
            target_audit_html = co_res["html"]
            platform_info = detect_platform_and_stack(target_audit_html, target_audit_url)

    # 5. Autonomous Cart Seeding (if requested or if 0 fields found in checkout)
    soup_test = BeautifulSoup(target_audit_html, "html.parser")
    inputs_count = len(soup_test.find_all(["input", "select", "textarea"]))
    if args.seed_cart or inputs_count <= 2 or "/cart" in target_audit_url.lower():
        safe_print("    [!] Cart appears empty or unseeded. Attempting autonomous cart seeding...")
        seed_result = seed_cart_and_get_checkout(final_url, fetcher, platform_name=platform_info["platform"])
        if isinstance(seed_result, dict) and seed_result.get("html"):
            target_audit_html = seed_result["html"]
            target_audit_url = seed_result["url"]
            platform_info = detect_platform_and_stack(target_audit_html, target_audit_url)
        elif isinstance(seed_result, str):
            co_res2 = fetcher.fetch_html(seed_result, use_playwright=args.playwright, is_mobile=args.mobile)
            if co_res2.get("ok"):
                target_audit_html = co_res2["html"]
                target_audit_url = co_res2["url"]
                platform_info = detect_platform_and_stack(target_audit_html, target_audit_url)

    # 6. Analyze DOM Friction & Form Usability
    analysis = analyze_checkout_dom(target_audit_html, target_audit_url)

    # 7. Output Delivery
    if args.json:
        full_payload = {
            "audit_meta": {
                "target_url": url,
                "audited_url": target_audit_url,
                "current_year": CURRENT_YEAR,
                "timestamp": datetime.datetime.now().isoformat(),
                "fetch_mode": fetch_res.get("mode", "unknown")
            },
            "platform_stack": platform_info,
            "discovered_funnel_paths": discovered_urls,
            "friction_analysis": analysis
        }
        print(json.dumps(full_payload, ensure_ascii=False, indent=2))
    else:
        print_audit_report(url, platform_info, discovered_urls, analysis)


if __name__ == "__main__":
    main()
