
const debug = 0;

async function checkAuth() {
	if (debug){return;}
	const token = localStorage.getItem('token');
	if (!token) {
		window.location.href = 'index.html';
		return;
	}

	try {
		const response = await fetch('http://127.0.0.1:8000/users/me', {
			headers: { 'Authorization': `Bearer ${token}` }
		});

		if (response.ok) {
			const userData = await response.json();
			document.getElementById('user-info').classList.remove('hidden');
			document.getElementById('user-id').innerText = userData.id;
			document.getElementById('user-name').innerText = userData.username;
		} else {
			logout();
		}
	} catch (error) {
		console.error("Ошибка связи с сервером");
	}
}

async function getAdminPanelInfo() {
	const token = localStorage.getItem('token');
	try {
		const response = await fetch('http://127.0.0.1:8000/home/admin_panel', {
			headers: { 'Authorization': `Bearer ${token}` }
		});

		if (response.ok) {
			const data = await response.json();
			document.getElementById('role-container').classList.remove('hidden');
			document.getElementById('user-role').innerText = data.role;
			
			// ПОЯВЛЕНИЕ КНОПКИ: Находим кнопку по ID и убираем скрывающий класс
			document.getElementById('change-role-btn').classList.remove('hidden');
		} else {
			const errorData = await response.json();
			alert(errorData.detail || "Доступ запрещен");
		}
	} catch (error) {
		console.error("Ошибка при запросе к админ панели:", error);
		alert("Ошибка соединения с сервером");
	}
}

async function changeRolePrompt() {
	const userId = prompt("Введите ID пользователя, которому нужно изменить роль:");
	if (!userId) return;

	const newRole = prompt("Введите новую роль (например: Admin, User):");
	if (!newRole) return;

	const token = localStorage.getItem('token');
	
	try {
		const response = await fetch('http://127.0.0.1:8000/home/change-role', {
			method: 'PATCH',
			headers: { 
				'Content-Type': 'application/json',
				'Authorization': `Bearer ${token}` 
			},
			body: JSON.stringify({
				user_id: parseInt(userId),
				new_role: newRole
			})
		});

		const data = await response.json();

		if (response.ok) {
			alert(data.message);
		} else {
			alert("Ошибка: " + (data.detail || "Не удалось изменить роль"));
		}
	} catch (error) {
		console.error("Ошибка запроса:", error);
		alert("Ошибка соединения с сервером");
	}
}

function logout() {
	localStorage.removeItem('token');
	window.location.href = 'index.html';
}

checkAuth();

console.log("[profile.js] has loaded!")