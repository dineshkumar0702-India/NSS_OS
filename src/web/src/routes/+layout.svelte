<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { theme, setTheme } from '$lib/theme';
	import { t } from '$lib/i18n';
	import { user, refreshUser, logout } from '$lib/auth';

	const publicPaths = ['/login', '/setup'];

	onMount(() => {
		setTheme($theme);
		refreshUser();
	});

	$: path = $page.url.pathname;
	$: isPublic = publicPaths.some((p) => path === p || path.startsWith(p + '/'));

	function onThemeChange(e) {
		const value = e.currentTarget?.value ?? 'light';
		setTheme(value === 'dark' ? 'dark' : 'light');
	}
</script>

{#if isPublic}
	<slot />
{:else}
	<div class="layout">
		<aside class="sidebar">
			<strong>{t('appName')}</strong>
			<nav class="nav" style="margin-top: 1rem">
				<a href="/dashboard" class:active={path.startsWith('/dashboard')}>{t('dashboard')}</a>
				<a href="/storage" class:active={path.startsWith('/storage')}>{t('storage')}</a>
				<a href="/shares" class:active={path.startsWith('/shares')}>{t('shares')}</a>
				<a href="/files" class:active={path.startsWith('/files')}>{t('files')}</a>
				<a href="/users" class:active={path.startsWith('/users')}>{t('users')}</a>
				<a href="/apps" class:active={path.startsWith('/apps')}>{t('apps')}</a>
				<a href="/backups" class:active={path.startsWith('/backups')}>{t('backups')}</a>
				<a href="/notifications" class:active={path.startsWith('/notifications')}>{t('notifications')}</a>
				<a href="/vpn" class:active={path.startsWith('/vpn')}>{t('vpn')}</a>
				<a href="/updates" class:active={path.startsWith('/updates')}>Updates</a>
				<a href="/security" class:active={path.startsWith('/security')}>Security</a>
			</nav>
			<div style="margin-top: 1.5rem; font-size: 0.85rem">
				<label class="muted" style="display:block">{t('theme')}</label>
				<select
					on:change={onThemeChange}
					value={$theme}
				>
					<option value="light">{t('light')}</option>
					<option value="dark">{t('dark')}</option>
				</select>
				{#if $user}
					<p style="margin-top:1rem" class="muted">{$user.username} ({$user.role})</p>
					<button type="button" style="margin-top:0.5rem;width:100%" on:click={() => logout()}>
						{t('logout')}
					</button>
				{/if}
			</div>
		</aside>
		<main class="main">
			<slot />
		</main>
	</div>
{/if}
