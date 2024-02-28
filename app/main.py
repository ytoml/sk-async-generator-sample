import logging
import uuid

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from semantic_kernel import Kernel, openai_settings_from_dot_env
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

from llm_lib.plugin import AlwaysRunPlugin
from llm_lib.service import AsyncStreamService, service_main

logging.basicConfig(level=logging.DEBUG)

api_key, _ = openai_settings_from_dot_env()
app = FastAPI()
kernel = Kernel()
kernel.add_chat_service(
    service_id="chat",
    service=OpenAIChatCompletion(ai_model_id="gpt-3.5-turbo", api_key=api_key),
)
kernel.import_plugin(AlwaysRunPlugin(kernel), "always_run")
service = AsyncStreamService(kernel, service_main)


@app.get("/")
async def chat_stream():
    connection_id = str(uuid.uuid4())
    receiver = service.run_on_prompt(connection_id, "Achieve the goal.")
    return StreamingResponse(content=receiver, media_type="text/plain")
