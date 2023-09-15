from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

# 默认是用GPT3.5的模型
chat = ChatOpenAI(
    streaming=True, callbacks=[StreamingStdOutCallbackHandler()], temperature=0
)
print(chat([HumanMessage(content="给我的金毛寻回猎犬起一个好听的名字。")]))
