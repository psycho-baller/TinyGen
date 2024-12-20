import { URL } from "./constants";

type DiffAPIResponse = {
	diff: string;
};
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
		const data = (await res.json()) as DiffAPIResponse;
		const result = data.diff;
		// Handle streaming response
		// const reader = res.body?.getReader();
		// const decoder = new TextDecoder("utf-8");
		// let result = "";

		// if (reader) {
		// 	while (true) {
		// 		const { done, value } = await reader.read();
		// 		if (done) break;
		// 		result += decoder.decode(value, { stream: true });
		// 		// Process the streamed data as needed
		// 		console.log(result);
		// 	}
		// }
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

export const getTheDiff = async (
	githubUsername: string,
	githubRepoId: string,
) => {
	try {
		const res = await fetch(
			`${URL}/diff?github_username=${githubUsername}&github_repo_id=${githubRepoId}`,
			{
				method: "GET",
			},
		);
		if (!res.ok) {
			throw new Error(`${res.status}`);
		}
		const data = (await res.json()) as { data: SupabaseData[] };
		console.log("Data from getTheDiff:", data);
		return data.data;
	} catch (e) {
		console.log("error", e);
		return null;
	}
};
