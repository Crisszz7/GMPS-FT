import React, { useEffect, useState } from "react";
import { useMessage } from "../context/MessageContext.jsx";
import { TrashIcon } from "../icons/index.jsx";
import { EditAltIcon } from "../icons/index.jsx";
import toast from "react-hot-toast";
import { djangoAPI } from "../api/axios.jsx";
import {DndContext, useDraggable, useDroppable} from "@dnd-kit/core"

export const MessageTemplate = () => {

    const { getMessages, messageTemplate } = useMessage()

    const [selectedMessage, setSelectedMessage] = useState(null)
    const [newTitle, setNewTitle] = useState("")
    const [newDescription, setNewDescription] = useState("")

    const startEditMessage = (message) => {
        setSelectedMessage(message.id)
        setNewTitle(message.title)
        setNewDescription(message.description)
    }

    const confirmDelete = (id) => {
        if (window.confirm("¿Estas seguro de eliminar este mensaje?")) {
            deleteMessage(id)
        }
    }

    const deleteMessage = async(id) => {
        try {
            await djangoAPI.delete(`messages/messages-templates/${id}/`)
            getMessages()
            toast.success("Mensaje eliminado")
        } catch (error) {
            console.log(error)
            toast.error("Error al eliminar el mensaje")
        }
    }

    const updateMessage = async(id) => {
        try {
            const response = await djangoAPI.put(`messages/messages-templates/${id}/`, {
                title: newTitle,
                description: newDescription,
            })
            toast.success("Mensaje actualizado")
            getMessages()
            setSelectedMessage(null)
        } catch (error) {
            console.log(error)
            toast.error("Error al actualizar el mensaje")
        }
    }

    useEffect(() => {
        getMessages()
    },[])

    return(
        <div>
            {messageTemplate.map((message) => (
                <div key={message.id} className="bg-white m-3 p-3 max-w-auto rounded relative">
                    {selectedMessage === message.id ? (
                        <form onSubmit={(e) => {e.preventDefault(); updateMessage(message.id)}}>
                            <input className="p-2 border border-gray-400 rounded m-1" type="text" value={newTitle} onChange={(e) => setNewTitle(e.target.value)} />
                            <textarea className="p-2 border border-gray-400 rounded m-1" value={newDescription} onChange={(e) => setNewDescription(e.target.value)}></textarea>
                            <button type="submit" className="bg-[#1F3361] text-white font-bold p-2 rounded cursor-pointer">Actualizar</button>
                        </form>
                    ) : (
                        <>
                            <h2 className="text-[#1F3361] font-bold border-b border-dashed"> {message.title} </h2>
                            <p className="p-2"> {message.description}</p>
                            <aside className="flex absolute bottom-0 right-0" >
                                <EditAltIcon className="text-2xl m-2 cursor-pointer" onClick={() => startEditMessage(message)}/>    
                                <TrashIcon className="text-2xl m-2 hover:text-red-500 cursor-pointer" onClick={() => confirmDelete(message.id)} />
                            </aside>
                        </>
                    )}

                </div>
            ))}
        </div> 
    )

}
 