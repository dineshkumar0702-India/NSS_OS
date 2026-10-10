export class ApiError extends Error {
	status: number;
	body: unknown;
	constructor(status: number, body: unknown) {
		super(typeof body === 'object' && body && 'detail' in body ? String((body as { detail: string }).detail) : `HTTP ${status}`);
		this.status = status;
		this.body = body;
	}
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
	const res = await fetch(path, {
		credentials: 'include',
		headers: {
			'Content-Type': 'application/json',
			...(init.headers ?? {})
		},
		...init
	});
	const text = await res.text();
	const data = text ? JSON.parse(text) : null;
	if (!res.ok) throw new ApiError(res.status, data);
	return data as T;
}

export const api = {
	get: <T>(path: string) => request<T>(path),
	post: <T>(path: string, body?: unknown) =>
		request<T>(path, { method: 'POST', body: body ? JSON.stringify(body) : undefined }),
	put: <T>(path: string, body?: unknown) =>
		request<T>(path, { method: 'PUT', body: body ? JSON.stringify(body) : undefined }),
	patch: <T>(path: string, body?: unknown) =>
		request<T>(path, { method: 'PATCH', body: body ? JSON.stringify(body) : undefined }),
	delete: <T>(path: string) => request<T>(path, { method: 'DELETE' })
};

export type SystemStatus = {
	version: string;
	codename: string;
	setup_complete: boolean;
	uptime_seconds: number;
};

export type UserPublic = {
	id: string;
	username: string;
	role: string;
	display_name: string;
};
