## Simplest MCP SSE server
The simplest MCP server/client, chat and ask about the weather in *** city, *** is always sunny.

## to run:

```bash
#1. Install dependencies Using uv (recommended)
uv sync

#2. Export environment variable
export ANTHROPIC_API_KEY="your-actual-api-key-here"

#3. Start the MCP server
uv run uvicorn server:app --host 0.0.0.0 --port 8000 --reload

#4. Start the Chat in another terminal
uv run chat
```
## Example output:
🚀 Connected to MCP server and Claude
📚 Available tools: ['get_weather']

💬 Starting conversation...
🔧 Executing tool: get_weather with args: {'city': 'Tokyo'}
🤖 Claude: 

==================================================

🎯 Interactive chat mode (type 'quit' to exit):

👤 You: what is the weather in Aruba
🔧 Executing tool: get_weather with args: {'city': 'Aruba'}
🤖 Claude: According to the weather information, it is currently sunny in Aruba. This is typical for Aruba, as it's known for its consistently warm and sunny weather, making it a popular Caribbean destination.

👤 You: what is the weather in Bolivia
🔧 Executing tool: get_weather with args: {'city': 'Bolivia'}
🤖 Claude: According to the current weather data, it is sunny in Bolivia. However, please note that Bolivia is a large country with varying elevations and climate zones, so the weather can differ significantly depending on the specific region or city you're interested in. If you'd like more specific information, you could let me know which city in Bolivia you're curious about.

👤 You: How is the weather in Finland
🔧 Executing tool: get_weather with args: {'city': 'Helsinki'}
🤖 Claude: According to the current weather data, it is sunny in Helsinki, Finland. However, please note that Finland is a relatively large country, and weather conditions can vary depending on the specific region you're interested in. Also, Finland experiences significant seasonal changes throughout the year due to its northern location. If you're interested in a specific city or region in Finland, feel free to ask!

👤 You: What is the weather in Africa
🤖 Claude: I notice you're asking about the weather in Africa, but Africa is actually a continent that contains 54 different countries with vastly different climate zones - from the Sahara Desert in the north to tropical rainforests in the center to more temperate regions in the south. 

To give you accurate weather information, I'll need you to specify a particular city or at least a specific country in Africa. For example, you could ask about:
- Cairo, Egypt
- Nairobi, Kenya
- Cape Town, South Africa
- Lagos, Nigeria

Which specific location in Africa would you like to know the weather for?

👤 You: Lagos
🔧 Executing tool: get_weather with args: {'city': 'Lagos'}
🤖 Claude: According to the current weather data, it is sunny in Lagos, Nigeria. This is quite typical for Lagos, as it has a tropical climate with generally warm temperatures year-round. Lagos typically experiences two rainy seasons (April to July and October to November) and two dry seasons (December to March and August to September).

👤 You: bye

