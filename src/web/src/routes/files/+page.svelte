<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';
	import { t } from '$lib/i18n';

	type Item = { name: string; path: string; is_dir: boolean; size_bytes: number | null };

	let path = '/data';
	let items: Item[] = [];
	let error = '';

	async function load(p = path) {
		error = '';
		try {
			const res = await api.get<{ path: string; items: Item[] }>(
				`/api/v1/files?path=${encodeURIComponent(p)}`
			);
			path = res.path;
			items = res.items;
		} catch (e) {
			if (e && typeof e === 'object' && 'status' in e && (e as { status: number }).status === 401) {
				await goto('/login');
				return;
			}
			error = e instanceof Error ? e.message : 'Error';
			items = [];
		}
	}

	onMount(() => load('/data'));

	function parentPath() {
		const parts = path.replace(/\\/g, '/').split('/').filter(Boolean);
		parts.pop();
		return '/' + parts.join('/') || '/data';
	}
</script>

<h1>{t('files')}</h1>

<div class="toolbar">
	<input bind:value={path} style="flex:1;max-width:480px" />
	<button type="button" on:click={() => load(path)}>{t('open')}</button>
	<button type="button" on:click={() => load(parentPath())}>{t('up')}</button>
	<button type="button" on:click={() => load(path)}>{t('refresh')}</button>
</div>

{#if error}<p class="error">{error}</p>{/if}

<section class="card" style="margin-top: 1rem">
	<p class="muted">{t('filePath')}: {path}</p>
	{#if items.length === 0}
		<p class="muted">{t('noData')}</p>
	{:else}
		<table class="table">
			<thead><tr><th>Name</th><th>Type</th><th>Size</th></tr></thead>
			<tbody>
				{#each items as item}
					<tr>
						<td>
							{#if item.is_dir}
								<button type="button" class="linkish" on:click={() => load(item.path)}>{item.name}/</button>
							{:else}
								{item.name}
							{/if}
						</td>
						<td>{item.is_dir ? 'dir' : 'file'}</td>
						<td>{item.size_bytes ?? '—'}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{/if}
</section>

<style>
	.linkish {
		background: none;
		border: none;
		padding: 0;
		color: var(--accent);
		cursor: pointer;
		font: inherit;
	}
</style>
