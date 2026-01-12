import customtkinter as ctk
from tkinter import filedialog
import re

# ==========================
# HTML Parsing Functions
# ==========================

def parse_html_advanced(html):
    """
    Parse HTML and return:
    - errors: list of strings
    - tree: list of tuples (tag_name, level, line_number)
    """
    stack = []
    errors = []
    tree = []

    if html.strip() == "":
        return ["⚠ File is empty!"], []

    lines = html.splitlines()
    tag_pattern = r"</?[a-zA-Z0-9]+[^>]*>"

    for line_num, line in enumerate(lines, start=1):
        tags = re.findall(tag_pattern, line)

        for tag in tags:
            tag_name_match = re.findall(r"[a-zA-Z0-9]+", tag)
            if not tag_name_match:
                continue
            tag_name = tag_name_match[0]

            # Closing tag
            if tag.startswith("</"):
                if not stack:
                    errors.append(f"Line {line_num}: Extra closing tag </{tag_name}>")
                else:
                    top_tag, top_level, top_line = stack.pop()
                    if top_tag != tag_name:
                        errors.append(f"Line {line_num}: Tag mismatch! Expected </{top_tag}> but found </{tag_name}>")
                    else:
                        tree.append((tag_name, top_level, top_line))  # matched closing

            # Self-closing tag
            elif tag.endswith("/>"):
                tree.append((tag_name, len(stack), line_num))  # self-closing, current level

            # Opening tag
            else:
                stack.append((tag_name, len(stack), line_num))

    # Remaining unclosed tags
    while stack:
        unclosed_tag, level, line_num = stack.pop()
        errors.append(f"Line {line_num}: Missing closing tag for <{unclosed_tag}>")
        tree.append((unclosed_tag, level, line_num))

    return errors, tree

# ==========================
# GUI Functions
# ==========================

def open_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("HTML Files", "*.html *.htm"), ("Text Files", "*.txt")]
    )
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            html_input.delete("0.0", ctk.END)
            html_input.insert(ctk.END, f.read())
        output_box.delete("0.0", ctk.END)

def save_errors():
    errors = output_box.get("0.0", ctk.END).strip()
    if not errors:
        ctk.CTkMessagebox.show_info("Save Error", "No errors to save!")
        return
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt")]
    )
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(errors)
        ctk.CTkMessagebox.show_info("Saved", f"Error report saved to {file_path}")

def toggle_mode():
    current_mode = ctk.get_appearance_mode()
    new_mode = "Dark" if current_mode == "Light" else "Light"
    ctk.set_appearance_mode(new_mode)

def clear_highlight():
    html_input.tag_remove("error_line", "0.0", ctk.END)
    html_input.tag_remove("tag", "0.0", ctk.END)

def highlight_errors(errors):
    clear_highlight()
    html_input.tag_config("error_line", background="#FFB6C1")  # pink background
    line_nums = []
    for err in errors:
        match = re.search(r"Line (\d+):", err)
        if match:
            line_nums.append(int(match.group(1)))
    for ln in line_nums:
        html_input.tag_add("error_line", f"{ln}.0", f"{ln}.end")

def highlight_syntax():
    # Simple HTML syntax highlighting: tags blue
    clear_highlight()
    html_input.tag_config("tag", foreground="#1E90FF")  # DodgerBlue
    content = html_input.get("0.0", ctk.END)
    for match in re.finditer(r"</?[a-zA-Z0-9]+[^>]*>", content):
        start = f"0.0 + {match.start()} chars"
        end = f"0.0 + {match.end()} chars"
        html_input.tag_add("tag", start, end)

def display_tree(tree):
    output_box.insert(ctk.END, "\nHTML Tree Structure:\n")
    for tag, level, line in tree:
        indent = "    " * level
        output_box.insert(ctk.END, f"{indent}{tag} (Line {line})\n")

def parse_button_clicked():
    html = html_input.get("0.0", ctk.END)
    errors, tree = parse_html_advanced(html)

    output_box.delete("0.0", ctk.END)
    highlight_syntax()
    highlight_errors(errors)

    if not errors:
        output_box.insert(ctk.END, "🎉 HTML is valid!\n")
    else:
        output_box.insert(ctk.END, "❌ Errors found:\n\n")
        for err in errors:
            output_box.insert(ctk.END, "• " + err + "\n")
    
    display_tree(tree)

# ==========================
# GUI Setup
# ==========================

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("HTML Parser")
root.geometry("1000x700")
root.resizable(False, False)

# Input Label
ctk.CTkLabel(root, text="Enter HTML Code or Open File:", font=("Arial", 14, "bold")).pack(pady=10)

# Input Text Box
html_input = ctk.CTkTextbox(root, height=250, width=950, font=("Consolas", 12))
html_input.pack(pady=5)

# Button Frame
button_frame = ctk.CTkFrame(root)
button_frame.pack(pady=10)

ctk.CTkButton(button_frame, text="Parse HTML", width=150, command=parse_button_clicked).grid(row=0, column=0, padx=10, pady=10)
ctk.CTkButton(button_frame, text="Open File", width=150, command=open_file).grid(row=0, column=1, padx=10, pady=10)
ctk.CTkButton(button_frame, text="Save Error Report", width=150, command=save_errors).grid(row=0, column=2, padx=10, pady=10)
ctk.CTkButton(button_frame, text="Toggle Dark/Light Mode", width=200, command=toggle_mode).grid(row=0, column=3, padx=10, pady=10)

# Output Label
ctk.CTkLabel(root, text="Parsing Result & HTML Tree:", font=("Arial", 14, "bold")).pack(pady=5)

# Output Text Box
output_box = ctk.CTkTextbox(root, height=250, width=950, font=("Consolas", 12))
output_box.pack(pady=5)

root.mainloop()
