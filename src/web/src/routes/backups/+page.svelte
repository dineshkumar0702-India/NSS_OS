<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';
	import { t } from '$lib/i18n';

	type Policy = { id: string; name: string; source_path: string; target_path: string };

	let policies: Policy[] = [];
	let name = 'daily-home';
	let source_path = '/data';
	let target_path = '/data/backups/restic-repo';
	let error = '';
	let message = '';

	async function load() {
		try {
			policies = (await api.get<{ items: Policy[] }>('/api/v1/backups/policies')).items;
		} catch (e) {
			if (e && typeof e === 'object' && 'status' in e && (e as { status: number }).status === 401) {
				await goto('/login');
			}
		}
	}

	onMount(load);

	async function savePolicy() {
		error = '';
		await api.post('/api/v1/backups/policies', { name, source_path, target_path, enabled: true });
		await load();
	}

	async function runNow() {
		message = '';
		const res = await api.post<{ job_id: string }>('/api/v1/backups/run', {
			source_path,
			target_path
		});
		message = `Backup job ${res.job_id}`;
	}
</script>

<h1>{t('backups')}</h1>
{#if error}<p class="error">{error}</p>{/if}
{#if message}<p style="color:var(--ok)">{message}</p>{/if}

<section class="card" style="margin:1rem 0">
	<h2>Policy</h2>
	<label><span class="muted">Name</span><input bind:value={name} /></label>
	<label style="display:block;margin-top:0.5rem"><span class="muted">Source</span><input bind:value={source_path} /></label>
	<label style="display:block;margin-top:0.5rem"><span class="muted">{t('backupTarget')}</span><input bind:value={target_path} /></label>
	<div class="toolbar" style="margin-top:0.75rem">
		<button type="button" on:click={savePolicy}>{t('save')}</button>
		<button type="button" class="primary" on:click={runNow}>{t('runBackup')}</button>
	</div>
</section>

<section class="card">
	<ul>
		{#each policies as p}
			<li>{p.name}: {p.source_path} → {p.target_path}</li>
		{/each}
	</ul>
</section>
