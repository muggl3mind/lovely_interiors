"""
Modern Browser-Use automation module for F&B paint sample ordering - CONSOLIDATED.

This module provides the consolidated Browser-Use integration for
automated F&B paint sample ordering.
"""

from .browser_agent_tool import (
    order_paint_samples,
    order_paint_samples_tool,
    order_fb_samples_with_browser_use,
    get_or_create_browser,
    close_browser
)
from .fb_tools import get_fb_tools, validate_tools
from .fb_tasks import (
    create_sample_ordering_task,
    create_single_color_search_task,
    create_cart_review_task,
    get_task_template,
    TASK_TEMPLATES
)

__all__ = [
    # Main functions (consolidated)
    'order_paint_samples',
    'order_paint_samples_tool',
    'order_fb_samples_with_browser_use',  # Alias for compatibility
    'get_or_create_browser', 
    'close_browser',
    
    # F&B custom tools
    'get_fb_tools',
    'validate_tools',
    
    # Task templates
    'create_sample_ordering_task',
    'create_single_color_search_task', 
    'create_cart_review_task',
    'get_task_template',
    'TASK_TEMPLATES'
] 