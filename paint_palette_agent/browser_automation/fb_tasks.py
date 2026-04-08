"""
F&B-Specific Task Templates for Browser-Use Agent.

This module provides optimized task descriptions for F&B website automation,
following Browser-Use prompting guide best practices with specific action references,
error recovery strategies, and keyboard navigation alternatives.
"""

from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def create_sample_ordering_task(colors: List[Dict[str, str]]) -> str:
    """
    Create optimized task description for F&B sample ordering.
    
    This follows Browser-Use prompting best practices:
    - Specific action references (click_element_by_index, send_keys, etc.)
    - Error recovery strategies with keyboard navigation fallbacks
    - Clear step-by-step instructions
    - F&B website-specific guidance
    
    Args:
        colors: List of color dicts with 'name' and 'number' fields
        
    Returns:
        Optimized task description string
    """
    
    # Prepare colors list for task description
    colors_list = [f"'{c['name']}' (No. {c['number']})" for c in colors]
    colors_text = ", ".join(colors_list)
    
    return f"""
    Navigate to https://www.farrow-ball.com/us/ and add these paint samples to cart:
    {colors_text}

    For each color:
    1. Use search action to find the color by name or number
    2. Use click_element_by_index to navigate to the color's product page  
    3. Look for "Sample Pot", "Paint Sample", or "100ml Sample" option (usually $8-12)
    4. Use click_element_by_index to add the sample pot to your cart
    5. Wait for confirmation and continue with next color

    Error handling strategies:
    - If a button cannot be clicked, use send_keys action with "Tab Tab Enter"
    - If search fails, use send_keys with keyboard navigation to search box
    - If page times out, use go_back and try alternative approach
    - If "Add to Cart" button is unresponsive, try keyboard navigation: Tab to button, then Enter

    Step-by-step process:
    1. **Homepage Navigation**: Go to farrow-ball.com/us/
    2. **Search Process**: 
       - Use search action or click_element_by_index for search box
       - Type color name or number using send_keys
       - Press Enter or click search button using click_element_by_index
    3. **Product Selection**:
       - Use click_element_by_index to select the matching color from results
       - Verify you're on the correct product page (color name/number matches)
    4. **Sample Addition**:
       - Look for sample options (100ml Sample Pot, typically $8-12)
       - Use click_element_by_index to select sample option
       - Use click_element_by_index to click "Add to Cart" or "Add to Basket"
       - Wait for cart confirmation
    5. **Repeat** for each remaining color

    After all samples are added:
    1. Use click_element_by_index to navigate to the shopping cart/basket
    2. Use extract_structured_data to get cart contents with:
       - List of items added
       - Individual prices
       - Total price
       - Currency ($ for US site)
    
    IMPORTANT REQUIREMENTS:
    - Stop at cart review - do NOT complete checkout or proceed to payment
    - Use exact action names: click_element_by_index, send_keys, extract_structured_data
    - If any action fails, try keyboard navigation alternatives before giving up
    - Return structured data about cart contents and total price
    - If a color cannot be found, note it clearly in the results
    
    SUCCESS CRITERIA:
    - All available colors added to cart
    - Clear cart total extracted
    - List of successfully added vs. not found colors
    - NO progression past cart review
    
    Return a clear summary including:
    - Items successfully added to cart
    - Items that couldn't be found
    - Total cart value
    - Cart URL for user to complete purchase
    """


def create_single_color_search_task(color_name: str, color_number: str = "") -> str:
    """
    Create task for searching and verifying a single F&B color.
    
    Useful for testing individual color availability.
    
    Args:
        color_name: F&B color name
        color_number: Optional F&B color number
        
    Returns:
        Task description for single color search
    """
    
    color_query = f"{color_name} {color_number}".strip()
    
    return f"""
    Navigate to https://www.farrow-ball.com/us/ and search for this specific color:
    "{color_query}"

    Process:
    1. Use search action to find the color
    2. Use click_element_by_index to select the matching result
    3. Verify you're on the correct product page
    4. Use extract_structured_data to get:
       - Color name
       - Color number  
       - Sample price
       - Availability status
       - Product URL

    Error handling:
    - If search returns no results, try searching just the color name without number
    - If still no results, try browsing color categories
    - Use keyboard navigation if clicking fails

    Return structured information about the color's availability and pricing.
    """


def create_cart_review_task() -> str:
    """
    Create task for reviewing cart contents without checkout.
    
    Returns:
        Task description for cart review
    """
    
    return """
    Navigate to the F&B shopping cart and extract detailed cart information.

    Process:
    1. Use click_element_by_index to navigate to cart/basket
    2. Use extract_structured_data to capture:
       - Each item name and quantity
       - Individual item prices  
       - Subtotal
       - Tax (if any)
       - Total price
       - Currency
       - Estimated delivery time

    Error handling:
    - If cart page doesn't load, try refreshing or going back and trying again
    - Use keyboard navigation if needed: Tab to cart icon, then Enter

    CRITICAL: Do NOT proceed to checkout or payment pages.
    Stop at cart review and return the extracted information.
    """


def create_color_availability_batch_task(colors: List[Dict[str, str]]) -> str:
    """
    Create task to check availability of multiple colors without adding to cart.
    
    Useful for pre-validation before attempting full sample ordering.
    
    Args:
        colors: List of color dictionaries
        
    Returns:
        Task description for batch availability checking
    """
    
    colors_list = [f"'{c['name']}' (No. {c['number']})" for c in colors]
    colors_text = ", ".join(colors_list)
    
    return f"""
    Check availability and pricing for these F&B colors without adding to cart:
    {colors_text}

    For each color:
    1. Use search action to find the color
    2. Use click_element_by_index to visit product page
    3. Check for sample availability and pricing
    4. Record results and go back to search for next color

    Extract for each color:
    - Color name and number (if found)
    - Sample availability (Yes/No)
    - Sample price (if available)
    - Any availability notes (out of stock, special order, etc.)

    Error handling:
    - If a color isn't found, mark as "Not Available" 
    - If page errors occur, try refreshing and searching again
    - Use go_back action to return to search between colors

    Return structured data with availability status for all requested colors.
    Do NOT add any items to cart - this is availability checking only.
    """


def create_error_recovery_task(failed_color: str, error_context: str = "") -> str:
    """
    Create task for recovering from failed color addition.
    
    Args:
        failed_color: Color name that failed to be added
        error_context: Context about what went wrong
        
    Returns:
        Task description for error recovery
    """
    
    return f"""
    Attempt to recover from failed addition of color: {failed_color}
    
    Previous error context: {error_context}
    
    Recovery strategies to try:
    1. **Clear any error dialogs**: Look for popup messages and close them
    2. **Navigate back to homepage**: Use go_back or direct navigation
    3. **Try alternative search**: 
       - Search by color number only (if available)
       - Search by partial color name
       - Try browsing color categories instead of search
    4. **Use keyboard navigation throughout**:
       - Tab to navigate between elements
       - Enter to activate buttons
       - Space for checkboxes/selections

    If color is successfully found:
    - Add sample to cart using keyboard navigation
    - Verify addition was successful
    - Return success status

    If recovery fails:
    - Document what was attempted
    - Return detailed error information for user guidance

    Focus on providing clear feedback about what works vs. what doesn't.
    """


# Task templates mapping for easy access
TASK_TEMPLATES = {
    'sample_ordering': create_sample_ordering_task,
    'single_color_search': create_single_color_search_task,
    'cart_review': create_cart_review_task,
    'availability_check': create_color_availability_batch_task,
    'error_recovery': create_error_recovery_task
}


def get_task_template(template_name: str, **kwargs) -> str:
    """
    Get a specific task template with parameters.
    
    Args:
        template_name: Name of template to use
        **kwargs: Parameters for the template function
        
    Returns:
        Generated task description string
    """
    
    if template_name not in TASK_TEMPLATES:
        available = ", ".join(TASK_TEMPLATES.keys())
        raise ValueError(f"Unknown template '{template_name}'. Available: {available}")
    
    template_func = TASK_TEMPLATES[template_name]
    
    try:
        return template_func(**kwargs)
    except TypeError as e:
        raise ValueError(f"Invalid parameters for template '{template_name}': {str(e)}")


# For testing and documentation
if __name__ == "__main__":
    # Test template generation
    test_colors = [
        {"name": "Elephant's Breath", "number": "229"},
        {"name": "Farrow's Cream", "number": "67"}
    ]
    
    print("=== Sample Ordering Task ===")
    task = create_sample_ordering_task(test_colors)
    print(task[:500] + "..." if len(task) > 500 else task)
    
    print("\n=== Available Templates ===")
    for name, func in TASK_TEMPLATES.items():
        print(f"- {name}: {func.__doc__.split('.')[0] if func.__doc__ else 'No description'}") 