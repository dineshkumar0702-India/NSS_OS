import { writable } from 'svelte/store';
import { api, type UserPublic } from './api';

export const user = writable<UserPublic | null>(null);

export async function refreshUser() {
	try {
		user.set(await api.get<UserPublic>('/api/v1/auth/me'));
	} catch {
		user.set(null);
	}
}

export async function login(username: string, password: string) {
	await api.post<UserPublic>('/api/v1/auth/login', { username, password });
	await refreshUser();
}

export async function logout() {
	try {
		await api.post('/api/v1/auth/logout');
	} finally {
		user.set(null);
	}
}
