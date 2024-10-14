import { useEffect, type FC, useState } from "react";
import "src/styles/tailwind.css";
import { useAllSnipsStore, useContentScriptStore } from "~stores/sniptube";
import type { Tag, Snip } from "~lib/types";
import "webextension-polyfill-global";
import Chat from "./components/Chat";
interface Props {}

const Popup: FC<Props> = () => {
	// const [count, setCount] = useState<number>(0);
	// useEffect(() => {
	//   chrome.action.setBadgeText({ text: count.toString() });
	// }, [count]);
	const inGithubRepo = useContentScriptStore((state) => state.inGithubRepo);
	const [currentUrl, setCurrentUrl] = useState<string>("");

	const setInGithubRepo = useContentScriptStore(
		(state) => state.setInGithubRepo,
	);
	const allSnips = useAllSnipsStore((state) => state.snips);
	// const tags = useMemo<Set<Tag>>(() => {
	// 	return allSnips.reduce((acc: Set<Tag>, snip: Snip) => {
	// 		snip.tags?.forEach((tag: Tag) => {
	// 			acc.add(tag);
	// 		});
	// 		return acc;
	// 	}, new Set<Tag>());
	// }, [allSnips]);
	useEffect(() => {
		// get the current video id
		browser.tabs.query({ active: true, currentWindow: true }).then((tabs) => {
			const tab = tabs[0];
			const url = tab.url ?? "";
			setCurrentUrl(url);
			setInGithubRepo(url.includes("github.com"));

			// temporary fix for dark mode (add a class to the html tag)
			if (!document.documentElement.classList.contains("dark")) {
				document.documentElement.classList.add("dark");
			}
		});
	}, [setInGithubRepo]);

	// const changeBackground = () => {
	//   chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
	//     const tab = tabs[0];
	//     if (tab.id) {
	//       chrome.tabs.sendMessage(
	//         tab.id,
	//         {
	//           color: "#555555",
	//         },
	//         (msg) => {
	//           console.log("result message:", msg);
	//         }
	//       );
	//     }
	//   });
	// };

	return (
		<div className="w-[30rem] flex flex-col min-h-[30rem] dark:bg-gray-950 dark:text-white">
			{inGithubRepo ? (
				<Chat currentUrl={currentUrl} />
			) : (
				<div>not in github</div>
			)}
			<footer className="flex justify-center w-full mb-2 text-sm text-gray-500 dark:text-gray-400 gap-x-1">
				Made with ❤️ by
				<a
					href="https://rami-maalouf.tech"
					target="_blank"
					rel="noopener noreferrer"
					className="font-semibold text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100"
				>
					Rami Maalouf
				</a>
			</footer>
		</div>
	);
};

export default Popup;
