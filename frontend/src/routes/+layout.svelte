<script lang="ts">
	import favicon from '$lib/assets/favicon.png';
	import "$lib/style.css";

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>ProjectBoard</title>
</svelte:head>

{@render children?.()}
