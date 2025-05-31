import React, { useEffect } from "react";
import { useMessage } from "../context/MessageContext.jsx";
import { TrashIcon } from "../icons/index.jsx";
import { EditAltIcon } from "../icons/index.jsx";
import toast from "react-hot-toast";
import { djangoAPI } from "../api/axios.jsx";

export const MessageTemplate = () => {

    const { getMessages, messageTemplate } = useMessage()

    const confirmDelete = (id) => {
        if (window.confirm("¿Estas seguro de eliminar este mensaje?")) {
            deleteMessage(id)
        }
    }

    const deleteMessage = async(id) => {
        try {
            const response = await djangoAPI.delete(`messages/messages-templates/${id}/`)

            getMessages()
            toast.success("Mensaje eliminado")
        } catch (error) {
            console.log(error)
            toast.error("Error al eliminar el mensaje")
        }
    }

    useEffect(() => {
        getMessages()
    },[])

    return(
        <div>
            {messageTemplate.map((message) => (
                <div key={message.id} className="bg-white m-3 p-3 max-w-auto rounded relative">
                    <h2 className="text-[#1F3361] font-bold border-b border-dashed"> {message.title} </h2>
                    <p className="p-2"> {message.description}</p>
                    <aside className="flex absolute bottom-0 right-0" >
                        <EditAltIcon className="text-2xl m-2 cursor-pointer" />    
                        <TrashIcon className="text-2xl m-2 hover:text-red-500 cursor-pointer" onClick={() => confirmDelete(message.id)} />
                    </aside>
                </div>
            ))}
        </div> 
    )

}
 