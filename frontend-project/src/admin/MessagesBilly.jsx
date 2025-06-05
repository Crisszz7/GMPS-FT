import { useNavigate } from "react-router-dom"; 
import { NavbarComponent } from "../components/NavbarComponent.jsx";
import { useState, useEffect } from "react";
import { djangoAPI } from "../api/axios.jsx";
import { useMessage } from "../context/MessageContext.jsx";
import billyJumping from "../assets/imgs/billyJumping.png";
import { SendAlt2Icon, EditAltIcon, TrashIcon } from "../icons/index";
import toast from "react-hot-toast";

export const MessagesBilly = () => {
    const { getMessages, messageAsesor } = useMessage()
    const [editMessage, setEditMessage] = useState(null)
    const [newMessageAsk, setNewMessageAsk] = useState("")
    const [newMessageAnswer, setNewMessageAnswer] = useState("")

    useEffect(() => {
        getMessages()
    }, [])

    const createMessage = async(data) => {
        data.preventDefault()
        console.log(data.target.ask.value)
        try {
            const response = await djangoAPI.post("messages/messages-ai/", 
                {
                'ask': data.target.ask.value,
                'answer': data.target.answer.value
            })   
            data.target.reset()
            getMessages()
            toast.success("Mensaje creado")
        } catch (error) {
            console.log(error)
            toast.error("Error al crear el mensaje")
        }
    }

    const confirmDelete = (id) => {
        if (window.confirm("¿Estas seguro de eliminar este mensaje?")) {
            deleteMessage(id)
        }
    }

    const deleteMessage = async(id) => {
        try {
            const response = await djangoAPI.delete(`messages/messages-ai/${id}/`, )

            getMessages()
            toast.success("Mensaje eliminado")
        } catch (error) {
            console.log(error)
            toast.error("Error al eliminar el mensaje")
        }
    }

    const startEditMessage = (message) => {
        setEditMessage(message.id)
        setNewMessageAsk(message.ask)
        setNewMessageAnswer(message.answer)
    }

    const SaveEditMessage = async(id) => {
        try {
            await djangoAPI.put(`messages/messages-ai/${id}/`, {
                'ask': newMessageAsk,
                'answer': newMessageAnswer
            })
            getMessages()
            toast.success("Mensaje editado")
            setEditMessage(null)
            setNewMessageAsk("")
            setNewMessageAnswer("")
        } catch (error) {
            console.log(error)
            toast.error("Error al editar el mensaje")
        }
    }

    return(
        <div className="w-full h-full flex flex-row  bg-[#f3f4f6] montserrat">
            <NavbarComponent />
            <div className="w-full h-full p-4 ">
                <h1 className="text-4xl font-bold mb-4 text-[#1F3361]"> Respuestas de Billy  </h1>
                <div className="w-10/12 h-auto flex  bg-gradient-to-r from-transparent to-white p-2 m-auto rounded-xl">
                    <img src={billyJumping} alt="" className=" w-1/4 m-3 object-contain"/>
                        <form onSubmit={createMessage} className="flex flex-col gap-2 w-full m-3">
                            <h2 className="text-sm text-[#1F3361] font-bold mt-3 mb-5"> RESPUESTAS PARA EL USUARIO </h2>
                            <label htmlFor="ask"  className="font-bold">Pregunta</label>
                            <input type="text" name="ask" placeholder="Pregunta" className="p-2 border border-gray-400 rounded "/>
                            <label htmlFor="answer" className="font-bold">Respuesta</label>
                            <textarea name="answer" id="answer" placeholder="Respuesta" className="p-2 min-h-40 max-h-96 bg-[#f3f4f6] border-dashed border-2 border-gray-400 rounded-xl"></textarea>
                            <button type="submit" className=" flex p-2 border w-1/2 font-semibold cursor-pointer rounded-lg hover:bg-[#FFD40A] hover:scale-105 transition-all duration-300"><SendAlt2Icon className=" p-1  "/>
                            Crear Mensaje</button>
                        </form>
                </div>
                <h3 className="text-[#1F3361] text-3xl text-center font-bold mt-3 mb-5"> Respuestas Guardadas </h3>
                <div className="w-full h-full grid grid-cols-2 gap-4">
                    {messageAsesor.map((message) => (
                        <>
                            <div key={message.id} className="bg-white  border border-gray-400 rounded p-2">
                                {editMessage === message.id ? (
                                    <form onSubmit={(e) =>  {e.preventDefault() 
                                    SaveEditMessage(message.id) } } className="flex flex-col gap-2">
                                        <input type="text" name="ask" value={newMessageAsk} className="border border-gray-400 p-2" onChange={e => setNewMessageAsk(e.target.value)} />
                                        <textarea name="answer" id="answer" value={newMessageAnswer} className="border border-gray-400 p-2" onChange={e => setNewMessageAnswer(e.target.value)} />
                                        <button type="submit" className="font-bold cursor-pointer">Guardar</button>
                                    </form>
                                ) : (
                                    <>
                                        <h3 className="bg-[#1F3361] text-white p-2 italic"> {message.ask} </h3>
                                        <p className="p-2"> - {message.answer} </p>
                                        <aside className="flex justify-end">
                                            <EditAltIcon onClick={() => startEditMessage(message)} className="cursor-pointer"/>
                                            <TrashIcon onClick={() => confirmDelete(message.id)} className="cursor-pointer hover:text-red-500"/>
                                        </aside>
                                    </>
                                )}
                            </div>
                        </>
                    ))}
                </div>
                
            </div>

        </div>
        )
}