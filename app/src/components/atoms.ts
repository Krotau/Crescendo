import { atom } from 'jotai'


export interface chatLogItem {
    question: string,
    ready: boolean,
    answer: string,
    reasoning: string,
}

export const currentChatAtom = atom<chatLogItem>({
    question: '',
    ready: false,
    answer: '',
    reasoning: '',
})

export const textAtom = atom<string>('')

export const healthAtom = atom<boolean>(false)

export const chatLogAtom = atom<chatLogItem[]>([])

export const contextSizeAtom = atom<number>(0)
