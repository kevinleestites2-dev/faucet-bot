import asyncio
import logging
import random
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger("FaucetBot")

WALLET = "0x369c2DDDBEb910c48356910069B2903b3Cb4d535"
NUM_BROWSERS = 10

FAUCET_TARGETS = [
    {
        "name": "FreeMATIC",
        "url": "https://freematic.com",
        "wallet_selector": "input[name='address'], input[placeholder*='address'], input[placeholder*='wallet']",
        "claim_selector": "button[type='submit'], button.claim, button#claim, input[type='submit']",
        "cooldown_minutes": 60
    },
    {
        "name": "MaticFaucet",
        "url": "https://maticfaucet.com",
        "wallet_selector": "input[name='address'], input[placeholder*='address'], input[placeholder*='wallet']",
        "claim_selector": "button[type='submit'], button.claim, button#claim, input[type='submit']",
        "cooldown_minutes": 60
    },
    {
        "name": "FaucetPay MATIC",
        "url": "https://faucetpay.io/faucets/matic",
        "wallet_selector": "input[name='address'], input[placeholder*='address']",
        "claim_selector": "button[type='submit'], button.btn-primary",
        "cooldown_minutes": 60
    }
]

async def claim_faucet(browser_id: int, target: dict, playwright):
    name = target["name"]
    log.info(f"[Browser {browser_id}] Launching -> {name}")
    browser = await playwright.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
    )
    context = await browser.new_context(
        user_agent=f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/{random.randint(110,120)}.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 720}
    )
    page = await context.new_page()
    try:
        await page.goto(target["url"], timeout=30000, wait_until="domcontentloaded")
        await asyncio.sleep(random.uniform(2, 4))
        wallet_input = await page.query_selector(target["wallet_selector"])
        if wallet_input:
            await wallet_input.fill(WALLET)
            await asyncio.sleep(random.uniform(1, 2))
            claim_btn = await page.query_selector(target["claim_selector"])
            if claim_btn:
                await claim_btn.click()
                await asyncio.sleep(3)
                log.info(f"[Browser {browser_id}] CLAIM SUBMITTED -> {name}")
            else:
                log.warning(f"[Browser {browser_id}] No claim button -> {name}")
        else:
            log.warning(f"[Browser {browser_id}] No wallet input -> {name}")
    except Exception as e:
        log.error(f"[Browser {browser_id}] Error on {name}: {e}")
    finally:
        await browser.close()

async def worker(browser_id: int):
    log.info(f"[Browser {browser_id}] Worker started")
    async with async_playwright() as playwright:
        while True:
            for target in FAUCET_TARGETS:
                await claim_faucet(browser_id, target, playwright)
                await asyncio.sleep(random.uniform(5, 15))
            wait = 3600 + random.randint(-300, 300)
            log.info(f"[Browser {browser_id}] Cycle done. Next in {wait//60}min")
            await asyncio.sleep(wait)

async def main():
    log.info(f"PANTHEON FAUCET BOT - {NUM_BROWSERS} parallel browsers")
    log.info(f"Wallet: {WALLET}")
    log.info(f"Targets: {len(FAUCET_TARGETS)} faucets")
    workers = [worker(i+1) for i in range(NUM_BROWSERS)]
    await asyncio.gather(*workers)

if __name__ == "__main__":
    asyncio.run(main())
