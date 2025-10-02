<script lang="ts">
	import { goto, invalidateAll } from '$app/navigation';

	let username = $state('');
	let password = $state('');
	let loading = $state(false);
	let error = $state('');

	async function handleSubmit(event: SubmitEvent) {
		event.preventDefault();
		if (loading) return;

		error = '';
		loading = true;

		try {
			const res = await fetch('/api/login', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username, password })
			});

			if (!res.ok) {
				let detail = 'Unable to sign in';
				try {
					const data = await res.json();
					detail = data?.detail ?? detail;
				} catch (parseError) {
					console.error('Failed to parse login error', parseError);
				}
				error = detail;
				return;
			}

			username = '';
			password = '';
			await invalidateAll();
			await goto('/');
		} finally {
			loading = false;
		}
	}
</script>

<main class="auth">
	<section class="panel">
		<header>
			<h1>ProjectBoard</h1>
			<p>Sign in to manage your projects.</p>
		</header>

		<form onsubmit={handleSubmit} class="auth-form">
			<label class="field">
				<span>Username</span>
				<input
					type="text"
					name="username"
					autocomplete="username"
					required
					bind:value={username}
				/>
			</label>

			<label class="field">
				<span>Password</span>
				<input
					type="password"
					name="password"
					autocomplete="current-password"
					required
					bind:value={password}
				/>
			</label>

			{#if error}
				<p class="error">{error}</p>
			{/if}

			<button class="btn primary" type="submit" disabled={loading}>
				{loading ? 'Signing in…' : 'Sign in'}
			</button>
		</form>

		<footer class="hint">
			<p>Default credentials: <code>admin / admin</code></p>
			<p>Need an account? <a href="/signup">Create one</a></p>
		</footer>
	</section>
</main>
