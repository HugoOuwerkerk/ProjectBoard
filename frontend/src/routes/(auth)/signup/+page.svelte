<script lang="ts">
	import { goto, invalidateAll } from '$app/navigation';

	let username = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let loading = $state(false);
	let error = $state('');

	async function handleSubmit(event: SubmitEvent) {
		event.preventDefault();
		if (loading) return;

		const trimmed = username.trim();
		if (trimmed !== username) {
			username = trimmed;
		}

		if (username.length < 3) {
			error = 'Username must be at least 3 characters long.';
			return;
		}

		if (password.length < 6) {
			error = 'Password must be at least 6 characters long.';
			return;
		}

		if (password !== confirmPassword) {
			error = 'Passwords do not match.';
			return;
		}

		error = '';
		loading = true;

		try {
			const res = await fetch('/api/signup', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username, password })
			});

			if (!res.ok) {
				let detail: string | string[] = 'Unable to create account';
				try {
					const data = await res.json();
					detail = data?.detail ?? detail;
				} catch (parseError) {
					console.error('Failed to parse signup error', parseError);
				}

				error = Array.isArray(detail) ? detail.join(' • ') : detail;
				return;
			}

			username = '';
			password = '';
			confirmPassword = '';
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
			<h1>Create an account</h1>
			<p>Sign up to start tracking your projects.</p>
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
					autocomplete="new-password"
					required
					bind:value={password}
				/>
			</label>

			<label class="field">
				<span>Confirm password</span>
				<input
					type="password"
					name="confirm"
					autocomplete="new-password"
					required
					bind:value={confirmPassword}
				/>
			</label>

			{#if error}
				<p class="error">{error}</p>
			{/if}

			<button class="btn primary" type="submit" disabled={loading}>
				{loading ? 'Creating account…' : 'Sign up'}
			</button>
		</form>

		<footer class="hint">
			<p>Already have an account? <a href="/login">Log in</a></p>
		</footer>
	</section>
</main>
