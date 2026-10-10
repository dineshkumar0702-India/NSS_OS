import { writable } from 'svelte/store';

export type Theme = 'light' | 'dark';

function initialTheme(): Theme {
	if (typeof localStorage === 'undefined') return 'light';
	return localStorage.getItem('opennas-theme') === 'dark' ? 'dark' : 'light';
}

export const theme = writable<Theme>(initialTheme());

export function applyTheme(value: Theme) {
	if (typeof document === 'undefined') return;
	document.documentElement.dataset.theme = value;
	localStorage.setItem('opennas-theme', value);
}

export function setTheme(value: Theme) {
	theme.set(value);
	applyTheme(value);
}
