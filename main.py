import asyncio
from playwright.async_api import async_playwright, TimeoutError
from plyer import notification
import win32gui
import win32con
import time
import os

def minimize_browser_window(window_title_substring):
    def enum_window_callback(hwnd, _):
        if window_title_substring.lower() in win32gui.GetWindowText(hwnd).lower():
            # Minimize the window
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    win32gui.EnumWindows(enum_window_callback, None)

async def main():
    async with async_playwright() as p:
        # Read the user_data_dir path from the text file
        try:
            with open('user_data_dir.txt', 'r') as f:
                user_data_dir = f.read().strip()
        except FileNotFoundError:
            print("The 'user_data_dir.txt' file was not found. Please run the setup script first.")
            return

        # Ensure the directory exists
        if not os.path.exists(user_data_dir):
            print(f"The user data directory '{user_data_dir}' does not exist. Please run the setup script again.")
            return
        
        # Launch Edge with the user data directory
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel='msedge',
            headless=False,  # Must be False to allow window manipulation
            args=['--enable-blink-features=WebHID']
        )
        minimize_browser_window('XPANEL Overview - Finalmouse')
        minimize_browser_window('about:blank')

        page = browser.pages[0] if browser.pages else await browser.new_page()
        await page.goto('https://xpanel.finalmouse.com/dongle-led')
        
        # Wait until the battery percentage is not empty and not '0%'
        battery_percentage = ''
        max_wait_time = 30  # Maximum time to wait in seconds
        start_time = asyncio.get_event_loop().time()
        
        while True:
            try:
                # Try to get the battery percentage
                battery_percentage = await page.inner_text('#battery')
                battery_percentage = battery_percentage.strip()
                
                # Check if battery_percentage is not empty and not '0%'
                if battery_percentage and battery_percentage != '0%':
                    break  # Exit the loop if condition is met
            except TimeoutError:
                # If the selector is not found, continue waiting
                pass
            except Exception as e:
                print(f"An error occurred: {e}")
                break  # Exit the loop on unexpected errors
            
            # Check if maximum wait time has been exceeded
            elapsed_time = asyncio.get_event_loop().time() - start_time
            if elapsed_time > max_wait_time:
                print("Timed out waiting for valid battery percentage.")
                battery_percentage = 'Unavailable'
                break
            
            # Wait for a short interval before trying again
            await asyncio.sleep(1)
        
        notification.notify(
            title="Battery Notification",
            message=f"Mouse at {battery_percentage} battery",
            timeout=15
        )
        
        # Close the browser
        await browser.close()

# Run the main function
asyncio.run(main())
