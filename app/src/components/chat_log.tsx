import { useAtomValue } from "jotai"
import { chatLogAtom, currentChatAtom } from "./atoms"

const ChatLog = () => {

    const chatLog = useAtomValue(chatLogAtom)

    const currentChat = useAtomValue(currentChatAtom)

    return (
        <div className="chat_log">

            <div className="chat_item">

                <div className="chat_container">
                    <div className="question">{currentChat.question}</div>
                </div>
                <div className="answer">{currentChat.answer}</div>
                <div className="reasoning">{currentChat.reasoning}</div>
                <div>
                    <button>Play</button>
                    <button>Expand</button>
                </div>

                <p>Chat Log</p>

                {
                    chatLog.map((logItem) => {
                        return (
                            <>
                            <div className="chat_container margin_top">
                                <div className="question">{logItem.question}</div>
                            </div>
                            <div className="answer">{logItem.answer}</div>
                            <div>
                                <button>Play</button>
                                <button>Expand</button>
                            </div>
                            </>
                        )
                    })
                }
            </div>
        </div>
    )
}

export default ChatLog