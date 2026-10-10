<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';
	import { t } from '$lib/i18n';

	type CatalogItem = { id: string; name: string; description?: string; template_id: string };
	type Instance = { id: string; template_id: string; state: string; compose_project: string };

	let catalog: CatalogItem[] = [];
	let instances: Instance[] = [];
	let error = '';
	let message = '';

	async function load() {
		error = '';
		try {
			catalog = (await api.get<{ items: CatalogItem[] }>('/api/v1/apps/catalog')).items;
			instances = (await api.get<{ items: Instance[] }>('/api/v1/apps/instances')).items;
		} catch (e) {
			if (e && typeof e === 'object' && 'status' in e && (e as { status: number }).status === 401) {
				await goto('/login');
				return;
			}
			error = e instanceof Error ? e.message : 'Error';
		}
	}

	onMount(load);

	async function install(template_id: string) {
		message = '';
		try {
			const res = await api.post<{ job_id: string }>('/api/v1/apps/instances', { template_id });
			message = `Install job ${res.job_id}`;
			await load();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error';
		}
	}

	async function action(id: string, action: string) {
		try {
			await api.post(`/api/v1/apps/instances/${id}/action`, { action });
			await load();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error';
		}
	}
</script>

<h1>{t('apps')}</h1>
{#if error}<p class="error">{error}</p>{/if}
{#if message}<p style="color:var(--ok)">{message}</p>{/if}

<section class="card" style="margin: 1rem 0">
	<h2>Catalog</h2>
	{#if catalog.length === 0}
		<p class="muted">{t('noData')}</p>
	{:else}
		<ul>
			{#each catalog as item}
				<li style="margin-bottom:0.75rem">
					<strong>{item.name}</strong> — {item.description ?? ''}
					<button type="button" class="primary" style="margin-left:0.5rem" on:click={() => install(item.template_id)}>
						{t('installApp')}
					</button>
				</li>
			{/each}
		</ul>
	{/if}
</section>

<section class="card">
	<h2>Installed</h2>
	{#if instances.length === 0}
		<p class="muted">{t('noData')}</p>
	{:else}
		<table class="table">
			<thead><tr><th>App</th><th>State</th><th>Actions</th></tr></thead>
			<tbody>
				{#each instances as inst}
					<tr>
						<td>{inst.template_id}</td>
						<td>{inst.state}</td>
						<td>
							<button type="button" on:click={() => action(inst.id, 'start')}>{t('start')}</button>
							<button type="button" on:click={() => action(inst.id, 'stop')}>{t('stop')}</button>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{/if}
</section>
