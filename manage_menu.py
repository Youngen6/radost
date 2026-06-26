import json
import re
import sys
import os

HTML_PATH = "index.html"
EDITABLE_PATH = "template_editable.html"

def unpack():
    if not os.path.exists(HTML_PATH):
        print(f"Error: {HTML_PATH} not found in the current directory.")
        return

    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()

    template_match = re.search(r'<script[^>]*type=["\']__bundler/template["\'][^>]*>(.*?)</script>', html_content, re.DOTALL | re.IGNORECASE)
    if not template_match:
        print("Error: Could not find the template script tag inside index.html.")
        return

    try:
        template_json = json.loads(template_match.group(1).strip())
        with open(EDITABLE_PATH, "w", encoding="utf-8") as f_out:
            f_out.write(template_json)
        print(f"Success! Unpacked template to {EDITABLE_PATH}.")
        print("You can now open template_editable.html, go down to line ~730 to edit your items, and add/change the 'vol' properties.")
        print("When you are done, run: python manage_menu.py pack")
    except Exception as e:
        print(f"Error parsing template JSON: {e}")

def pack():
    if not os.path.exists(HTML_PATH):
        print(f"Error: {HTML_PATH} not found.")
        return
    if not os.path.exists(EDITABLE_PATH):
        print(f"Error: {EDITABLE_PATH} not found. Run 'unpack' first.")
        return

    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()

    with open(EDITABLE_PATH, "r", encoding="utf-8") as f:
        editable_content = f.read()

    # Find the tag to replace
    pattern = r'(<script[^>]*type=["\']__bundler/template["\'][^>]*>)(.*?)(</script>)'
    
    # JSON-encode the editable content to match the original layout
    encoded_template = json.dumps(editable_content)

    new_html, count = re.subn(pattern, rf"\g<1>{encoded_template}\g<3>", html_content, flags=re.DOTALL | re.IGNORECASE)
    if count == 0:
        print("Error: Could not find the template script tag inside index.html to replace.")
        return

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)

    print("Success! Packaged your changes back into index.html.")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ["unpack", "pack"]:
        print("Usage:")
        print("  python manage_menu.py unpack   - Decodes index.html template to template_editable.html")
        print("  python manage_menu.py pack     - Re-saves template_editable.html back into index.html")
    else:
        cmd = sys.argv[1]
        if cmd == "unpack":
            unpack()
        elif cmd == "pack":
            pack()
