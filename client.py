"""Claude Chat Client integrated with MCP Server using Server-Sent Events (SSE)."""

import asyncio
import json
import os
from typing import List, Dict, Any

import httpx
from mcp import ClientSession
from mcp.client.sse import sse_client
from anthropic import AsyncAnthropic


class MCPClaudeClient:
    """
    A client that integrates MCP tools with Claude's chat API.
    """
    
    def __init__(self, anthropic_api_key: str, mcp_server_url: str = "http://localhost:8000/sse"):
        self.claude_client = AsyncAnthropic(api_key=anthropic_api_key)
        self.mcp_server_url = mcp_server_url
        self.mcp_session = None
        self.available_tools = []
        
    async def __aenter__(self):
        """Async context manager entry."""
        # Establish MCP connection
        self.sse_connection = sse_client(url=self.mcp_server_url)
        self.read, self.write = await self.sse_connection.__aenter__()
        
        # Initialize MCP session
        self.mcp_session = ClientSession(self.read, self.write)
        await self.mcp_session.__aenter__()
        await self.mcp_session.initialize()
        
        # Get available tools
        tools_response = await self.mcp_session.list_tools()
        self.available_tools = tools_response.tools
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.mcp_session:
            await self.mcp_session.__aexit__(exc_type, exc_val, exc_tb)
        if hasattr(self, 'sse_connection'):
            await self.sse_connection.__aexit__(exc_type, exc_val, exc_tb)
    
    def _convert_mcp_tools_to_claude_format(self) -> List[Dict[str, Any]]:
        """
        Convert MCP tools to Claude tool use format.
        """
        claude_tools = []
        
        for tool in self.available_tools:
            # Claude tool structure
            claude_tool = {
                "name": tool.name,
                "description": tool.description or "",
            }
            
            # Convert input schema if available
            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                claude_tool["input_schema"] = tool.inputSchema
            else:
                # Fallback if no schema provided
                claude_tool["input_schema"] = {
                    "type": "object",
                    "properties": {},
                }
            
            claude_tools.append(claude_tool)
        
        return claude_tools
    
    async def _execute_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Execute an MCP tool and return the result.
        """
        try:
            result = await self.mcp_session.call_tool(name=tool_name, arguments=arguments)
            
            # Extract text content from the result
            if result.content and len(result.content) > 0:
                return result.content[0].text
            else:
                return f"Tool {tool_name} executed successfully but returned no content."
                
        except Exception as e:
            return f"Error executing tool {tool_name}: {str(e)}"
    
    async def chat_with_tools(self, messages: List[Dict[str, Any]], 
                            model: str = "claude-3-5-sonnet-20241022",
                            max_tokens: int = 1024) -> str:
        """
        Have a conversation with Claude that can use MCP tools.
        
        Args:
            messages: List of chat messages in Claude format
            model: Claude model to use
            max_tokens: Maximum tokens for response
            
        Returns:
            The assistant's final response
        """
        claude_tools = self._convert_mcp_tools_to_claude_format()
        
        # Separate system message from conversation messages
        system_message = None
        conversation_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                conversation_messages.append(msg)
        
        # Make initial chat completion request
        response = await self.claude_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_message,
            messages=conversation_messages,
            tools=claude_tools if claude_tools else None,
        )
        
        # Handle tool use
        if response.stop_reason == "tool_use":
            # Add Claude's response to conversation
            conversation_messages.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Process tool calls
            tool_results = []
            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_name = content_block.name
                    tool_input = content_block.input
                    tool_id = content_block.id
                    
                    print(f"🔧 Executing tool: {tool_name} with args: {tool_input}")
                    
                    # Execute the MCP tool
                    tool_result = await self._execute_mcp_tool(tool_name, tool_input)
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": tool_result
                    })
            
            # Add tool results to conversation
            conversation_messages.append({
                "role": "user",
                "content": tool_results
            })
            
            # Get final response after tool execution
            final_response = await self.claude_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_message,
                messages=conversation_messages,
            )
            
            # Extract text content from final response
            text_content = ""
            for content_block in final_response.content:
                if content_block.type == "text":
                    text_content += content_block.text
            
            return text_content
        
        else:
            # Extract text content from response
            text_content = ""
            for content_block in response.content:
                if content_block.type == "text":
                    text_content += content_block.text
            
            return text_content


async def main():
    """
    Example usage of the integrated MCP + Claude client.
    """
    # Get API key from environment variable or set directly
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "your-anthropic-api-key-here")
    
    if ANTHROPIC_API_KEY == "your-anthropic-api-key-here":
        print("❌ Please set your Anthropic API key:")
        print("   Option 1: Set environment variable: export ANTHROPIC_API_KEY='your-key'")
        print("   Option 2: Edit the ANTHROPIC_API_KEY variable in this file")
        return
    
    try:
        async with MCPClaudeClient(ANTHROPIC_API_KEY) as client:
            print("🚀 Connected to MCP server and Claude")
            print(f"📚 Available tools: {[tool.name for tool in client.available_tools]}")
            print()
            
            # Example conversation
            messages = [
                {
                    "role": "system", 
                    "content": "You are a helpful assistant that can check weather information for cities. Use the available tools when users ask about weather."
                },
                {
                    "role": "user", 
                    "content": "What's the weather like in Tokyo and New York?"
                }
            ]
            
            print("💬 Starting conversation...")
            response = await client.chat_with_tools(messages, model="claude-3-5-sonnet-20241022")
            
            print("🤖 Claude:", response)
            
            print("\n" + "="*50 + "\n")
            
            # Interactive chat loop
            print("🎯 Interactive chat mode (type 'quit' to exit):")
            conversation_history = [
                {
                    "role": "system", 
                    "content": "You are a helpful assistant that can check weather information for cities. Use the available tools when users ask about weather."
                }
            ]
            
            while True:
                user_input = input("\n👤 You: ")
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    break
                
                conversation_history.append({"role": "user", "content": user_input})
                
                try:
                    response = await client.chat_with_tools(conversation_history, model="claude-3-5-sonnet-20241022")
                    print(f"🤖 Claude: {response}")
                    
                    # Add Claude's response to conversation history
                    conversation_history.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    print(f"❌ Error: {e}")
    
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        print("Make sure your MCP server is running on http://localhost:8000")


# Alternative: Simple function-based approach
async def simple_claude_mcp_chat(user_message: str, anthropic_api_key: str) -> str:
    """
    Simple function to ask a question that might use MCP tools.
    
    Args:
        user_message: The user's question
        anthropic_api_key: Your Anthropic API key
        
    Returns:
        Claude's response
    """
    async with MCPClaudeClient(anthropic_api_key) as client:
        messages = [
            {"role": "user", "content": user_message}
        ]
        return await client.chat_with_tools(messages)


# Example usage with environment variable
async def quick_example():
    """Quick example that uses environment variable for API key."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Set ANTHROPIC_API_KEY environment variable")
        return
    
    response = await simple_claude_mcp_chat(
        "What's the weather in London?", 
        api_key
    )
    print(f"Claude: {response}")


if __name__ == "__main__":
    asyncio.run(main())
