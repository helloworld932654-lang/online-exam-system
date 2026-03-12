import sys
import re

print("Starting fix...")

# 1. Fix exam.html
with open(r'c:\Users\Krushna\OneDrive\Desktop\online-exam-system\templates\exam.html', 'r', encoding='utf-8') as f:
    exam = f.read()

old_img_src = "{{ url_for('static', filename=q[10].replace('static/', '')) if q[10].startswith('static/') else '/' + q[10] }}"
new_img_src = "{{ url_for('static', filename=q[10].replace('static/', '')) }}"

if old_img_src in exam:
    exam = exam.replace(old_img_src, new_img_src)
    with open(r'c:\Users\Krushna\OneDrive\Desktop\online-exam-system\templates\exam.html', 'w', encoding='utf-8') as f:
        f.write(exam)
    print("Fixed image src in exam.html")
else:
    print("Could not find image src pattern in exam.html")

# 2. Fix admin.html
with open(r'c:\Users\Krushna\OneDrive\Desktop\online-exam-system\templates\admin.html', 'r', encoding='utf-8') as f:
    admin = f.read()

if old_img_src in admin:
    admin = admin.replace(old_img_src, new_img_src)
    print("Fixed image src in admin.html")

modal_pattern = re.compile(r'(<!-- Edit Modal -->.*?<div class="modal-footer border-top-0 pt-0 pb-4 px-4 bg-white">\s*<button type="button" class="btn btn-light shadow-sm" data-bs-dismiss="modal">Cancel</button>\s*<button type="submit" class="btn btn-warning shadow-sm"><i class="bi bi-save me-2"></i>Save Changes</button>\s*</div>\s*</form>\s*</div>\s*</div>\s*</div>)', re.DOTALL)

modal_blocks = modal_pattern.findall(admin)
if modal_blocks:
    modal_block = modal_blocks[0]
    # remove it from its current position
    admin = admin.replace(modal_block, "")
    
    insertion_point = "<!-- Student Results -->"
    new_modals = "{% for q in questions %}\n" + modal_block + "\n{% endfor %}\n\n"
    
    if insertion_point in admin:
        admin = admin.replace(insertion_point, new_modals + insertion_point)
        with open(r'c:\Users\Krushna\OneDrive\Desktop\online-exam-system\templates\admin.html', 'w', encoding='utf-8') as f:
            f.write(admin)
        print("Fixed modal position in admin.html")
    else:
        print("Could not find Student Results insertion point")
else:
    print("Could not find modal block in admin.html")
