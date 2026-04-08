"""
Modern Browser-Use Integration for F&B Paint Sample Ordering - CONSOLIDATED VERSION.

All-in-one: Validation → Filtering → Async Handling → Browser Automation → Response Formatting.
Root agent calls order_paint_samples() → This does everything → Done.
"""

import asyncio
import logging
import os
import subprocess
import time
import requests
import concurrent.futures
from typing import Dict, List, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file (check multiple locations)
env_locations = [
    Path.cwd() / ".env",  # Current working directory
    Path(__file__).parent / ".env",  # Same directory as this script
    Path(__file__).parent.parent / ".env",  # paint_palette_agent/
    Path(__file__).parent.parent.parent / ".env",  # Root directory
]

for env_path in env_locations:
    if env_path.exists():
        load_dotenv(env_path)
        logger = logging.getLogger(__name__)
        logger.info(f"Loaded .env from {env_path}")
        break
else:
    logger = logging.getLogger(__name__)
    logger.warning("No .env file found in expected locations")

try:
    from browser_use import Agent as BrowserUseAgent, Browser
    from browser_use.llm import ChatGoogle
    BROWSER_USE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Browser-Use not available: {e}")
    BROWSER_USE_AVAILABLE = False

logger = logging.getLogger(__name__)


# ============================================================================
# BROWSER MANAGEMENT
# ============================================================================

def _is_chrome_debug_running() -> bool:
    """Check if Chrome is running with remote debugging on port 9222."""
    try:
        response = requests.get("http://localhost:9222/json/version", timeout=2)
        return response.status_code == 200
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False


def _start_chrome_debug() -> bool:
    """
    Start Chrome in debug mode if not already running.
    Returns True if Chrome was started or is already running, False on error.
    """
    if _is_chrome_debug_running():
        logger.info("Chrome debug mode already running on port 9222")
        return True
    
    logger.info("Chrome debug mode not detected. Starting Chrome with remote debugging...")
    
    try:
        # Start Chrome with remote debugging using default profile
        # This preserves your logins, bookmarks, extensions, etc.
        chrome_command = [
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            '--remote-debugging-port=9222', '--user-data-dir=/tmp/chrome-debug-profile'
        ]
        
        # Start Chrome in background (don't wait for it to exit)
        subprocess.Popen(
            chrome_command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True  # Detach from this process
        )
        
        # Wait for Chrome to start (up to 10 seconds)
        logger.info("Waiting for Chrome to start (visible, not headless)...")
        for i in range(20):  # 20 attempts * 0.5 seconds = 10 seconds max
            time.sleep(0.5)
            if _is_chrome_debug_running():
                logger.info(f"✓ Chrome started successfully in debug mode (port 9222) - VISIBLE window should be open!")
                return True
        
        logger.warning("Chrome started but debug port not responding after 10 seconds")
        return False
        
    except Exception as e:
        logger.error(f"Failed to start Chrome in debug mode: {e}")
        return False


async def get_or_create_browser(use_real_browser: bool = True, debug: bool = True):
    """
    Create a fresh Browser connection.
    
    Note: We create a new Browser object each time to avoid event queue issues,
    but when using CDP (use_real_browser=True), it connects to the same Chrome 
    instance, so Chrome stays open and persistent across calls.
    """
    
    # Create browser - either connect to debug Chrome or launch new one
    if use_real_browser:
        # Auto-start Chrome with debug port if not already running
        if not _start_chrome_debug():
            logger.warning("Could not start Chrome in debug mode, falling back to new browser instance")
            browser = Browser(
                keep_alive=True,
                headless=False if debug else True
            )
        else:
            # Connect to the visible Chrome instance via CDP
            try:
                logger.info("Connecting to Chrome via CDP (http://localhost:9222)...")
                browser = Browser(
                    cdp_url="http://localhost:9222",  # Connect to debug Chrome
                    keep_alive=True
                )
                logger.info("✓ Connected to Chrome browser via CDP (port 9222) - using visible Chrome window")
            except Exception as e:
                logger.warning(f"Could not connect to Chrome via CDP: {e}")
                logger.info("Falling back to new browser instance...")
                browser = Browser(
                    keep_alive=True,
                    headless=False if debug else True
                )
    else:
        # Launch new browser instance with keep_alive
        browser = Browser(
            keep_alive=True,  # Keep browser open after agent finishes
            headless=False if debug else True
        )
        logger.info("Launching new browser instance (will stay alive)")
    
    return browser


async def close_browser():
    """
    Legacy function - no longer needed since we don't cache Browser objects.
    
    Chrome instances stay open due to keep_alive=True or CDP connection,
    but individual Browser objects are created fresh each time to avoid
    event queue shutdown issues.
    """
    logger.info("close_browser() called - no-op (browsers are not cached)")


# ============================================================================
# INTERNAL BROWSER AUTOMATION (Low-level)
# ============================================================================

async def _run_browser_automation(
    colors: List[Dict[str, str]], 
    debug: bool = True,
    use_real_browser: bool = False
) -> Dict[str, Any]:
    """
    Internal function: Run browser automation to add colors to F&B cart.
    Called by order_paint_samples() after validation.
    """
    
    if not colors:
        return {
            "success": False,
            "error": "No colors provided"
        }
    
    # Build task description for Browser-Use agent
    colors_list = [f"'{c['name']}' (No. {c['number']})" for c in colors]
    colors_text = ", ".join(colors_list)
    
    task_description = f"""
    Go to https://www.farrow-ball.com/us/paint and add these paint samples to cart:
    {colors_text}

    For each color:
    1. Search for the color name
    2. Go to the product page
    3. Look for the modal in the top left of the page that has a "Select Samples" button and click it
    4. Click the "Add" button
    5. Close the modal and continue to the next color
    
    After adding all samples, go to the cart and tell me:
    - What's in the cart
    - The total price
    
    DO NOT checkout. Just add to cart and report back.
    """
    
    try:
        # Get or create browser
        browser = await get_or_create_browser(use_real_browser=use_real_browser, debug=debug)
        
        # Verify API key is available
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found in environment. "
                "Please create a .env file with: GOOGLE_API_KEY=your_key"
            )
        
        llm = ChatGoogle(
            model="gemini-2.5-flash",
            api_key=api_key
        )
        
        agent = BrowserUseAgent(
            task=task_description,
            llm=llm,
            browser=browser,
            max_actions=50,
            use_vision=True,
            action_delay=2.0  # Let AJAX-heavy site stabilize
        )
        
        logger.info(f"Starting Browser-Use to order {len(colors)} F&B samples")
        
        # Run the agent
        result = await agent.run()
        
        # Extract basic info from result
        result_text = str(result).lower()
        success = "cart" in result_text or "added" in result_text
        
        logger.info(f"Browser-Use completed. Success: {success}")
        
        return {
            "success": success,
            "cart_url": "https://www.farrow-ball.com/us/checkout/cart/",
            "result": str(result)[:500],  # First 500 chars for debugging
            "total_items": len(colors),
            "total_price": "$0.00"  # Will be updated if parsed from result
        }
        
    except Exception as e:
        logger.error(f"Browser-Use failed: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "cart_url": "https://www.farrow-ball.com/us"
        }


# ============================================================================
# RESPONSE FORMATTING
# ============================================================================

def _create_next_steps_message(result: Dict[str, Any]) -> str:
    """Create helpful next steps message for the user."""
    
    if result.get("success") and result.get("total_items", 0) > 0:
        total_price = result.get("total_price", "$0.00")
        total_items = result.get("total_items", 0)
        delivery = result.get("delivery_estimate", "3-5 business days")
        cart_url = result.get("cart_url", "https://www.farrow-ball.com/us/cart")
        checkout_window = result.get("checkout_window")
        browser_open = result.get("browser_status") == "open_for_checkout"
        
        if browser_open and checkout_window:
            # Browser is open for user to complete checkout
            return f"""✅ Success! Your {total_items} paint sample(s) have been added to the cart (Total: {total_price}).

🌐 **A browser window has been opened for you** with the items already in your cart!

To complete your order:
1. Look for the browser window that just opened
2. You should see your {total_items} sample(s) in the cart
3. Click "Proceed to Checkout" 
4. Enter your payment and delivery details
5. Complete your purchase

⏰ **You have {checkout_window} to complete checkout** before the browser auto-closes.

Estimated delivery: {delivery}

The samples will help you see how the colors look in your specific lighting conditions before making your final paint decisions."""
        else:
            # Traditional flow - browser closed, provide link
            return f"""✅ Success! Your {total_items} paint sample(s) have been added to your Farrow & Ball cart (Total: {total_price}).

To complete your order:
1. Visit your cart: {cart_url}
2. Review the samples and quantities  
3. Proceed to checkout to enter payment and delivery details
4. Complete your purchase securely

Estimated delivery: {delivery}

The samples will help you see how the colors look in your specific lighting conditions before making your final paint decisions."""
    
    elif result.get("items_not_found"):
        not_found = ", ".join(result.get("items_not_found", []))
        return f"""Some colors couldn't be automatically added: {not_found}

Please visit farrow-ball.com/us manually to search for these colors and add samples to your cart. 
Look for the paint sample option (100ml, typically $8-12) for each recommended color."""
    
    else:
        return """Please visit farrow-ball.com/us to manually order paint samples. Look for the paint sample option (100ml, typically $8-12) for each recommended color."""


# ============================================================================
# MAIN ENTRY POINT (High-level - called by agent)
# ============================================================================

def order_paint_samples(
    recommended_colors: List[Dict[str, Any]], 
    user_message: str = "",
    debug_mode: bool = True,
    keep_browser_open: bool = True,
    checkout_timeout_minutes: int = 0,
    use_real_browser: bool = True  # Connect to debug Chrome by default
) -> Dict[str, Any]:
    """
    Order F&B paint samples through Browser-Use automation - CONSOLIDATED VERSION.
    
    This is the single entry point that handles:
    - Input validation
    - F&B color filtering  
    - Async execution handling
    - Browser automation
    - Response formatting
    
    Parameters
    ----------
    recommended_colors : List[Dict[str, Any]]
        List of color dictionaries from the catalog with at least 'name' and 'number' fields.
        Example: [{"name": "Elephant's Breath", "number": "229", "brand": "Farrow & Ball"}]
        
    user_message : str, optional
        Additional context or special instructions from the user about the ordering process.
        
    debug_mode : bool, optional
        Whether to run browser automation in debug mode with additional logging.
        Default is False.
    
    keep_browser_open : bool, optional
        If True, browser window stays open for user to complete checkout in the same session.
        This preserves the shopping cart so items don't disappear. Default is True.
    
    checkout_timeout_minutes : int, optional
        Number of minutes to keep browser open for checkout. Default is 10 minutes.
    
    use_real_browser : bool, optional
        If True, auto-starts Chrome with remote debugging (port 9222) if not running,
        then connects via CDP. Uses your default Chrome profile (preserves logins).
        If False, launches a new clean browser instance.
        Default is True.
        
        Chrome starts with: --remote-debugging-port=9222 (visible, not headless)
        
        IMPORTANT: Browser-Use will control the currently active tab in Chrome.
        To avoid hijacking your ADK Web tab:
        1. Open a new blank tab (Cmd+T) in the Chrome window that opens
        2. Make that tab active
        3. Go back to ADK Web and trigger the tool
        4. Automation runs in the blank tab!
    
    Returns
    -------
    Dict[str, Any]
        Dictionary containing ordering results:
        - success: bool - Whether the automation was successful
        - items_successfully_added: List[str] - Color names successfully added to cart
        - items_not_found: List[str] - Color names that couldn't be found
        - total_price: str - Total cart value (e.g., "$27.00")
        - total_items: int - Number of samples in cart
        - delivery_estimate: str - Expected delivery timeframe
        - cart_url: str - Direct link to F&B cart page
        - next_steps: str - Instructions for the user to complete purchase
        - errors_encountered: List[str] - Any issues during automation
    """
    
    # ========================================================================
    # STEP 1: INPUT VALIDATION
    # ========================================================================
    
    if not recommended_colors:
        return {
            "success": False,
            "error": "No colors provided for ordering",
            "items_successfully_added": [],
            "items_not_found": [],
            "total_price": "$0.00", 
            "total_items": 0,
            "delivery_estimate": "Not available",
            "cart_url": "",
            "next_steps": "Please provide color recommendations first",
            "errors_encountered": ["No colors provided"]
        }
    
    # ========================================================================
    # STEP 2: CHECK BROWSER-USE AVAILABILITY
    # ========================================================================
    
    if not BROWSER_USE_AVAILABLE:
        return {
            "success": False,
            "error": "Browser-Use automation not available",
            "items_successfully_added": [],
            "items_not_found": [color.get('name', 'Unknown') for color in recommended_colors],
            "total_price": "$0.00",
            "total_items": 0,
            "delivery_estimate": "Not available", 
            "cart_url": "https://www.farrow-ball.com/us",
            "next_steps": "Please visit farrow-ball.com manually to order samples",
            "errors_encountered": ["Browser-Use integration required but not installed"]
        }
    
    # ========================================================================
    # STEP 3: FILTER AND FORMAT COLORS (F&B only)
    # ========================================================================
    
    colors_to_order = []
    for color in recommended_colors:
        # Extract required fields, handling different possible formats
        color_name = color.get('name', color.get('color_name', 'Unknown'))
        color_number = color.get('number', color.get('color_number', color.get('code', 'Unknown')))
        
        # Only add F&B colors
        brand = color.get('brand', color.get('brand_name', '')).lower()
        if 'farrow' in brand or 'ball' in brand or not brand:  # Include if F&B or unknown brand
            colors_to_order.append({
                'name': color_name,
                'number': str(color_number).replace('No.', '').replace('No', '').strip()
            })
    
    if not colors_to_order:
        return {
            "success": False,
            "error": "No Farrow & Ball colors found in recommendations",
            "items_successfully_added": [],
            "items_not_found": [color.get('name', 'Unknown') for color in recommended_colors],
            "total_price": "$0.00",
            "total_items": 0,
            "delivery_estimate": "Not available",
            "cart_url": "",
            "next_steps": "This tool only works with Farrow & Ball colors",
            "errors_encountered": ["No F&B colors in recommendations"]
        }
    
    logger.info(f"Attempting to order {len(colors_to_order)} F&B paint samples")
    if user_message:
        logger.info(f"User context: {user_message}")
    
    # ========================================================================
    # STEP 4: RUN BROWSER AUTOMATION (handling async properly)
    # ========================================================================
    
    try:
        # Handle async execution context properly
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context, run in a thread to avoid event loop conflict
            
            def run_browser_automation():
                # Create a new event loop in this thread
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    result = new_loop.run_until_complete(
                        _run_browser_automation(
                            colors_to_order, 
                            debug=debug_mode,
                            use_real_browser=use_real_browser
                        )
                    )
                    logger.info(f"Thread automation completed")
                    return result
                except Exception as e:
                    logger.error(f"Thread automation error: {str(e)}")
                    raise
                finally:
                    # Clean up event loop
                    try:
                        new_loop.run_until_complete(asyncio.sleep(0.1))
                    except:
                        pass
                    new_loop.close()
            
            # Run in thread with timeout
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_browser_automation)
                result = future.result(timeout=400)  # 6.5 minute timeout
                logger.info(f"Browser automation completed in thread")
                
        except RuntimeError:
            # No event loop running, use asyncio.run directly
            result = asyncio.run(
                _run_browser_automation(
                    colors_to_order, 
                    debug=debug_mode,
                    use_real_browser=use_real_browser
                )
            )
            logger.info(f"Browser automation completed directly")
        
        # ====================================================================
        # STEP 5: FORMAT AND ENHANCE RESPONSE
        # ====================================================================
        
        logger.info(f"Result received: success={result.get('success')}, items={result.get('total_items')}")
        
        # Convert £ to $ for US site if needed
        if result.get("total_price", "").startswith("£"):
            price_value = result["total_price"].replace("£", "")
            result["total_price"] = f"${price_value}"
        
        # Add next steps message
        result["next_steps"] = _create_next_steps_message(result)
        result["cart_url"] = result.get("cart_url", "https://www.farrow-ball.com/us/cart")
        
        # Add default fields if missing
        result.setdefault("items_successfully_added", [c['name'] for c in colors_to_order])
        result.setdefault("items_not_found", [])
        result.setdefault("delivery_estimate", "3-5 business days")
        result.setdefault("errors_encountered", [])
        
        # Log result
        if result.get("success"):
            logger.info(f"Successfully added {result.get('total_items', 0)} samples to F&B cart")
        else:
            logger.warning(f"Browser automation encountered issues: {result.get('errors_encountered', [])}")
        
        return result
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Unexpected error during sample ordering: {str(e)}")
        logger.error(f"Full traceback:\n{error_details}")
        return {
            "success": False,
            "error": f"Automation error: {str(e)}",
            "items_successfully_added": [],
            "items_not_found": [color['name'] for color in colors_to_order],
            "total_price": "$0.00",
            "total_items": 0,
            "delivery_estimate": "Not available",
            "cart_url": "https://www.farrow-ball.com/us",
            "next_steps": "Please visit farrow-ball.com manually to order samples",
            "errors_encountered": [str(e)]
        }


# ============================================================================
# BACKWARD COMPATIBILITY ALIASES
# ============================================================================

# Keep old function name for any code that might still reference it
order_fb_samples_with_browser_use = order_paint_samples
order_paint_samples_tool = order_paint_samples


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    # Test with sample F&B colors
    test_colors = [
        {
            "name": "Elephant's Breath",
            "number": "229", 
            "brand": "Farrow & Ball",
            "hex": "#958D84"
        },
        {
            "name": "Farrow's Cream", 
            "number": "67",
            "brand": "Farrow & Ball",
            "hex": "#EDDE9D"
        }
    ]
    
    print("Testing Consolidated F&B Sample Ordering...")
    print("=" * 50)
    
    result = order_paint_samples(test_colors, debug_mode=True)
    
    print("Ordering Result:")
    for key, value in result.items():
        if key != 'next_steps':  # Print next_steps separately for readability
            print(f"  {key}: {value}")
    
    print(f"\nNext Steps:\n{result.get('next_steps', 'No next steps provided')}")
    
    print("\n" + "=" * 50)
    print("Consolidated Browser-Use Integration Test Complete") 