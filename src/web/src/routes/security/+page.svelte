<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';

	let advisor: { score: number; findings: { severity: string; title: string; remediation: string }[] } | null =
		null;

	onMount(async () => {
		try {
			advisor = await api.get('/api/v1/security/advisor');
		} catch {
			await goto('/login');
		}
	});
</script>

<h1>Security advisor</h1>
{#if advisor}
	<p>Score: <strong>{advisor.score}</strong> / 100</p>
	<ul>
		{#each advisor.findings as f}
			<li class="card" style="margin:0.5rem 0">
				<strong>{f.severity}</strong> — {f.title}
				<div class="muted">{f.remediation}</div>
			</li>
		{/each}
	</ul>
	{#if advisor.findings.length === 0}
		<p class="muted">No issues reported.</p>
	{/if}
{/if}
