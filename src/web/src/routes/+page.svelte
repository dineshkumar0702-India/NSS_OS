<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api, type SystemStatus } from '$lib/api';

	onMount(async () => {
		try {
			const status = await api.get<SystemStatus>('/api/v1/system/status');
			if (!status.setup_complete) {
				await goto('/setup');
				return;
			}
			await goto('/dashboard');
		} catch {
			await goto('/login');
		}
	});
</script>

<p class="muted">Loading…</p>
