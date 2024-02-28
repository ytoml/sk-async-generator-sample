import asyncio
import functools
from contextlib import asynccontextmanager
from typing import Any, AsyncContextManager, Callable, Coroutine

from semantic_kernel import Kernel
from semantic_kernel.planning import ActionPlanner


async def service_main(
    planner: ActionPlanner, prompt: str, logger: AsyncContextManager
) -> str:
    plan = await planner.create_plan(goal=prompt)
    context = planner._kernel.create_new_context()
    context["log_manager"] = logger

    result_context = await plan.invoke(prompt, context=context)
    return result_context["input"]


MainFunctionOnPrompt = Callable[
    [Kernel, str, AsyncContextManager], Coroutine[Any, Any, str]
]
StrQueue = asyncio.Queue[str]


class AsyncStreamService:
    def __init__(
        self, kernel: Kernel, main_function_on_prompt: MainFunctionOnPrompt
    ):
        self.kernel = kernel
        self.planner = ActionPlanner(kernel)
        self.main = main_function_on_prompt
        self.queues: dict[str, StrQueue] = {}

    def _register(self, exec_id: str):
        queue: StrQueue = asyncio.Queue()
        if exec_id in self.queues:
            raise ValueError(f"Execution ID '{exec_id}' is already running")
        self.queues[exec_id] = queue

        async def stream():
            while exec_id in self.queues:  # False after 'run_on_prompt' ends.
                msg = await queue.get()
                yield msg
                queue.task_done()

        return stream()

    def put_safe(self, exec_id: str, text: str):
        queue = self.queues.get(exec_id)
        if queue:
            queue.put_nowait(text)

    @asynccontextmanager
    async def log(self, exec_id: str, text: str, end: str = "\n"):
        async def log_background():
            for char in text:
                while exec_id in self.queues:
                    try:
                        self.put_safe(exec_id, char)
                        await asyncio.sleep(0.01)
                        break
                    except asyncio.QueueFull:
                        await asyncio.sleep(0.1)
                    except KeyError:
                        raise ValueError(
                            f"Execution ID '{exec_id}' does not exist"
                        )
            self.put_safe(exec_id, end)

        task = asyncio.create_task(log_background())
        try:
            yield
        finally:
            task.result()

    def run_on_prompt(self, exec_id: str, prompt: str):
        async def main():
            log_func = functools.partial(self.log, exec_id)
            result = await self.main(self.planner, prompt, log_func)  # type: ignore
            queue = self.queues.pop(exec_id)
            await queue.put(result)

        receiver = self._register(exec_id)
        _ = asyncio.create_task(main())
        return receiver
