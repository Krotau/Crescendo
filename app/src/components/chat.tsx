import { useAtom, useSetAtom } from 'jotai';
import { z } from 'zod/v4';

import { textAtom, healthAtom, currentChatAtom, chatLogItem, chatLogAtom, contextSizeAtom, fileMenuAtom } from './atoms';
import { useMemo, useState } from 'react';


interface serverChatResponse {
    msg: string,
    done: boolean,
    context_size: number,
}


const serverChatResponseSchema = z.object({
    msg: z.string(),
    done: z.boolean(),
    context_size: z.number(),
})


interface serverToolInit {
    tool_name: string,
    tool_arguments: {},
}


const serverToolInitSchema = z.object({
    tool_name: z.string(),
    tool_arguments: z.object(),
})


interface serverResponse {
    kind: 'tool_init' | 'tool_result' | 'message',
    payload: any
}


// type ServerPayloads = typeof serverToolInitSchema | typeof serverResponseSchema


const serverResponseSchema = z.object({
    kind: z.literal(["tool_init", "tool_result", "message"]),
    payload: z.object()
})


const Chat = () => {

    const [text, setText] = useAtom(textAtom);

    const [health, setHealth] = useAtom(healthAtom);

    const [chats, setChats] = useState(0);

    const [reasoning, setReasoning] = useState(false);

    const [chatLog, setChatLog] = useAtom(chatLogAtom);

    const [currentChat, setCurrentChat] = useAtom(currentChatAtom);

    let [open, setOpen] = useAtom(fileMenuAtom);

    const setContextSize = useSetAtom(contextSizeAtom);

    const chatSocket = useMemo(() => {return new WebSocket('ws://localhost:8000/ws')}, []);


    const sendMessage = () => {
        console.log("Sending message to api");

        if (chats > 0) {
            setChatLog([...chatLog, currentChat])
        }

        chatSocket.send(text);

        setCurrentChat({
            question: text,
            ready: false,
            answer: '',
            reasoning: '',
        });

        setText('');
        setChats(chats + 1);
    }


    const updateCurrentChat = (data: serverChatResponse) => {
        let new_ready = data.done
        
        if (data.msg == '<think>') {
            console.log("thinking...")
            setReasoning(true)
            return
        }

        if (data.msg == '</think>') {
            console.log("done thinking!")
            setReasoning(false)
            return
        }

        let newChatInfo: chatLogItem
        if (reasoning) {
            let new_msg = currentChat.reasoning.concat(data.msg)
            newChatInfo = {
                ...currentChat,
                reasoning: new_msg,
                ready: new_ready,
            }
            setCurrentChat(newChatInfo)
        } else {
            let new_msg = currentChat.answer.concat(data.msg)
            newChatInfo = {
                ...currentChat,
                answer: new_msg,
                ready: new_ready,
            }
            setCurrentChat(newChatInfo)
        }

    }


    chatSocket.onopen = () => {
        setHealth(true)
    }


    chatSocket.onmessage = (event: MessageEvent<string>) => {
        let raw_data = JSON.parse(event.data)

        let data: serverResponse = serverResponseSchema.parse(raw_data)

        if (data.kind === 'message') {
            const payload: serverChatResponse = serverChatResponseSchema.parse(raw_data.payload)

            setContextSize(payload.context_size)

            updateCurrentChat(payload)

        } else {
            console.log(raw_data)
        }

    }


    return(
        <>

        { health ? ":)" : ":("}

        <p>Ask something...</p>

        <input 
            type="text" 
            id="messageText" 
            autoComplete="off"
            value={text}
            onChange={e => setText(e.target.value)}
            onKeyDown={(e) => {
                if (e.key === 'Enter') {
                    sendMessage()
                }
            }}
        />

        <div className="chat_buttons">
            <button onClick={() => sendMessage()}>Send</button>
            <button>Clear Context</button>
            <button onClick={() => {setOpen(!open)}}>File Menu</button>
        </div>

        </>
    )
}

export default Chat;