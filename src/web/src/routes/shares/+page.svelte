<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';
	import { t } from '$lib/i18n';

	type Share = { id: string; name: string; volume_id: string; protocols: string[] };

	let items: Share[] = [];
	let name = '';
	let volume_id = '';
	let error = '';
	let ok = '';

	async function load() {
		error = '';
		try {
			const res = await api.get<{ items: Share[] }>('/api/v1/shares');
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
		ok = '';
		error = '';
		try {
			await api.post('/api/v1/shares', { name, volume_id, protocols: ['smb'] });
			name = '';
			volume_id = '';
			ok = 'Created';
			await load();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error';
		}
	}
</script>

<h1>{t('shares')}</h1>
{#if error}<p class="error">{error}</p>{/if}
{#if ok}<p style="color:var(--ok)">{ok}</p>{/if}

<section class="card" style="margin: 1rem 0">
	<h2>{t('createShare')}</h2>
	<label>
		<span class="muted">{t('shareName')}</span>
		<input bind:value={name} />
	</label>
	<label style="display:block;margin-top:0.5rem">
		<span class="muted">{t('volumeId')}</span>
		<input bind:value={volume_id} placeholder="UUID from storage/volumes (API)" />
	</label>
	<button type="button" class="primary" style="margin-top:0.75rem" on:click={create}>{t('save')}</button>
</section>

<section class="card">
	{#if items.length === 0}
		<p class="muted">{t('noData')}</p>
	{:else}
		<table class="table">
			<thead><tr><th>Name</th><th>Volume</th><th>Protocols</th></tr></thead>
			<tbody>
				{#each items as s}
					<tr>
						<td>{s.name}</td>
						<td class="muted">{s.volume_id}</td>
						<td>{s.protocols.join(', ')}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{/if}
</section>
