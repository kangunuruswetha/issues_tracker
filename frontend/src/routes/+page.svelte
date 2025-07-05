<script>
	import { goto } from '$app/navigation';
	import { isAuthenticated } from '$lib/stores/auth.js';
	import { onMount } from 'svelte';

	onMount(() => {
		// Redirect based on authentication status
		if ($isAuthenticated) {
			goto('/dashboard'); // If authenticated, go to dashboard
		} else {
			goto('/login'); // If not authenticated, go to login
		}
	});
</script>

<!-- This page will typically be blank as it immediately redirects -->
<div class="flex items-center justify-center min-h-screen bg-gray-50">
	<p class="text-lg text-gray-600">Loading...</p>
</div>