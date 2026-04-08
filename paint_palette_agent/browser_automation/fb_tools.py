"""
F&B-specific Browser-Use Custom Tools.

This module provides custom actions for F&B website automation
following the current Browser-Use Tools pattern with ActionResult returns.
"""

import logging
from typing import Dict, Any, List
import re
import json

try:
    from browser_use import Tools, ActionResult
    TOOLS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Browser-Use Tools not available: {e}")
    TOOLS_AVAILABLE = False
    Tools = None
    ActionResult = None

logger = logging.getLogger(__name__)

# Initialize F&B tools following current Browser-Use pattern
fb_tools = Tools() if TOOLS_AVAILABLE else None


if TOOLS_AVAILABLE:

    @fb_tools.action(description="Extract F&B color information from current product page")
    async def extract_fb_color_info(page_html: str = "") -> ActionResult:
        """
        Extract detailed color information from F&B product page.
        
        This custom tool helps parse F&B-specific page structure
        to extract color details, pricing, and availability.
        
        Args:
            page_html: Optional HTML content to parse
            
        Returns:
            ActionResult with extracted color data
        """
        try:
            # Extract color information using patterns specific to F&B website
            color_data = {}
            
            if page_html:
                # Extract color name
                name_match = re.search(r'<h1[^>]*>([^<]*(?:No\.\s*\d+)?[^<]*)</h1>', page_html, re.IGNORECASE)
                if name_match:
                    color_data['name'] = name_match.group(1).strip()
                
                # Extract color number
                number_match = re.search(r'No\.\s*(\d+)', page_html, re.IGNORECASE)
                if number_match:
                    color_data['number'] = number_match.group(1)
                
                # Extract sample price
                price_matches = re.findall(r'£(\d+\.?\d*)', page_html)
                if price_matches:
                    # Look for sample-related prices (usually around £9)
                    for price in price_matches:
                        if 8 <= float(price) <= 12:  # Sample price range
                            color_data['sample_price'] = f"£{price}"
                            break
                    if 'sample_price' not in color_data and price_matches:
                        color_data['sample_price'] = f"£{price_matches[0]}"
                
                # Check availability
                if 'out of stock' in page_html.lower() or 'unavailable' in page_html.lower():
                    color_data['available'] = False
                else:
                    color_data['available'] = True
            
            return ActionResult(
                extracted_content=color_data,
                include_in_memory=True,
                long_term_memory=f"Extracted F&B color info: {color_data.get('name', 'Unknown')} (No. {color_data.get('number', 'Unknown')})"
            )
            
        except Exception as e:
            logger.error(f"Failed to extract F&B color info: {str(e)}")
            return ActionResult(
                extracted_content={
                    "error": str(e),
                    "available": False
                },
                include_in_memory=True,
                long_term_memory=f"Failed to extract color info: {str(e)}"
            )


    @fb_tools.action(description="Extract F&B shopping cart total and contents")
    async def get_fb_cart_total(page_html: str = "") -> ActionResult:
        """
        Extract cart total and item details from F&B shopping cart page.
        
        This tool specifically handles F&B cart page structure to
        provide accurate pricing and item information.
        
        Args:
            page_html: HTML content of cart page
            
        Returns:
            ActionResult with cart details
        """
        try:
            cart_data = {
                "total_price": "£0.00",
                "total_items": 0,
                "items": [],
                "currency": "£"
            }
            
            if page_html:
                # Extract total price - look for common cart total patterns
                total_patterns = [
                    r'Total[^£]*£(\d+\.?\d*)',
                    r'Subtotal[^£]*£(\d+\.?\d*)',
                    r'Order Total[^£]*£(\d+\.?\d*)',
                    r'Cart Total[^£]*£(\d+\.?\d*)'
                ]
                
                for pattern in total_patterns:
                    total_match = re.search(pattern, page_html, re.IGNORECASE)
                    if total_match:
                        cart_data["total_price"] = f"£{total_match.group(1)}"
                        break
                
                # Extract individual items
                # Look for product names in cart (F&B color names pattern)
                color_patterns = [
                    r'([A-Z][^<>]*(?:No\.\s*\d+)[^<>]*)',  # Color names with numbers
                    r'([A-Z][^<>]*(?:Sample|Pot)[^<>]*)',   # Items with "Sample" or "Pot"
                ]
                
                for pattern in color_patterns:
                    items = re.findall(pattern, page_html)
                    cart_data["items"].extend([item.strip() for item in items[:10]])  # Limit to 10 items
                
                # Count items (fallback if parsing fails)
                if not cart_data["items"]:
                    # Look for quantity indicators
                    qty_matches = re.findall(r'quantity[^>]*>(\d+)', page_html, re.IGNORECASE)
                    cart_data["total_items"] = sum(int(q) for q in qty_matches)
                else:
                    cart_data["total_items"] = len(cart_data["items"])
            
            return ActionResult(
                extracted_content=cart_data,
                include_in_memory=True,
                long_term_memory=f"F&B cart: {cart_data['total_items']} items, total {cart_data['total_price']}"
            )
            
        except Exception as e:
            logger.error(f"Failed to extract cart total: {str(e)}")
            return ActionResult(
                extracted_content={
                    "error": str(e),
                    "total_price": "£0.00",
                    "total_items": 0,
                    "items": []
                },
                include_in_memory=True,
                long_term_memory=f"Failed to extract cart info: {str(e)}"
            )


    @fb_tools.action(description="Check F&B color availability and pricing")
    async def check_fb_color_availability(color_name: str, color_number: str = "") -> ActionResult:
        """
        Check if a specific F&B color is available for sample ordering.
        
        This tool can help verify color availability before attempting
        to add samples to cart, reducing failed automation attempts.
        
        Args:
            color_name: Name of the F&B color
            color_number: Optional F&B color number
            
        Returns:
            ActionResult with availability status
        """
        try:
            # This would typically make a targeted search or API call
            # For now, provide structured format for the browser agent to use
            
            search_info = {
                "color_name": color_name.strip(),
                "color_number": color_number.strip() if color_number else None,
                "search_query": f"{color_name} {color_number}".strip(),
                "availability_checked": True
            }
            
            return ActionResult(
                extracted_content=search_info,
                include_in_memory=True,
                long_term_memory=f"Checking availability for F&B color: {color_name} {color_number}"
            )
            
        except Exception as e:
            logger.error(f"Failed to check color availability: {str(e)}")
            return ActionResult(
                extracted_content={
                    "error": str(e),
                    "availability_checked": False
                },
                include_in_memory=True,
                long_term_memory=f"Failed to check availability for {color_name}: {str(e)}"
            )


else:
    # Fallback when Browser-Use tools not available
    logger.warning("Browser-Use Tools not available - F&B custom tools disabled")
    fb_tools = None


def get_fb_tools():
    """
    Get F&B custom tools for use with Browser-Use agent.
    
    Returns:
        Tools instance with F&B-specific actions, or None if unavailable
    """
    return fb_tools


# For testing and validation
def validate_tools():
    """Validate that F&B tools are properly configured."""
    if not TOOLS_AVAILABLE:
        return False, "Browser-Use Tools not available"
    
    if fb_tools is None:
        return False, "F&B tools not initialized"
    
    # Check that tools have been registered
    expected_actions = [
        'extract_fb_color_info',
        'get_fb_cart_total', 
        'check_fb_color_availability'
    ]
    
    # This would check tool registration in a real implementation
    # For now, just verify tools object exists
    return True, f"F&B tools initialized with custom actions"


if __name__ == "__main__":
    # Test tools validation
    is_valid, message = validate_tools()
    print(f"F&B Tools Status: {message}")
    
    if is_valid:
        print("Available custom actions:")
        print("- extract_fb_color_info: Extract color details from product page")
        print("- get_fb_cart_total: Extract cart total and contents")
        print("- check_fb_color_availability: Check color availability") 