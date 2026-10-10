<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';

	let status: Record<string, unknown> | null = null;
	let plan: Record<string, unknown> | null = null;
	let message = '';

	onMount(async () => {
		try {
			status = await api.get('/api/v1/updates/status');
		} catch {
			await goto('/login');
		}
	});

	async function dryRun() {
		plan = await api.post('/api/v1/updates/apply', { dry_run: true });
	}

	async function apply() {
		if (!plan?.confirm_token) return;
		const res = await api.post<{ job_id: string }>('/api/v1/updates/apply', {
			confirm_token: plan.confirm_token,
			snapshot_label: plan.snapshot_label
		});
		message = `Update job ${res.job_id}`;
	}

	async function rollback() {
		const res = await api.post('/api/v1/updates/rollback', {});
		message = JSON.stringify(res);
	}
</script>

<h1>System updates</h1>
{#if status}
	<section class="card">
		<pre style="font-size:0.85rem;overflow:auto">{JSON.stringify(status, null, 2)}</pre>
	</section>
{/if}
<div class="toolbar">
	<button type="button" class="primary" on:click={dryRun}>Plan OTA (dry-run)</button>
	<button type="button" on:click={apply} disabled={!plan?.confirm_token}>Apply</button>
	<button type="button" on:click={rollback}>Rollback</button>
</div>
{#if message}<p style="color:var(--ok)">{message}</p>{/if}
