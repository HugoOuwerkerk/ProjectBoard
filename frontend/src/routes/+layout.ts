import type { LayoutLoad } from './$types';

export const ssr = false;

export const load: LayoutLoad = async ({ fetch, depends }) => {
	depends('auth:session');

	try {
		const res = await fetch('/api/me');
		if (res.ok) {
			const user = await res.json();
			return { user };
		}
	} catch (error) {
		console.error('Failed to resolve /api/me', error);
	}

	return { user: null };
};
