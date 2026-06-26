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

    # Find the opening tag, then extract everything up to the real closing </script>.
    # We can't use a simple regex because </script> may appear inside the JSON content.
    # Instead: find the tag open, then walk forward until we find </script> that is NOT
    # preceded by a backslash (i.e. not the escaped <\/script> inside the JSON string).
    tag_match = re.search(r'<script[^>]*type=["\']__bundler/template["\'][^>]*>', html_content, re.IGNORECASE)
    if not tag_match:
        print("Error: Could not find the template script tag inside index.html.")
        return

    content_start = tag_match.end()
    # Anchor to the JSON's closing quote so a broken file with unescaped </script> inside
    # the template doesn't cause us to stop too early.
    close_match = re.search(r'"\s*</script>', html_content[content_start:], re.IGNORECASE)
    if not close_match:
        print("Error: Could not find the closing </script> for the template tag.")
        return

    # close_match.end() is after the ">"; subtract 9 to get the position of "<"
    raw_json = html_content[content_start : content_start + close_match.end() - len('</script>')].strip()

    try:
        template_json = json.loads(raw_json)
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

    # Find the opening tag using the same robust approach as unpack()
    tag_match = re.search(r'<script[^>]*type=["\']__bundler/template["\'][^>]*>', html_content, re.IGNORECASE)
    if not tag_match:
        print("Error: Could not find the template script tag inside index.html to replace.")
        return

    content_start = tag_match.end()
    # Find the real closing </script> by anchoring to the JSON string's closing quote.
    # A valid template JSON ends with " then optional whitespace then </script>.
    # Using just (?<!\\)</script> would stop at the first unescaped </script> inside
    # a broken/unescaped template, replacing only part of the old content and leaving
    # garbage in the HTML.
    close_match = re.search(r'"\s*</script>', html_content[content_start:], re.IGNORECASE)
    if not close_match:
        print("Error: Could not find the closing </script> for the template tag.")
        return

    # close_match.end() is right after the ">" of </script>, so subtract 9 to get the "<"
    content_end = content_start + close_match.end() - len('</script>')

    # JSON-encode and escape ALL "</" sequences to "<\/" in the JSON string.
    # This serves two purposes:
    # 1. Prevents the HTML parser from closing the <script> tag early at </script>.
    # 2. Prevents the DC framework's fetch-and-update path (parseDcText) from finding
    #    "</x-dc>" in the raw HTML source and overwriting the mounted component with
    #    the raw JSON-encoded template content (which would show "\n" everywhere).
    # The original Claude Design output achieved the same by using / for every "/".
    # JSON.parse / json.loads correctly decode "<\/" back to "</" after parsing.
    encoded_template = json.dumps(editable_content, ensure_ascii=False).replace('</', r'<\/')

    new_html = html_content[:content_start] + encoded_template + html_content[content_end:]

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
