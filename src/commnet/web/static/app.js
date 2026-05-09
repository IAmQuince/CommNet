async function runLoopback() {
  const out = document.getElementById('loopback-output');
  if (!out) return;
  out.textContent = 'Running loopback self-test...';
  try {
    const response = await fetch('/api/loopback-test');
    const data = await response.json();
    out.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    out.textContent = 'Loopback test failed: ' + err;
  }
}

function setMenuVisible(dropdown, visible) {
  if (!dropdown) return;
  dropdown.hidden = !visible;
  const btn = document.getElementById('account-button');
  if (btn) btn.setAttribute('aria-expanded', visible ? 'true' : 'false');
}

function renderAccountMenu(data) {
  const menu = document.getElementById('account-menu');
  const name = document.getElementById('account-name');
  const avatar = document.getElementById('account-avatar');
  if (!menu || !name || !avatar) return;
  const signedIn = !!data.signed_in;
  menu.dataset.state = signedIn ? 'signed-in' : 'guest';
  name.textContent = signedIn ? (data.display_name || data.username || 'User') : 'Guest';
  avatar.className = 'account-avatar ' + (data.icon_kind || 'blank');
  avatar.innerHTML = data.icon_html || '○';

  const show = {
    login: !signedIn,
    signup: !signedIn,
    account: signedIn,
    profile: signedIn,
    icon: signedIn,
    settings: signedIn,
    mail: signedIn,
    requests: signedIn,
    portal: true,
    admin: !!data.can_admin,
    logout: signedIn,
  };
  document.querySelectorAll('#account-dropdown [data-menu]').forEach((el) => {
    const key = el.getAttribute('data-menu');
    el.style.display = show[key] ? '' : 'none';
  });
}

async function loadAccountMenu() {
  const menu = document.getElementById('account-menu');
  if (!menu) return;
  try {
    const response = await fetch('/api/session', {cache: 'no-store'});
    const data = await response.json();
    renderAccountMenu(data);
  } catch (err) {
    renderAccountMenu({signed_in:false, can_admin:false, icon_kind:'blank', icon_html:'○'});
  }
}

function bindAccountMenu() {
  const btn = document.getElementById('account-button');
  const dropdown = document.getElementById('account-dropdown');
  if (!btn || !dropdown) return;
  btn.addEventListener('click', (event) => {
    event.stopPropagation();
    setMenuVisible(dropdown, dropdown.hidden);
  });
  document.addEventListener('click', () => setMenuVisible(dropdown, false));
  dropdown.addEventListener('click', (event) => event.stopPropagation());
}

document.addEventListener('DOMContentLoaded', () => {
  bindAccountMenu();
  loadAccountMenu();
});
