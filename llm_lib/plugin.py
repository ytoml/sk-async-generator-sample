import asyncio

from semantic_kernel import Kernel, KernelContext
from semantic_kernel.plugin_definition import kernel_function


class AlwaysRunPlugin:
    def __init__(self, kernel: Kernel):
        self.kernel = kernel
        self.queue_manager: dict[str, asyncio.Queue] = {}

    @kernel_function(
        name="always_run",
        description="Function that must be always chosen whatever the goal is. In every plan, this function will be the first step (it's ok to execute this step only).",
    )
    async def run(self, context: KernelContext) -> str:
        log = context["log_manager"]
        async with log("This is a response to User."):
            for char in "I'm always present in the server log!":
                print(char, end="", flush=True)
                await asyncio.sleep(0.03)
        print(flush=True)

        return "Done."
