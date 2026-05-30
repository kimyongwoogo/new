const drawer = document.querySelector('#assistantDrawer');
const toggleDrawer = (open) => {
  drawer.classList.toggle('open', open);
  drawer.setAttribute('aria-hidden', String(!open));
};

document.querySelector('#assistantToggle').addEventListener('click', () => toggleDrawer(!drawer.classList.contains('open')));
document.querySelector('#assistantClose').addEventListener('click', () => toggleDrawer(false));

document.querySelectorAll('.quick-prompts button').forEach((button) => {
  button.addEventListener('click', () => sendMessage(button.textContent));
});

document.querySelector('#chatForm').addEventListener('submit', (event) => {
  event.preventDefault();
  const input = document.querySelector('#chatInput');
  if (!input.value.trim()) return;
  sendMessage(input.value.trim());
  input.value = '';
});

function sendMessage(message) {
  const chat = document.querySelector('#chatBody');
  chat.insertAdjacentHTML('beforeend', `<div class="user-bubble">${message}</div>`);
  const answer = message.includes('일정')
    ? '오늘은 4개의 일정이 있습니다. 오전 11시 신규 프로젝트 킥오프 미팅을 먼저 준비하시는 것을 추천드려요.'
    : '박지현 이사님께 보낼 답장 초안을 준비할게요. 어떤 내용을 강조하면 좋을까요?';
  setTimeout(() => {
    chat.insertAdjacentHTML('beforeend', `<div class="ai-bubble">${answer}</div>`);
    chat.scrollTop = chat.scrollHeight;
  }, 280);
}

document.querySelectorAll('.task input').forEach((checkbox) => {
  checkbox.addEventListener('change', () => {
    const label = checkbox.closest('.task');
    const text = label.querySelector('p');
    label.classList.toggle('done', checkbox.checked);
    if (checkbox.checked && !text.querySelector('s')) text.innerHTML = `<s>${text.childNodes[0].textContent.trim()}</s><small>완료됨</small>`;
    document.querySelector('#doneCount').textContent = document.querySelectorAll('.task input:checked').length + 1;
  });
});

const dialog = document.querySelector('#scheduleDialog');
document.querySelector('#addSchedule').addEventListener('click', () => dialog.showModal());
document.querySelector('#addTask').addEventListener('click', () => alert('새로운 할 일을 빠르게 추가할 수 있어요.'));

document.querySelector('.mobile-menu').addEventListener('click', () => document.querySelector('.sidebar').classList.toggle('open'));
document.querySelectorAll('.main-nav .nav-item').forEach((item) => item.addEventListener('click', () => {
  document.querySelector('.main-nav .active').classList.remove('active');
  item.classList.add('active');
}));
