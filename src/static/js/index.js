const form = document.getElementById('auth-form');
const toggleBtn = document.getElementById('toggle-mode');
const statusDiv = document.getElementById('status');
let isLogin = true;

// Переключение между Входом и Регистрацией
toggleBtn.onclick = () => {
	isLogin = !isLogin;
	document.getElementById('title').innerText = isLogin ? "Вход" : "Регистрация";
	toggleBtn.innerText = isLogin ? "Нет аккаунта? Зарегистрироваться" : "Уже есть аккаунт? Войти";
	statusDiv.classList.add('hidden');
};

form.onsubmit = async (e) => {
	e.preventDefault();
	const username = document.getElementById('username').value;
	const password = document.getElementById('password').value;
	
	// Эндпоинт зависит от режима
	const endpoint = isLogin ? '/login' : '/register';
	
	try {
		const response = await fetch(`http://127.0.0.1:8000${endpoint}`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ username, password })
		});

		const data = await response.json();

		if (response.ok) {
			showStatus(isLogin ? "Успешный вход!" : "Вы успешно зарегистрированы!", "green");
			
			if (data.access_token) {
				// 1. Сохраняем токен
				localStorage.setItem('token', data.access_token);
				
				// 2. Ждем секунду (чтобы пользователь успел увидеть надпись "Успех") 
				// и перекидываем на страницу профиля
				setTimeout(() => {
					window.location.href = 'profile.html';
				}, 1000);
			}
		}
	} catch (error) {
		showStatus("Сервер не отвечает. Проверь, запущен ли uvicorn!", "red");
	}
};

function showStatus(text, color) {
	statusDiv.innerText = text;
	statusDiv.className = `mt-4 text-center text-sm font-bold text-${color}-600`;
	statusDiv.classList.remove('hidden');
}

console.log("[index.js] has loaded!")