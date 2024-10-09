import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        # Prompt the user for the user_data_dir path
        print("Welcome to the Setup Script for Finalmouse Battery Notification.")
        user_data_dir = input("Please enter the path to your user data directory (e.g., C:\\Users\\YourName\\Documents\\batteryProfile):\n").strip()

        # Ensure the directory exists
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)
            print(f"Created new directory at {user_data_dir}")

        # Store the path in a text file
        with open('user_data_dir.txt', 'w') as f:
            f.write(user_data_dir)
            print(f"User data directory path saved to 'user_data_dir.txt'.")

        # Launch Edge with the user data directory
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel='msedge',
            headless=False,  # Must be False to allow interaction
            args=['--enable-blink-features=WebHID']
        )

        page = browser.pages[0] if browser.pages else await browser.new_page()
        await page.goto('https://xpanel.finalmouse.com/dongle-led')

        print("\nSetup Instructions:")
        print("1. When the browser opens, you may be prompted to allow HID access.")
        print("2. Grant the HID permission to allow the page to access your mouse.")
        print("3. Ensure that your mouse is connected and turned on.")
        print("4. Once you've granted permission and confirmed the battery percentage is displayed, close the browser window.")
        print("\nPress Enter here after you've completed the above steps.")
        input()

        # Close the browser context
        await browser.close()
        print("Setup complete! Your user data directory is now configured.")

# Run the main function
asyncio.run(main())
