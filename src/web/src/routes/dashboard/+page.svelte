<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api, type SystemStatus } from '$lib/api';
	import { t } from '$lib/i18n';

	let status: SystemStatus | null = null;
	let caps: Record<string, unknown> | null = null;
	let services: { items: { unit: string; active: string }[] } | null = null;
	let error = '';

	onMount(async () => {
		try {
			status = await api.get<SystemStatus>('/api/v1/system/status');
			if (!status.setup_complete) {
				await goto('/setup');
				return;
			}
			caps = await api.get('/api/v1/system/capabilities');
			services = await api.get('/api/v1/services');
		} catch (e) {
			if (e && typeof e === 'object' && 'status' in e && (e as { status: number }).status === 401) {
				await goto('/login');
				return;
			}
			error = e instanceof Error ? e.message : t('error');
		}
	});
</script>

<h1>{t('dashboard')}</h1>

{#if error}
	<p class="error">{error}</p>
{:else if !status}
	<p class="muted">{t('loading')}</p>
{:else}
	<div class="grid-2" style="margin-top: 1rem">
		<section class="card">
			<h2>{t('systemStatus')}</h2>
			<p><strong>{status.codename}</strong> v{status.version}</p>
			<p class="muted">Uptime: {Math.floor(status.uptime_seconds / 60)} min</p>
		</section>
		{#if caps}
			<section class="card">
				<h2>{t('capabilities')}</h2>
				<ul>
					<li>Profile: {caps.profile}</li>
					<li>RAM: {caps.ram_mb} MB</li>
					<li>Docker: {caps.docker ? 'yes' : 'no'}</li>
					<li>ZFS: {caps.zfs ? 'yes' : 'no'}</li>
				</ul>
			</section>
		{/if}
	</div>
	{#if services?.items?.length}
		<section class="card" style="margin-top: 1rem">
			<h2>Services</h2>
			<table class="table">
				<thead><tr><th>Unit</th><th>Active</th></tr></thead>
				<tbody>
					{#each services.items as s}
						<tr><td>{s.unit}</td><td>{s.active}</td></tr>
					{/each}
				</tbody>
			</table>
		</section>
	{/if}
{/if}
