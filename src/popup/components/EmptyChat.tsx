import { type FC } from "react";

interface Props {}

const EnptyChat: FC<Props> = (props) => {
	const {} = props;

	return (
		<main className="flex flex-col items-center justify-center my-auto">
			<h1 className="text-2xl font-semibold">Start a conversation!</h1>
			<p className="text-lg text-center">
				Let me know how I can help you with this repository today.
			</p>
		</main>
	);
};

export default EnptyChat;
