import { useEffect, useState } from "react";
import {djangoAPI} from "../api/axios.jsx";
import { useForm } from "react-hook-form";
import { NavbarComponent } from "../components/NavbarComponent.jsx";
import { XIcon, AlertTriangleIcon,  SendAlt2Icon, FileDetailIcon, TrashIcon } from "../icons/index.jsx";
import { toast }from 'react-hot-toast';
import { MessageTemplate } from "../components/MessageComponent.jsx"; 
import { useMessage } from "../context/MessageContext.jsx";
import { useAdmin } from "../context/UserContext.jsx";
import { data } from "react-router-dom";

export const MessagesWhatsapp = () => {
    const {  register, handleSubmit, formState : {errors} } = useForm();
    const [ handleModal, sethandleModal] = useState(false)
    const { getMessages } = useMessage()
    const { user } = useAdmin()
    const [file, setFile] = useState([])
    const [disable, setDisable] = useState(false)

    const saveFileExcel = async(data) => {
        data.preventDefault()
        const formData = new FormData();
        formData.append("file", data.target.file.files[0]); 

        try {
            const response = await djangoAPI.post("messages/upload-excel/", formData)
            setDisable(true)
            toast.success("Archivo guardado con exito")
            getFileExcel()
        } catch (error) {
            toast.error("No se pudo guardar el excel")
        }
    }

    const getFileExcel = async () => {
        try {
            const response = await djangoAPI.get("messages/upload-excel/");
            setFile(response.data);
            if (response.data.length > 0) {
                setDisable(true);
            } else {
                setDisable(false);
            }
        } catch (error) {
            toast.error("No se pudo obtener el excel: " + error);
        }
    };

    const confirmDelete = (id) => {
        if (window.confirm("¿Estas seguro de eliminar este archivo?")) {
            deleteFileExcel(id)
        }
    }

    const deleteFileExcel = async(id) => {
        try {
            const response = await djangoAPI.delete(`messages/upload-excel/${id}/`)
            toast.success("Archivo eliminado con exito")
            getFileExcel()
        } catch (error) {
            toast.error("No se pudo eliminar el excel: " + error)
        }
    }

    const createMessageTemplate = async(data) => {
        try {
            const response = await djangoAPI.post("messages/messages-templates/" , {
                title : data.title,
                description: data.description,
            })
            toast.success("Mensaje creado con exito" )
            getMessages()
        } catch (error) {
            toast.error("No se pudo crear el mensaje")
        }
    }

    useEffect(() => {
        getMessages()
        getFileExcel()
    }, [])

    let fileID = ""

    if (file.length > 0) {
        fileID = file[0].id
    }

    return (
        <div className="flex montserrat">
            <NavbarComponent/>
            {/* Contenedor global */}
            <div className=" h-dvh p-4 flex flex-row w-full bg-[#f3f4f6]">
                
                {/* Campo para enviar el mensaje y botones relacionados */}
                <div className=" basis-2/3 ">
                <h1 className="text-[#1F3361] font-bold text-4xl mb-2"> Mensajes </h1>
                <p className="text-gray-700 ">Envia un mensaje a varios usuarios de whatsapp</p>
                    <form className="flex flex-col bg-white shadow shadow-gray-400 p-3 rounded-lg">
                        <label htmlFor="" className="font-bold m-2">
                            MENSAJE DE MARKETING 
                        </label>  
                        <textarea 
                        className="bg-gray-50 p-2 border border-gray-600 w-full ropunded min-w-full min-h-48 rounded"
                            name="" id="" placeholder="Escribe o suelta el mensaje aqui !"
                            >
                        </textarea>
                        <div>
                            <button className="border-black border flex p-2 rounded-lg m-3 font-semibold cursor-pointer hover:bg-[#FFD40A] hover:scale-105 transition-all duration-300 hover:cursor-pointer"> <SendAlt2Icon className=" p-1  "/> Enviar Mensaje </button>
                        </div>
                    </form>
                    <div className="flex p-2 ">
                        <button className="text-[#1F3361] bg-blue-300 flex p-3 rounded font-semibold cursor-pointer" onClick={() => 
                        sethandleModal(true)
                        }> Crear mensaje </button>                        
                    </div>
                    <div className="flex w-full">
                        <form onSubmit={saveFileExcel} className="flex flex-col bg-white max-w-auto p-2 border border-gray-400 rounded ">
                            {!disable ? (
                                <>
                                <span className="flex font-bold text-[#1F3361] text-sm">Sube tu archivo de excel <FileDetailIcon className=" p-1  "/> </span>     
                                <input type="file" name="file" accept=".xlsx" className="bg-neutral-200 font-bold p-2  italic text-xs m-2 cursor-pointer" />  
                                <button type="submit"  className=" p-2 rounded font-semibold cursor-pointer bg-green-300 text-green-900 w-auto text-sm" > Subir </button>
                                </>
                            ) : (
                                <>
                                <span className="flex font-bold text-[#1F3361] text-sm">Excel cargado <FileDetailIcon className=" p-1  "/> </span>
                                <button type="submit"  className=" p-2 rounded font-semibold cursor-pointer bg-gray-300 text-gray-900 w-auto text-sm" onClick={() => confirmDelete(fileID)}> Elimina el Excel </button>
                                </>
                            )}
                        </form>

                        {/* <div className="flex flex-wrap p-2 overflow-y-auto h-32 justify-center">
                            {file.map(element => (
                                element.data.map((to, i) => (
                                    <div key={i} className="m-2">
                                        <span className="text-[#1F3361] font-bold shadow-sm rounded-full p-2 "> {to.Celular} </span>
                                    </div>
                                ))
                            ))}
                        </div> */}

                </div>
                </div>



                {/* Caja de las plantillas de mensajes */}
                <div className="max-w-96 max-h-full overflow-auto basis-1/3 p-2">
                <h3 className="text-[#1F3361] font-semibold"> Plantillas </h3>
                    <MessageTemplate/>
                </div>
                
            </div>





            {/* Modal crear plantilla mensaje*/}
            {handleModal && 
            <div className="w-dvw h-dvh bg-[#0000005e] absolute top-0 left-0 flex justify-center items-center">
                <form onSubmit={handleSubmit(createMessageTemplate)} className="bg-white relative w-1/2 max-h-full flex flex-col p-3 rounded">
                    <XIcon className="absolute top-3 right-3 bg-gray-200 rounded-full p-1 cursor-pointer" onClick={() => {
                        sethandleModal(false)
                    }} />
                    <h3 className="text-[#1F3361] font-bold"> Mensaje de Marketing </h3>
                    <label htmlFor="" className="font-bold m-1"> Titulo </label>
                        <input 
                        className=" border border-gray-400 rounded w-11/12 p-1 m-auto"
                        {...register("title", {required:" Por favor completa esta campo"})}
                        type="text" name="title" id="" placeholder="Titulo para el mensaje "/>
                        {errors.title && <span className="text-orange-600 p-1 m-1 flex w-full"><AlertTriangleIcon/> {errors.title.message}</span> }
                    <label htmlFor=""  className="font-bold m-1"> Contenido </label>
                        <textarea name="description" id="" placeholder="Contenido del mensaje"
                        className=" border border-gray-400 rounded w-11/12 p-1 min-h-48 mb-3 m-auto "
                        {...register("description", {required:" Por favor completa este campo"})}
                        >
                        </textarea>
                        {errors.description && <span  className="text-orange-600  p-1 m-1 flex w-full "><AlertTriangleIcon/> {errors.description.message}</span> }
                    <button className="text-white p-2 w-1/2 m-auto font-bold bg-[#1F3361] rounded cursor-pointer "> Crear </button>
                </form>
            </div>
            }
            {/* Fin modal */}


        </div>
    )

}