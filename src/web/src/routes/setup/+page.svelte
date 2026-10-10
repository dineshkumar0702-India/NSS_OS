<script lang="ts">
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';
	import { t } from '$lib/i18n';

	let hostname = 'opennas';
	let timezone = 'Asia/Kolkata';
	let admin_username = 'admin';
	let admin_password = '';
	let error = '';
	let loading = false;

	async function submit() {
		error = '';
		loading = true;
		try {
			await api.post('/api/v1/system/setup', {
				hostname,
				timezone,
				admin_username,
				admin_password
			});
			await goto('/login');
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error';
		} finally {
			loading = false;
		}
	}
</script>

<div style="max-width: 420px; margin: 3rem auto; padding: 1rem">
	<h1>{t('setup')}</h1>
	<form on:submit|preventDefault={submit} class="card" style="display: grid; gap: 0.75rem">
		<label>
			<span class="muted">{t('hostname')}</span>
			<input bind:value={hostname} required />
		</label>
		<label>
			<span class="muted">{t('timezone')}</span>
			<input bind:value={timezone} required />
		</label>
		<label>
			<span class="muted">{t('adminUser')}</span>
			<input bind:value={admin_username} required autocomplete="username" />
		</label>
		<label>
			<span class="muted">{t('adminPassword')}</span>
			<input type="password" bind:value={admin_password} required minlength="12" autocomplete="new-password" />
		</label>
		{#if error}<p class="error">{error}</p>{/if}
		<button type="submit" class="primary" disabled={loading}>{loading ? $t('loading') : $t('save')}</button>
	</form>
</div>
