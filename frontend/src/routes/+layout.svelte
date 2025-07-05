<script>
	import '../app.css';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { isAuthenticated, user, logout } from '$lib/stores/auth.js';
	import { websocketManager } from '$lib/utils/websocket.js';
	import { goto } from '$app/navigation';

	let showMobileMenu = false;

	onMount(() => {
		// Initialize WebSocket connection
		websocketManager.connect();
		
		return () => {
			websocketManager.disconnect();
		};
	});

	function handleLogout() {
		logout();
		goto('/login');
	}

	function toggleMobileMenu() {
		showMobileMenu = !showMobileMenu;
	}

	$: isLoginPage = $page.route.id === '/login' || $page.route.id === '/register';
</script>

<div class="min-h-screen bg-gray-50">
	{#if $isAuthenticated && !isLoginPage}
		<!-- Navigation -->
		<nav class="bg-white shadow-sm border-b border-gray-200">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div class="flex justify-between h-16">
					<div class="flex">
						<div class="flex-shrink-0 flex items-center">
							<h1 class="text-xl font-bold text-gray-900">Issues & Insights Tracker</h1>
						</div>
						<div class="hidden sm:ml-6 sm:flex sm:space-x-8">
							<a
								href="/dashboard"
								class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm"
								class:border-blue-500={$page.route.id === '/dashboard'}
								class:text-blue-600={$page.route.id === '/dashboard'}
							>
								Dashboard
							</a>
							<a
								href="/issues"
								class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm"
								class:border-blue-500={$page.route.id === '/issues'}
								class:text-blue-600={$page.route.id === '/issues'}
							>
								Issues
							</a>
							<a
								href="/issues/new"
								class="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm"
								class:border-blue-500={$page.route.id === '/issues/new'}
								class:text-blue-600={$page.route.id === '/issues/new'}
							>
								New Issue
							</a>
						</div>
					</div>
					<div class="hidden sm:ml-6 sm:flex sm:items-center">
						<div class="ml-3 relative">
							<div class="flex items-center space-x-4">
								<span class="text-sm text-gray-700">
									{$user?.full_name || $user?.email} 
									<span class="text-xs text-gray-500">({$user?.role})</span>
								</span>
								<button
									on:click={handleLogout}
									class="btn btn-secondary text-sm"
								>
									Logout
								</button>
							</div>
						</div>
					</div>
					<div class="sm:hidden flex items-center">
						<button
							on:click={toggleMobileMenu}
							class="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
						>
							<svg class="h-6 w-6" stroke="currentColor" fill="none" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
							</svg>
						</button>
					</div>
				</div>
			</div>

			<!-- Mobile menu -->
			{#if showMobileMenu}
				<div class="sm:hidden">
					<div class="pt-2 pb-3 space-y-1">
						<a href="/dashboard" class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50 hover:border-gray-300">Dashboard</a>
						<a href="/issues" class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50 hover:border-gray-300">Issues</a>
						<a href="/issues/new" class="block pl-3 pr-4 py-2 border-l-4 text-base font-medium border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50 hover:border-gray-300">New Issue</a>
					</div>
					<div class="pt-4 pb-3 border-t border-gray-200">
						<div class="flex items-center px-4">
							<div class="ml-3">
								<div class="text-base font-medium text-gray-800">{$user?.full_name || $user?.email}</div>
								<div class="text-sm font-medium text-gray-500">{$user?.role}</div>
							</div>
						</div>
						<div class="mt-3 space-y-1">
							<button
								on:click={handleLogout}
								class="block px-4 py-2 text-base font-medium text-gray-500 hover:text-gray-800 hover:bg-gray-100 w-full text-left"
							>
								Logout
							</button>
						</div>
					</div>
				</div>
			{/if}
		</nav>
	{/if}

	<!-- Main content -->
	<main class={isLoginPage ? '' : 'max-w-7xl mx-auto py-6 sm:px-6 lg:px-8'}>
		<slot />
	</main>
</div>
