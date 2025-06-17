// place files you want to import through the `$lib` alias in this folder.
let API_BASE = '';
const isDev = import.meta.env.DEV;
const isBrowser = typeof window !== 'undefined';

if (isDev && isBrowser) {
	API_BASE = localStorage.getItem('FLASK_API_BASE') || 'http://127.0.0.1:5000';

	// Optionally prompt the user to change it
	const override = confirm(`Current Flask API is set to: ${API_BASE}\n\nDo you want to change it?`);
	if (override) {
		const input = prompt('Enter Flask API URL (e.g., http://127.0.0.1:5000)');
		if (input) {
			API_BASE = input;
			localStorage.setItem('FLASK_API_BASE', API_BASE);
		}
	}
}

export function apiFetch(path, options = {}) {
	const url = isDev && isBrowser ? `${API_BASE}${path}` : path;
	return fetch(url, options);
}