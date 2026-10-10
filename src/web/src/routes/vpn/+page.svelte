<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';
	import { t } from '$lib/i18n';

	let enabled = false;
	let listen_port = 51820;
	let address = '10.200.0.1/24';
	let note = '';

	onMount(async () => {
		try {
			const cfg = await api.get<{ enabled: boolean; interface: { listen_port: number; address: string }; note?: string }>(
				'/api/v1/vpn/wireguard'
			);
			enabled = cfg.enabled;
			listen_port = cfg.interface?.listen_port ?? 51820;
			address = cfg.interface?.address ?? address;
		} catch (e) {
			if (e && typeof e === 'object' && 'status' in e && (e as { status: number }).status === 401) {
				await goto('/login');
			}
		}
	});

	async function save() {
		const res = await api.put<{ note?: string }>('/api/v1/vpn/wireguard', {
			enabled,
			interface: { listen_port, address },
			peers: []
		});
		note = res.note ?? 'Saved';
	}
</script>

<h1>{t('vpn')} (WireGuard)</h1>
<section class="card">
	<label><input type="checkbox" bind:checked={enabled} /> Enable WireGuard</label>
	<label style="display:block;margin-top:0.5rem">Listen port <input type="number" bind:value={listen_port} /></label>
	<label style="display:block;margin-top:0.5rem">Tunnel address <input bind:value={address} /></label>
	<button type="button" class="primary" style="margin-top:0.75rem" on:click={save}>{t('save')}</button>
	{#if note}<p class="muted">{note}</p>{/if}
</section>
