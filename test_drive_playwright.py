import time
from playwright.sync_api import sync_playwright

def get_drive_stream(url, mime_type="audio"):
    found_urls = []
    
    def handle_request(request):
        # drive videos use videoplayback
        if "videoplayback" in request.url:
            if f"mime={mime_type}" in request.url:
                found_urls.append(request.url)
    
    with sync_playwright() as p:
        # headless=True is faster but sometimes Google might block it, we'll try True first
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.on("request", handle_request)
        
        print(f"Navigating to {url}")
        page.goto(url)
        
        # We need to wait for the video player to load and start fetching streams.
        # Sometimes Drive auto-plays or starts buffering if we click the play button.
        try:
            # Let's wait a bit for network requests
            page.wait_for_timeout(5000)
            
            # If no urls found, maybe we need to click play
            if not found_urls:
                print("Clicking play button...")
                # The play button often has role="button" and aria-label="Play" or similar class
                page.mouse.click(500, 500) # clicking in the middle of the screen usually triggers play
                page.wait_for_timeout(3000)
                
        except Exception as e:
            print(f"Error during page interaction: {e}")
            
        browser.close()
        
    return found_urls

if __name__ == "__main__":
    # Test link (replace with a real one if needed, or I'll just ask the user or test with a known one)
    # I don't have a specific test link, but this is the logic.
    print("Test script ready.")
