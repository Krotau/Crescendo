import { useAtomValue } from "jotai"
import { contextSizeAtom } from "./atoms"

function percentage(partialValue: number, totalValue: number) {
   return Math.round((100 * partialValue) / totalValue);
} 

const Context = () => {

    const MAX_SIZE = 40000

    const contextSize = useAtomValue(contextSizeAtom)

    let p = percentage(contextSize, MAX_SIZE)

    const p_str_width = () => {
        return {width: `${p.toFixed(2)}%`}
    }

    return (
        <>
        <div className="serverinfo_context_container">
            <p>Context Used: {p}%</p>
            <div className="context_container">
                <div style={p_str_width()} className="context_bar"><p></p></div>
            </div>
        </div>       
        </>

    )
}

export default Context