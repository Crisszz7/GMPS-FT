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
                <div className="w-full h-full grid grid-cols-2">
                    {messageAsesor.map((message) => (
                        <div key={message.id} className="bg-white m-3 p-3 max-w-auto  rounded shadow-lg shadow-gray-200 relative">
                            <h2 className="text-[#1F3361] font-bold border-b border-dashed"> {message.ask} </h2>
                            <p className="p-3"> {message.answer}</p>
                            <aside className="flex absolute bottom-0 right-0" onClick={() => confirmDelete(message.id)}>
                                <EditAltIcon className="text-2xl m-2 cursor-pointer" />    
                                <TrashIcon className="text-2xl m-2 hover:text-red-500 cursor-pointer" />
                            </aside>
                        </div>
                    ))}
                </div>
                
            </div>

        </div>
        )
}