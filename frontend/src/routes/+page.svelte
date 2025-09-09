<!-- This runs only once, when the module is first evaluated -->
<script module>
	let total = 0;
</script>

<script lang="ts">
	let item_id = $state();
	let word = $state();

	async function roll() {
		const res = await fetch('http://127.0.0.1:8000/getItems');
		const data = await res.json();
	}


</script>

<main>
	<h1 class="title">ProjectBoard</h1>
	<p class="subtitle">Organiseer je projecten, notities en taken op één plek.</p>

	<div class="board">
		<div class="column"><h2>Open</h2></div>
		<div class="column"><h2>In Progress</h2></div>
		<div class="column"><h2>Done</h2></div>
	</div>
</main>

<style>
	:root {
		--primary: #50c878;	/* nog veranderen */
		--secondary: #2e282a;  /* nog veranderen */
		--accent: #DD1155;		/* nog veranderen */
		--background: #2e282a; 
		--surface: #50c878;
		--text: #eaeaea;
	}
	main {
		font-family: system-ui, sans-serif;
		padding: 2rem;
		background: var(--background);
		color: var(--text);
		min-height: 100vh;
	}

	.title { color: var(--primary); margin-bottom: 0.5rem; }
	.subtitle { color: var(--text); margin-bottom: 2rem; }

	.board { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }
	.column { background: var(--surface); padding: 1rem; border-radius: 12px; min-height: 200px; }
	.column h2 { margin-top: 0; color: var(--secondary); }
</style>