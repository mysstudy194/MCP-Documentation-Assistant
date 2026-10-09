import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters
from dotenv import load_dotenv

from utils import get_response_from_llm

load_dotenv()

server_params = StdioServerParameters(
    command="uv",
    args=["run", "mcp_server.py"],
    env=None,
)


async def main():
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:

            await session.initialize()

            tools_response = await session.list_tools()
            print("Available tools:", [t.name for t in tools_response.tools])

            query = "Publish a package on GitLab using uv"
            library = "uv"

            res = await session.call_tool(
                "get_docs",
                arguments={
                    "query": query,
                    "library": library,
                },
            )

            # Convert MCP response into plain text
            context = "\n".join(
                item.text
                for item in res.content
                if hasattr(item, "text")
            )

            print("\n========== CONTEXT ==========\n")
            print(context[:3000])



            SYSTEM_PROMPT = """
You are a documentation assistant.

Answer ONLY using the provided documentation.

If the answer cannot be found in the documentation, reply exactly:

I don't know based on the provided documentation.

Keep every SOURCE: line exactly as it appears.
List all SOURCE lines at the end.
"""

            user_prompt = f"""
Question:
{query}

Documentation:

{context}
"""

            answer = get_response_from_llm(
                user_prompt=user_prompt,
                system_prompt=SYSTEM_PROMPT,
                model="openai/gpt-oss-20b",
            )

            print("\nANSWER:\n")
            print(answer)


if __name__ == "__main__":
    asyncio.run(main())