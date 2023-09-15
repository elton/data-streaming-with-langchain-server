import asyncio
from typing import AsyncIterable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    content: str


async def send_message(content: str) -> AsyncIterable[str]:
    callback = AsyncIteratorCallbackHandler()  # 这个callback是用来处理异步的数据流的
    model = ChatOpenAI(
        streaming=True,
        verbose=True,
        callbacks=[callback],
    )

    # 创建一个异步任务。这个异步任务将在后台执行，而不会阻塞主程序。
    task = asyncio.create_task(
        # agenerate是异步生成器，它会在后台执行，而不会阻塞主程序。
        model.agenerate(messages=[[HumanMessage(content=content)]])
    )

    try:
        # 这个循环会在接收到来自模型的响应消息时进行迭代。
        # 异步for循环迭代回调对象的aiter()方法产生的令牌（tokens）
        async for token in callback.aiter():
            # 将每个令牌异步地产生（yield）出来，以便外部可以逐个获取这些令牌。
            yield token
    except Exception as e:
        print(f"Caught exception: {e}")
    finally:
        # 将回调的done属性设置为True，表示回调操作已经完成。
        callback.done.set()

    # 等待异步任务完成。这样做是为了确保在所有操作完成之后才结束函数的执行。
    await task


@app.post("/stream_chat/")
async def stream_chat(message: Message):
    print(message.content)
    generator = send_message(message.content)
    return StreamingResponse(generator, media_type="text/event-stream")
