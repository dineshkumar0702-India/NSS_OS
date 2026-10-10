<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';
	import { t } from '$lib/i18n';

	let items: { type: string; name: string; config: Record<string, string> }[] = [];
	let type = 'email';
	let name = 'alerts';
	let webhook = '';

	onMount(async () => {
		try {
			const res = await api.get<{ items: typeof items }>('/api/v1/notifications/channels');
			items = res.items;
		} catch (e) {
			if (e && typeof e === 'object' && 'status' in e && (e as { status: number }).status === 401) {
				await goto('/login');
			}
		}
	});

	async function save() {
		await api.put('/api/v1/notifications/channels', {
			items: [{ type, name, enabled: true, config: { webhook_url: webhook } }]
		});
		items = (await api.get<{ items: typeof items }>('/api/v1/notifications/channels')).items;
	}
</script>

<h1>{t('notifications')}</h1>
<section class="card" style="margin:1rem 0">
	<label>Type <select bind:value={type}><option value="email">email</option><option value="webhook">webhook</option><option value="telegram">telegram</option></select></label>
	<label style="display:block;margin-top:0.5rem">Name <input bind:value={name} /></label>
	<label style="display:block;margin-top:0.5rem">Webhook URL <input bind:value={webhook} /></label>
	<button type="button" class="primary" style="margin-top:0.75rem" on:click={save}>{t('save')}</button>
</section>
<ul>
	{#each items as c}
		<li>{c.name} ({c.type})</li>
	{/each}
</ul>
