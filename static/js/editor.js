/**
 * LexReg AI – Document Editor JavaScript
 * Handles contenteditable rich text editor
 */
document.addEventListener('DOMContentLoaded', function () {
  const editor = document.getElementById('editor');
  if (!editor) return;

  // Word count
  editor.addEventListener('input', updateWordCount);
  updateWordCount();

  // Auto-save every 2 minutes
  setInterval(autoSave, 120000);
});

function updateWordCount() {
  const editor = document.getElementById('editor');
  if (!editor) return;
  const text  = editor.innerText || '';
  const words = text.trim() ? text.trim().split(/\s+/).length : 0;
  const chars = text.length;
  const el    = document.getElementById('wordCount');
  if (el) el.textContent = `${words} words · ${chars} characters`;
}

function autoSave() {
  const form = document.getElementById('editorForm');
  if (!form) return;
  document.getElementById('contentInput').value = document.getElementById('editor').innerHTML;
  document.getElementById('formAction').value   = 'save';
  // Silent save via fetch
  const fd = new FormData(form);
  fetch(form.action || window.location.pathname, {
    method: 'POST',
    body: fd,
  }).then(() => {
    showEditorNotif('Auto-saved ✓');
  }).catch(() => {});
}

function showEditorNotif(msg) {
  let notif = document.getElementById('editorNotif');
  if (!notif) {
    notif = document.createElement('div');
    notif.id = 'editorNotif';
    notif.style.cssText = 'position:fixed;bottom:20px;right:20px;background:#00c896;color:#fff;padding:8px 16px;border-radius:20px;font-size:13px;font-weight:600;z-index:9999;box-shadow:0 4px 12px rgba(0,0,0,.2);';
    document.body.appendChild(notif);
  }
  notif.textContent = msg;
  notif.style.opacity = '1';
  setTimeout(() => { notif.style.opacity = '0'; }, 2000);
}
