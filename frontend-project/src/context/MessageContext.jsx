import { createContext, useContext, useState } from "react";
import { djangoAPI } from "../api/axios.jsx";

const MessageContext = createContext()

export const useMessage = () => useContext(MessageContext);

export const MessageProvider = ({ children }) => {

    const [messageTemplate, setMesssageTemplate] = useState([])
    const [messageAsesor, setMessageAsesor] = useState([])

    const getMessages = async () => {
        try {
            const response = await djangoAPI.get("messages/messages-templates")
            const responseTwo = await djangoAPI.get("/messages/messages-ai/")
            setMesssageTemplate(response.data)
            setMessageAsesor(responseTwo.data)
        } catch (error) {
            console.error("Hay un error mi bro")
        }
    }

    return(
       <MessageContext.Provider value={{ getMessages, messageTemplate, messageAsesor}}>
            {children}
       </MessageContext.Provider >
    )
}