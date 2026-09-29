const toastRegion = document.querySelector('.nt-toast-region');

function showToast(message, tone = 'success') {
  const toast = document.createElement('div');
  toast.className = 'nt-toast';
  toast.dataset.tone = tone;
  toast.setAttribute('role', 'status');
  toast.innerHTML = `<span class="nt-icon" aria-hidden="true">${tone === 'error' ? '×' : tone === 'warning' ? '!' : '✓'}</span><span class="nt-toast__text"></span><button class="nt-toast__close" type="button" aria-label="关闭提示">✕</button>`;
  toast.querySelector('.nt-toast__text').textContent = message;
  let dismissTimer;
  const close = () => { window.clearTimeout(dismissTimer); toast.remove(); };
  const pauseDismiss = () => window.clearTimeout(dismissTimer);
  const startDismiss = () => { window.clearTimeout(dismissTimer); dismissTimer = window.setTimeout(close, 5000); };
  toast.querySelector('button').addEventListener('click', close);
  toast.addEventListener('pointerenter', pauseDismiss);
  toast.addEventListener('pointerleave', startDismiss);
  toast.addEventListener('focusin', pauseDismiss);
  toast.addEventListener('focusout', (event) => { if (!toast.contains(event.relatedTarget)) startDismiss(); });
  toastRegion.append(toast);
  startDismiss();
}

document.querySelectorAll('[data-copy]').forEach((button) => {
  button.addEventListener('click', async () => {
    const value = button.dataset.copy;
    try { await navigator.clipboard.writeText(value); } catch { /* Local file previews can block clipboard access. */ }
    button.dataset.state = 'copied';
    button.textContent = '已复制';
    window.setTimeout(() => { delete button.dataset.state; button.textContent = '复制'; }, 2500);
  });
});

document.querySelectorAll('[data-tab]').forEach((tab) => {
  tab.addEventListener('click', () => {
    const target = tab.dataset.tab;
    const tablist = tab.closest('[role="tablist"]');
    tablist.querySelectorAll('[role="tab"]').forEach((item) => item.setAttribute('aria-selected', String(item === tab)));
    const container = tablist.parentElement;
    container.querySelectorAll('[role="tabpanel"]').forEach((panel) => { panel.hidden = panel.id !== target; });
    tab.focus({ preventScroll: true });
  });
});

document.querySelectorAll('[data-toast]').forEach((button) => {
  button.addEventListener('click', () => showToast(button.dataset.toast, button.dataset.tone));
});

document.querySelectorAll('[data-dialog]').forEach((button) => {
  button.addEventListener('click', () => document.getElementById(button.dataset.dialog).showModal());
});

document.querySelector('[data-demo-loading]').addEventListener('click', (event) => {
  const button = event.currentTarget;
  button.dataset.state = 'loading';
  button.textContent = '重算中';
  window.setTimeout(() => { button.dataset.state = 'success'; button.textContent = '局部刷新完成'; }, 900);
  window.setTimeout(() => { delete button.dataset.state; button.textContent = '演示加载态'; }, 2500);
});

document.getElementById('reject-form').addEventListener('submit', (event) => {
  if (event.submitter.value === 'confirm') showToast('关联命题已重算，判断与条件矩阵已局部刷新。', 'warning');
});
document.getElementById('export-form').addEventListener('submit', (event) => {
  if (event.submitter.value === 'confirm') showToast('卷宗已生成：事实与推论已分区归档。', 'success');
});

