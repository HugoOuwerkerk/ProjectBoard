<!-- This runs only once, when the module is first evaluated -->
<script module>
	let total = 0;
</script>

<script lang="ts">
	let item_id = $state();
	let word = $state();

	async function roll() {
		const res = await fetch('http://127.0.0.1:8000/items/42?word=ik');
		const data = await res.json();
		item_id = data.item_id;
		word = data.word;
	}


</script>

<h1>item_id = {item_id}</h1> 
<h1>word = {word}</h1>
<button onclick={roll}>Roll the dice</button>

<style>

</style>