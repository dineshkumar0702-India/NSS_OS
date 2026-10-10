<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api, type UserPublic } from '$lib/api';
	import { t } from '$lib/i18n';

	let items: UserPublic[] = [];
	let username = '';
	let password = '';
	let role = 'operator';
	let error = '';

	async function load() {
		error = '';
		try {
			const res = await api.get<{ items: UserPublic[] }>('/api/v1/users');
			items = res.items;
		} catch (e) {
			if (e && typeof e === 'object' && 'status' in e && (e as { status: number }).status === 401) {
				await goto('/login');
				return;
			}
			error = e instanceof Error ? e.message : 'Error';
		}
	}

	onMount(load);

	async function create() {
		error = '';
		try {
			await api.post('/api/v1/users', { username, password, role });
			username = '';
			password = '';
			await load();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error';
		}
	}
</script>

<h1>{t('users')}</h1>
{#if error}<p class="error">{error}</p>{/if}

<section class="card" style="margin: 1rem 0">
	<h2>{t('createUser')}</h2>
	<label>
		<span class="muted">{t('username')}</span>
		<input bind:value={username} />
	</label>
	<label style="display:block;margin-top:0.5rem">
		<span class="muted">{t('password')}</span>
		<input type="password" bind:value={password} />
	</label>
	<label style="display:block;margin-top:0.5rem">
		<span class="muted">{t('role')}</span>
		<select bind:value={role}>
			<option value="viewer">viewer</option>
			<option value="operator">operator</option>
			<option value="admin">admin</option>
		</select>
	</label>
	<button type="button" class="primary" style="margin-top:0.75rem" on:click={create}>{t('save')}</button>
</section>

<section class="card">
	<table class="table">
		<thead><tr><th>User</th><th>Role</th></tr></thead>
		<tbody>
			{#each items as u}
				<tr><td>{u.username}</td><td>{u.role}</td></tr>
			{/each}
		</tbody>
	</table>
</section>
