import { URL } from "./constants";

export const genTheDiff = async (repoUrl: string, prompt: string) => {
	try {
		const res = await fetch(`${URL}/diff`, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({ repoUrl, prompt }),
		});
		if (!res.ok) {
			throw new Error(`${res.status}`);
		}
		// const data = (await res.json()) as DiffAPIResponse;
		// Handle streaming response
		const reader = res.body?.getReader();
		const decoder = new TextDecoder("utf-8");
		let result = "";

		if (reader) {
			while (true) {
				const { done, value } = await reader.read();
				if (done) break;
				result += decoder.decode(value, { stream: true });
				// Process the streamed data as needed
				console.log(result); // You can update your UI or state here
			}
		}
		// localStorage.setItem(videoId, JSON.stringify(data));
		return result;
	} catch (e) {
		console.log("error", e);
		return null;
	}
};

type SupabaseData = {
	id: number;
	user_message: string;
	github_username: string;
	github_repo_id: string;
	ai_response: string;
	created_at: string;
};

export const getTheDiff = async (repoUrl: string) => {
	try {
		const res = await fetch(`${URL}/diff`, {
			method: "GET",
		});
		if (!res.ok) {
			throw new Error(`${res.status}`);
		}
		const data = (await res.json()) as { data: SupabaseData[] };
		return data.data;
	} catch (e) {
		console.log("error", e);
		return null;
	}
};
