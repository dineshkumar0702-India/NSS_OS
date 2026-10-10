<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';
	import { t } from '$lib/i18n';

	type Disk = { path: string; size_bytes: number; model?: string };
	type Pool = { id: string; name: string; backend: string; state: string };

	let disks: Disk[] = [];
	let pools: Pool[] = [];
	let poolName = 'tank';
	let devices = '/dev/sdb';
	let plan: { confirm_token?: string; commands_preview?: string[]; warnings?: string[] } | null = null;
	let message = '';
	let error = '';

	async function load() {
		error = '';
		try {
			const d = await api.get<{ items: Disk[] }>('/api/v1/storage/disks');
			const p = await api.get<{ items: Pool[] }>('/api/v1/storage/pools');
			disks = d.items;
			pools = p.items;
		} catch (e) {
			if (e && typeof e === 'object' && 'status' in e && (e as { status: number }).status === 401) {
				await goto('/login');
				return;
			}
			error = e instanceof Error ? e.message : 'Error';
		}
	}

	onMount(load);

	async function dryRun() {
		plan = null;
		message = '';
		error = '';
		const devList = devices.split(/[\s,]+/).filter(Boolean);
		try {
			plan = await api.post('/api/v1/storage/pools', {
				name: poolName,
				backend: 'btrfs',
				devices: devList,
				dry_run: true
			});
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error';
		}
	}

	async function confirmCreate() {
		if (!plan?.confirm_token) return;
		message = '';
		error = '';
		const devList = devices.split(/[\s,]+/).filter(Boolean);
		try {
			const res = await api.post<{ job_id: string }>('/api/v1/storage/pools', {
				name: poolName,
				backend: 'btrfs',
				devices: devList,
				confirm_token: plan.confirm_token
			});
			message = `Job ${res.job_id} started`;
			plan = null;
			await load();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error';
		}
	}

	function fmt(bytes: number) {
		if (!bytes) return '—';
		const gb = bytes / 1024 ** 3;
		return `${gb.toFixed(1)} GB`;
	}
</script>

<h1>{t('storage')}</h1>

<div class="toolbar">
	<button type="button" on:click={load}>{t('refresh')}</button>
</div>

{#if error}<p class="error">{error}</p>{/if}
{#if message}<p style="color: var(--ok)">{message}</p>{/if}

<div class="grid-2" style="margin-top: 1rem">
	<section class="card">
		<h2>{t('disks')}</h2>
		{#if disks.length === 0}
			<p class="muted">{t('noData')}</p>
		{:else}
			<table class="table">
				<thead><tr><th>Path</th><th>Size</th><th>Model</th></tr></thead>
				<tbody>
					{#each disks as d}
						<tr>
							<td>{d.path}</td>
							<td>{fmt(d.size_bytes)}</td>
							<td>{d.model ?? '—'}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		{/if}
	</section>

	<section class="card">
		<h2>{t('pools')}</h2>
		{#if pools.length === 0}
			<p class="muted">{t('noData')}</p>
		{:else}
			<ul>
				{#each pools as p}
					<li>{p.name} ({p.backend}) — {p.state}</li>
				{/each}
			</ul>
		{/if}
	</section>
</div>

<section class="card" style="margin-top: 1rem">
	<h2>{t('createPool')}</h2>
	<label>
		<span class="muted">Name</span>
		<input bind:value={poolName} />
	</label>
	<label style="display:block;margin-top:0.5rem">
		<span class="muted">Devices (space-separated)</span>
		<input bind:value={devices} />
	</label>
	<div class="toolbar" style="margin-top: 0.75rem">
		<button type="button" class="primary" on:click={dryRun}>{t('dryRun')}</button>
		{#if plan?.confirm_token}
			<button type="button" on:click={confirmCreate}>{t('confirmCreate')}</button>
		{/if}
	</div>
	{#if plan?.warnings?.length}
		<ul class="error">
			{#each plan.warnings as w}<li>{w}</li>{/each}
		</ul>
	{/if}
	{#if plan?.commands_preview}
		<pre style="font-size:0.8rem;overflow:auto">{plan.commands_preview.join('\n')}</pre>
	{/if}
</section>
