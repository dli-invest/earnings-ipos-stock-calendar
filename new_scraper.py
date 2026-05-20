import asyncio
import os
from pydoll.browser.chromium import Chrome
from pydoll.browser.options import ChromiumOptions
from random_user_agent.user_agent import UserAgent
from get_proxy import get_and_set_selenium_proxy

async def bypass_cloudflare_example():
    # Create browser options
    # options = ChromiumOptions()

    # # Simple proxy without authentication
    # options.add_argument('--proxy-server=192.168.1.100:8080')
    # # Or proxy with authentication
    # # options.add_argument('--proxy-server=username:password@192.168.1.100:8080')

    # # Bypass proxy for specific domains
    # options.add_argument('--proxy-bypass-list=*.internal.company.com,localhost')
    options = ChromiumOptions()
    if not os.environ.get("NODRIVER_HEADLESS") == "True" and os.environ.get("DISPLAY", ":99"):
        display_var = os.environ.get("DISPLAY")
        print("display", display_var)
        options.add_argument(f'--display=:99')
    # options.add_argument(f'--display=:99')
    # options.binary_location = '/usr/bin/google-chrome-stable'
    # options.add_argument('--headless=new')
    # options.add_argument('--window-size=1920,1080')
    # options.add_argument("--enable-webgl")
    try:
        # selected_proxy = get_and_set_selenium_proxy()
        # print("going to use selected proxy", selected_proxy)
        # options.add_argument(f'--proxy-server={selected_proxy}')
        pass
    except Exception as e:
        print(e)

    # add user agent
    try:
        user_agent_rotator = UserAgent()
        user_agent = user_agent_rotator.get_random_user_agent()
        options.add_argument(f'--user-agent={user_agent}')
        pass
    except Exception as e:
        print(e)

    async with Chrome(options=options) as browser:
        tab = await browser.start()

    # The context manager will wait for the captcha to be processed
    # before continuing execution
    
        await tab.enable_auto_solve_cloudflare_captcha()
        await tab.go_to('https://2captcha.com/demo/cloudflare-turnstile-challenge')

        await asyncio.sleep(10)

        # This code runs only after the captcha is successfully bypassed
        output_dir = "screenshots"
        os.makedirs(output_dir, exist_ok=True) # Ensure the directory exists
        screenshot_path = os.path.join(output_dir, "cloudflare_bypass_screenshot.png")
        
        print(f"Taking screenshot and saving to {screenshot_path}")
        await tab.take_screenshot(path=screenshot_path, quality=90) # Save as PNG, full page

        print(f"Screenshot saved: {screenshot_path}")
        
        await tab.disable_auto_solve_cloudflare_captcha()

        await asyncio.sleep(3)

asyncio.run(bypass_cloudflare_example())
