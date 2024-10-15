import {
	type FC,
	useEffect,
	type ComponentPropsWithoutRef,
	useState,
} from "react";
import type { Snip } from "~lib/types";
import { useContentScriptStore, useSnipsStore } from "~stores/sniptube";
import { useForm, type SubmitHandler } from "react-hook-form";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { atomDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { genTheDiff, getTheDiff } from "~lib/talkToBackend";
import EmptyChat from "./EmptyChat";

interface Props extends ComponentPropsWithoutRef<"div"> {
	currentUrl: string;
}

type ChatMessage = {
	id: string;
	text: string;
	sender: "user" | "ai";
};

type FormInputs = {
	message: string;
};
const Chat: FC<Props> = (props) => {
	const { currentUrl, className } = props;

	const [messages, setMessages] = useState<ChatMessage[]>([]);
	const { register, handleSubmit, reset } = useForm<FormInputs>();

	useEffect(() => {
		const githubUsername = currentUrl.split("/")[3];
		const githubRepoId = currentUrl.split("/")[4];
		if (!githubUsername || !githubRepoId) return;
		getTheDiff(githubUsername, githubRepoId).then((response) => {
			console.log("Response from getTheDiff:", response);
			for (const data of response) {
				const userMessage: ChatMessage = {
					id: data.created_at + data.id,
					text: data.user_message,
					sender: "user",
				};
				const botMessage: ChatMessage = {
					id: data.created_at + data.id,
					text: data.ai_response,
					sender: "ai",
				};
				setMessages((prevMessages) => [
					...prevMessages,
					userMessage,
					botMessage,
				]);
			}
		});
	}, [currentUrl]);

	const sendMessage: SubmitHandler<FormInputs> = async (data) => {
		console.log("Form data:", data);
		if (data.message.trim() === "") return; // Check for empty message

		const newMessage: ChatMessage = {
			id: `${Date.now().toString()}-user`,
			text: data.message,
			sender: "user",
		};
		setMessages((prevMessages) => [...prevMessages, newMessage]);
		reset();

		const response = await genTheDiff(currentUrl, data.message);
		const botMessage: ChatMessage = {
			id: `${Date.now().toString()}-ai`,
			text: response,
			sender: "ai",
		};
		setMessages((prevMessages) => [...prevMessages, botMessage]);
	};

	const renderMessage = (message: ChatMessage) => {
		if (!message.text) return null;
		const parts = message.text.split(/(```[\s\S]*?```)/g);
		return parts.map((part, index) => {
			if (part.startsWith("```") && part.endsWith("```")) {
				const code = part.slice(3, -3).trim();
				const language = code.split("\n")[0];
				const codeContent = code.split("\n").slice(1).join("\n");
				return (
					<SyntaxHighlighter
						key={index}
						language={language || "javascript"}
						style={atomDark}
						className="rounded-md my-2"
					>
						{codeContent}
					</SyntaxHighlighter>
				);
			}
			return (
				<p key={index} className="mb-2">
					{part}
				</p>
			);
		});
	};

	return (
		<main className={`flex flex-col flex-1 ${className}`}>
			{/* <Topbar tags={tags} /> */}
			<div className="flex-1 overflow-y-auto p-4 space-y-4">
				{messages.map((message) => (
					<div
						key={message.id}
						className={`flex ${
							message.sender === "user" ? "justify-end" : "justify-start"
						}`}
					>
						<div
							className={`max-w-xs lg:max-w-md xl:max-w-lg px-4 py-2 rounded-lg ${
								message.sender === "user"
									? "bg-teal-600 text-white"
									: "bg-gray-700 text-gray-100"
							}`}
						>
							{renderMessage(message)}
						</div>
					</div>
				))}
				{messages.length === 0 && <EmptyChat />}
			</div>
			<form
				onSubmit={handleSubmit(sendMessage)}
				className="flex items-center p-4"
			>
				<input
					{...register("message", { required: true })}
					className="flex-1 px-4 py-2 bg-gray-700 text-gray-100 rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500"
					placeholder="Type your message..."
				/>
				<button
					type="submit"
					className="px-4 py-2 bg-teal-600 text-white rounded-r-md hover:bg-teal-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
				>
					Send
				</button>
			</form>
		</main>
	);
};

export default Chat;
