import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers import JsonOutputParser


from db import insert_to_supabase
from github import GithubFileLoader

from dotenv import load_dotenv
import os
from typing import List, Union, Dict

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class TinyGen:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="gpt-4o",
            max_tokens=4096,
            temperature=0,
            streaming=True,
            verbose=True,
            openai_api_key=OPENAI_API_KEY,
        )

    async def call(self, repo_url, prompt):
        loader = GithubFileLoader(repo_url)

        print("Loading files from the repository...\n")
        files = loader.load()
        print("Files loaded successfully!\n\n")
        self.repo_files = []
        for file in files:
            self.repo_files.append(file)
        print("Files loaded successfully!\n\n")
        self.prompt = prompt

        # Summarize files
        print(
            f"Summarizing files...\nMaking a batch call to summarize file chain for {len(self.repo_files)} files...\n"
        )
        self.repo_files_with_summaries = self.summarize_files(self.repo_files)
        print("Done summarizing all files!\n\n")

        # Initialize rest of the chains
        tinygen_chain = self.initialize_and_combine_chains(self.repo_files, self.prompt)

        diff = tinygen_chain.invoke(
            {
                "files_list": self.repo_files_with_summaries,
                "user_query": self.prompt,
            }
        )

        # Insert Data to Supabase after processing is finished
        insert_to_supabase(prompt, loader.username, loader.repo_id, diff)

        return diff

    async def stream(self, repo_url, prompt):

        loader = GithubFileLoader(repo_url)

        print("Loading files from the repository...\n")
        files = loader.load()
        print("Files loaded successfully!\n\n")
        self.repo_files = []
        for file in files:
            self.repo_files.append(file)
        print("Files loaded successfully!\n\n")
        self.prompt = prompt

        # summarize files
        self.repo_files_with_summaries = self.summarize_files(self.repo_files)
        print("Done summarizing all files!\n\n")

        # Initialize rest of the chains
        # Four Chains: identify relevant files -> modify code -> generate diff -> reflection on diff)
        tinygen_chain = self.initialize_and_combine_chains(self.repo_files, self.prompt)

        response = tinygen_chain.astream_events(
            {"files_list": self.repo_files_with_summaries, "user_query": self.prompt},
            version="v1",
            include_types=["chat_model"],
        )

        generated_text = ""

        async for event in self.retry_operation(response):
            kind = event["event"]
            chain = event["name"]

            if kind == "on_chat_model_stream" and chain == "reflection_chain":
                chunk_content = str(event["data"]["chunk"].content)
                generated_text += chunk_content  # Accumulate the generated text
                yield chunk_content  # Yield the chunk to the client
            elif (
                kind == "on_chat_model_start"
                and chain == "identify_relevant_files_chain"
            ):
                print("##### Starting Identify Relevant Files Chain...\n\n")
            elif kind == "on_chat_model_start" and chain == "code_conversion_chain":
                print("##### Starting Code Conversion Chain...\n\n")
            elif kind == "on_chat_model_start" and chain == "generate_diff_chain":
                print("\n\n##### Starting Generate Diff Chain...\n\n")
            elif kind == "on_chat_model_start" and chain == "reflection_chain":
                print("\n\n##### Starting Reflection Chain...\n\n")

        # Insert Data to supabase after all streaming is finished!

        response = insert_to_supabase(
            prompt, loader.username, loader.repo_id, generated_text
        )

    async def retry_operation(self, operation, retries=3, delay=1):
        for attempt in range(retries):
            try:
                # Check if the operation is an async generator
                if hasattr(operation, "__aiter__"):
                    # If it's an async generator, return the async generator itself
                    async for result in operation:
                        yield result  # Yield each result from the async generator
                else:
                    # Otherwise, await the operation
                    yield await operation
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(delay)  # Wait before retrying
                else:
                    print("All attempts failed.")
                    raise  # Re-raise the last exception

    def summarize_files(self, repo_files):
        ############
        # 1. Summary Chain: summarize all files
        ############
        summarize_prompt = PromptTemplate.from_template(
            """
            Here is the given contents from a file:
            <contents>
            {contents}
            </contnets>

            Here is the given file path for this file:
            <file_path>
            {file_path}
            </file_path>

            Generate me a concise summary of the purpose of this file in the context of the project.
            It must be very clear so that even developers who just moved to this project can understand this file by analyzing the generated summary
            without additional questions.
            """
        )
        summary_chain = (
            summarize_prompt | self.llm | StrOutputParser()
        )  # CURRENTLY USING GPT-4-Turbo for summaries! (Reason: 400K Tokens Per Minute allowed)

        summarize_files = summary_chain.map() | self.transform_summary_chain_output

        return summarize_files.invoke(repo_files)

    def transform_summary_chain_output(self, summaries):
        files_with_summaries = []
        for i, summary in enumerate(summaries):
            file_and_summary = {
                "file_path": self.repo_files[i]["file_path"],
                "file_summary": summary,
            }
            files_with_summaries.append(file_and_summary)

        return files_with_summaries

    def transform_relevant_files_chain_output(
        self, relevant_file_paths: dict[str, List]
    ):
        relevant_files = get_file(relevant_file_paths["files"], self.repo_files)
        return relevant_files

    def transform_conversion_chain_output(self, code_changes: List[Dict]):
        original_files = []

        print("code changes: ", code_changes)

        for code_change in code_changes:
            original_file_path = code_change["original_file_path"]
            original_file = get_file(original_file_path, self.repo_files)
            original_files.append(
                {"file_path": original_file_path, "contents": original_file}
            )

        return {"original_files": original_files, "changed_files": code_changes}

    def initialize_and_combine_chains(self, repo_url, prompt):
        ############
        # 2. Identify Relevant Files Chain: given a summary of each file, identify relevant files to the user prompt
        ############
        identify_relevant_files_prompt = PromptTemplate.from_template(
            """
            You're a senior software developer implementing changes in files the project.
            Based on the provided instructions, all file paths, and summary of each file, identify the file
            that needs to be modified to solve the user's issue or request.

            <files_list>
            {files_list}
            </files_list>

            <user_query>
            {user_query}
            </user_query>

            There may be just a single file OR there maybe multiple files. You decide which files you think are relevant. If there are multiple files, 
            make sure each path is in a new line. think carefully and output all relevant files!

            Output *ONLY* the file path(s), relative to project root, as a list
            without any comments or explanation, like this:

            ```json
            {{"files": [path/to/file, path/to/file]}}
            ```
            
            Use double quotes for all strings and escape any double quotes within the string with a backslash. Before submitting, ensure the json is valid!
            """
        )

        identify_relevant_files_chain = (
            identify_relevant_files_prompt
            | self.llm.with_config({"run_name": "identify_relevant_files_chain"})
            | JsonOutputParser()
        )
        ############
        # 3. Code Conversion Chain: Given all of the files, generate the code that would fix the user's issue in the file
        ############
        code_conversion_prompt = PromptTemplate.from_template(
            """
            You are an expert at solving user issues in the code base. Given a user query defined under <user_query></user_query>,
            You are given the relevant files needed to solve the user's issue that he/she is having for the given repository
            These are the relevant files given to you under <relevant_files></relevant_files>

            <relevant_files>
            {relevant_files}
            </relevant_files>

            Given these files, do the following step by step:
                1. Identify what changes need to be made in the files
                2. update the code so that the user's issue is solved
            
            <user_query>
            {user_query}
            </user_query>

            Return the name of the file(s) that was updated,
            and also the updated file in a json list format like this:
            [
                    {{
                        "original_file_path": <path of original file>,
                        "new_file_path": <path of the new file>,
                        "updated_contents": <new_file_contents>,
                        "what_changed": <simple description of what was added>
                    }},
                    {{
                        "original_file_path": <path of original file>,
                        "new_file_path": <path of the new file>,
                        "updated_contents": <new_file_contents>,
                        "what_changed": <simple description of what was added>
                    }}
            ]

            Important: Return only the json and no other text! Make sure to escape any string literals so that the json is valid!
            For all strings, use double quotes and escape any double quotes within the string with a backslash. Before submitting, ensure the json is valid!
            """
        )

        code_conversion_chain = (
            code_conversion_prompt
            | self.llm.with_config({"run_name": "code_conversion_chain"})
            | JsonOutputParser()
        )

        ############
        # 4. Generate Diff: Given the changed file and the original file, generate the unified diff
        ############
        generate_diff_prompt = PromptTemplate.from_template(
            """
            You are an expert at generating diffs given the original files and the modified files. You are given the original file paths and content.
            You are also given the changed files and possible reason for the changes. There may be just one file that was modified or more than one.

            Generate the unified diff for the changes that were made!

            Return only the diff and nothing else

            <original_files>
            {original_files}
            </original_files>

            <changed_file>
            {changed_files}
            </changed_file>
            """
        )
        generate_diff_chain = (
            generate_diff_prompt
            | self.llm.with_config({"run_name": "generate_diff_chain"})
            | StrOutputParser()
        )

        ############
        # 5. Reflection Chain: Given the generated diff, user query, original file and changed file, check to see if the diff is correct. Return the diff if correct, or regenerate it again
        ############
        reflection_prompt = PromptTemplate.from_template(
            """
            You are given a diff please check to make sure that the diff is correct!
            Ensure that it's compilable and also solves the user's query. If its correct,
            then don't change it and return the diff and only the diff.
            If it's incorrect, then generate a new diff based on the changed files.

            Return only the diff! If it was correct, then just return the original diff and nothing else. if it was incorrect,
            then return the new diff and nothing else!
            
            <original_files>
            {original_files}
            </original_file>

            <changed_file>
            {changed_files}
            </changed_files>

            <diff>
            {diff}
            </diff>

            <user_query>
            {user_query}
            </user_query>
            """
        )
        reflection_chain = (
            reflection_prompt
            | self.llm.with_config({"run_name": "reflection_chain"})
            | StrOutputParser()
        )

        identify_relevant_files = (
            identify_relevant_files_chain
            | (
                lambda x: print("Relevant files before transformation:", x) or x
            )  # Print before transformation
            | self.transform_relevant_files_chain_output
        )

        convert_code = code_conversion_chain | self.transform_conversion_chain_output

        final_chain = (
            RunnablePassthrough.assign(relevant_files=identify_relevant_files)
            .pick(["user_query", "relevant_files"])
            .pipe(convert_code)
            .assign(user_query=lambda x: prompt, diff=generate_diff_chain)
            .pick(["user_query", "diff", "original_files", "changed_files"])
            .pipe(reflection_chain)
        )

        return final_chain


system_prompt = """
**Background:**
- As a programming maestro, you possess a broad spectrum of coding abilities, ready to tackle diverse programming challenges.
- Your areas of expertise include project design, efficient code structuring with precision and clarity.
"""


def get_file(file_paths: Union[List[str], str], repo_files: List[Dict[str, str]]):
    """
    Get the contents of multiple files given their relative file paths from a list of repository files.

    Args:
    - file_paths (Union[List[str], str]): List of relative paths to the files or a single file path as a string.
    - repo_files (List[Dict[str, str]]): List of dictionaries with 'file_path' and 'contents' keys representing files in a repository.

    Returns:
    - List[Dict[str, str]]: A list of dictionaries, each containing the file path and its contents.
    """

    if isinstance(file_paths, str):
        file_paths = [file_paths]

    file_contents = []

    for file_path in file_paths:
        # Search for the file_path in repo_files
        matched_files = [f for f in repo_files if f["file_path"] == file_path]
        if matched_files:
            # Assuming only one match should be found, take the first one.
            print(f"{file_path} found!")
            file_contents.append(matched_files[0])
        else:
            # If the file isn't found, append an entry with an empty contents.
            file_contents.append(
                {"file_path": file_path, "contents": "This file was not found"}
            )
            print(f"Warning! The file {file_path} was not found in the repository.")

    return file_contents
