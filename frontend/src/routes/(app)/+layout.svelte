<script lang="ts">
	import { goto, invalidateAll } from '$app/navigation';

	let { children, data } = $props();
	let loggingOut = $state(false);

	async function logout() {
		if (loggingOut) return;
		loggingOut = true;
		try {
			await fetch('/api/logout', { method: 'POST' });
			await invalidateAll();
			await goto('/login');
		} finally {
			loggingOut = false;
		}
	}
</script>

<div class="app-shell">
	<header class="app-header">
		<div class="brand">
			<a href="/" class="brand-link">ProjectBoard</a>
		</div>
		<div class="spacer"></div>
		<p class="user">Signed in as <strong>{data.user.username}</strong></p>
		<button class="btn ghost" type="button" onclick={logout} disabled={loggingOut}>
			{loggingOut ? 'Logging out…' : 'Log out'}
		</button>
	</header>

	<main class="app-main">
		{@render children?.()}
	</main>
</div>
