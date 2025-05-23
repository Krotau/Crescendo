import { useAtomValue } from "jotai"
import { contextSizeAtom } from "./atoms"

const Context = () => {

    const contextSize = useAtomValue(contextSizeAtom)

    return (
        <div className="context_bar"> Context Used: {contextSize}</div>
    )
}

export default Context