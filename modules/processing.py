# File: /content_automation/content_system/processing.py
# ---- THIS IS THE CORRECTED VERSION ----

import re

def post_processor(raw_text: str) -> tuple[str | None, str | None]:
    """
    Cleans raw, model-generated HTML, removes common wrappers,
    extracts the title from the <h1> tag, and returns the cleaned HTML content.
    """
    if not raw_text:
        return None, None

    # --- 1. Aggressive Cleaning Stage ---

    # Start with stripping any leading/trailing whitespace
    cleaned_text = raw_text.strip()

    # Remove Markdown code blocks if they still appear (e.g., ```html)
    if cleaned_text.startswith('```'):
        cleaned_text = re.sub(r'^```(html)?\n', '', cleaned_text)
        cleaned_text = re.sub(r'\n```$', '', cleaned_text)

    # Remove any stray <body> or <html> tags that might wrap the content
    cleaned_text = cleaned_text.replace("<body>", "").replace("</body>", "")
    cleaned_text = cleaned_text.replace("<html>", "").replace("</html>", "")

    # --- 2. Extraction and Finalization Stage ---

    # Find the title within the first h1 tag
    # The regex looks for an <h1> tag, captures its content non-greedily, and closes it.
    # It is case-insensitive (re.IGNORECASE) and handles newlines inside the tag (re.DOTALL)
    title_match = re.search(r'<h1.*?>(.*?)</h1>', cleaned_text, re.IGNORECASE | re.DOTALL)

    if title_match:
        # The title is just the text content of the H1 tag.
        # We also strip any potential HTML tags that might be inside the h1 tag itself.
        title_text = re.sub('<[^<]+?>', '', title_match.group(1)) # Remove tags
        title = title_text.strip()
    else:
        # Fallback 1: Try to find h2 tags
        h2_match = re.search(r'<h2.*?>(.*?)</h2>', cleaned_text, re.IGNORECASE | re.DOTALL)
        if h2_match:
            title_text = re.sub('<[^<]+?>', '', h2_match.group(1))
            title = title_text.strip()
        else:
            # Fallback 2: Try to extract from the first paragraph or any text
            p_match = re.search(r'<p.*?>(.*?)</p>', cleaned_text, re.IGNORECASE | re.DOTALL)
            if p_match:
                # Take first 50 characters from first paragraph as title
                title_text = re.sub('<[^<]+?>', '', p_match.group(1))
                title = title_text.strip()[:50] + "..." if len(title_text.strip()) > 50 else title_text.strip()
            else:
                # Fallback 3: Extract any text content and use first line
                text_content = re.sub('<[^<]+?>', '', cleaned_text)
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                if lines:
                    title = lines[0][:50] + "..." if len(lines[0]) > 50 else lines[0]
                else:
                    title = "Untitled Article"

    # Remove the H1 tag from the content since we've extracted it as the title
    # This prevents duplicate titles when publishing to WordPress
    content_without_h1 = re.sub(r'<h1.*?>.*?</h1>', '', cleaned_text, flags=re.IGNORECASE | re.DOTALL)
    
    # Also remove H2 tags if we used them for title extraction
    if not title_match and h2_match:
        content_without_h1 = re.sub(r'<h2.*?>.*?</h2>', '', content_without_h1, flags=re.IGNORECASE | re.DOTALL)
    
    full_html_content = content_without_h1.strip()

    if not full_html_content:
        return None, None

    return title, full_html_content