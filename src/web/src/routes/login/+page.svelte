<script lang="ts">
	import { goto } from '$app/navigation';
	import { login } from '$lib/auth';
	import { t } from '$lib/i18n';

	let username = '';
	let password = '';
	let error = '';
	let loading = false;

	async function submit() {
		error = '';
		loading = true;
		try {
			await login(username, password);
			await goto('/dashboard');
		} catch (e) {
			error = e instanceof Error ? e.message : t('error');
		} finally {
			loading = false;
		}
	}
</script>

<div style="max-width: 380px; margin: 3rem auto; padding: 1rem">
	<h1>{t('login')}</h1>
	<form on:submit|preventDefault={submit} class="card" style="display: grid; gap: 0.75rem">
		<label>
			<span class="muted">{t('username')}</span>
			<input bind:value={username} required autocomplete="username" />
		</label>
		<label>
			<span class="muted">{t('password')}</span>
			<input type="password" bind:value={password} required autocomplete="current-password" />
		</label>
		{#if error}<p class="error">{error}</p>{/if}
		<button type="submit" class="primary" disabled={loading}>{loading ? $t('loading') : $t('login')}</button>
	</form>
</div>
