import { use, useEffect, useState } from "react";
import {djangoAPI} from "../api/axios.jsx";
import { set, useForm } from "react-hook-form";
import { NavbarComponent } from "../components/NavbarComponent.jsx";
import { XIcon, AlertTriangleIcon,  SendAlt2Icon, FileDetailIcon, UserCheckIcon, CommunityIcon , DiscussionIcon, PlusIcon, UserXIcon} from "../icons/index.jsx";
import { toast }from 'react-hot-toast';
import { MessageTemplate } from "../components/MessageComponent.jsx"; 
import { useMessage } from "../context/MessageContext.jsx";
import { useAdmin } from "../context/UserContext.jsx";

export const MessagesWhatsapp = () => {
    const {  register, handleSubmit, setValue, formState : {errors}, reset } = useForm();
    const [ handleModal, sethandleModal] = useState(false)
    const { getMessages, messageTemplate } = useMessage()
    const { user } = useAdmin()
    const [file, setFile] = useState([])
    const [disable, setDisable] = useState(false)
    const [ approvedApplicant, setApprovedApplicant ] = useState(true)
    const [newDescription, setNewDescription] = useState("")
    const [ approvedMessage, setApprovedMessage ] = useState([])
    
    const createMessageTemplate = async(data) => {
        console.log(data)
        try {
            const response = await djangoAPI.post("messages/messages-templates/" , {
                title : data.title,
                description: data.description,
            })
            toast.success("Mensaje creado con exito" )
            getMessages()
        } catch (error) {
            console.error(error)
            toast.error("No se pudo crear el mensaje")
        }
    }

    const approvedHandleSumbit = async(data) => {
        let message = null;
        console.log( data)
        console.log("messageTemplate:", messageTemplate);


    
        // Elegir qué mensaje editar según el título enviado desde el formulario
        if (data.title.includes("Mensaje No Aprobados")) {
            message = messageTemplate.find(m => m.title.includes("Mensaje No Aprobados"));
        } else if (data.title.includes("Mensaje Aprobados")) {
            message = messageTemplate.find(m => m.title.includes("Mensaje Aprobados"));
        }
    
        if (message && message.id){
            try {
                await djangoAPI.put(`messages/messages-templates/${message.id}/`, {
                    title : data.title,
                    description : data.description
                })
                toast.success("Se guardó el mensaje")
                setNewDescription(message.description)
                getMessages()
            } catch (error) {
                console.error(error)
            }
        } else {
            // Si no existía, lo crea
            createMessageTemplate(data)
        }
    }
    

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

    useEffect(() => {
        setValue("title", approvedApplicant ? "Mensaje Aprobados" : "Mensaje No Aprobados");
      }, [approvedApplicant, setValue]);

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
            <div className=" h-auto p-4 flex flex-row w-full bg-[#f3f4f6]">
                
                {/* Campo para enviar el mensaje y botones relacionados */}
                <div className=" basis-2/3 ">
                <h1 className="text-[#1F3361] font-bold text-4xl mb-2 flex items-center"> Campaña de mensajes  </h1>
                <p className="text-gray-500 mb-2">Envia un mensaje a varios usuarios de Whatsapp según tu necesidad</p>
                    <form onSubmit={saveFileExcel} className="flex flex-col bg-white  p-3 rounded-lg mb-4">
                        <div className="flex  items-center border-b border-gray-300 p-2 font-semibold">
                            <aside className="bg-[#FFD40A] text-black max-w-max  p-2 font-bold rounded-full">1</aside>
                            <h2 className="m-2"> Elige tus destinatarios </h2>
                            <CommunityIcon />
                        </div>
                            {!disable ? (
                                <>
                                <span className="flex font-bold text-[#1F3361] text-sm p-1">Sube tu archivo de excel <FileDetailIcon className=" p-1  "/> </span>     
                                <input type="file" name="file" accept=".xlsx" className="border-dashed border border-gray-400 font-bold p-2  italic text-xs m-2 text-gray-500 cursor-pointer" />  
                                <button type="submit"  className=" p-2 rounded-lg font-semibold cursor-pointer border w-auto text-sm hover:bg-green-500  max-w-max hover:scale-105 transition-all duration-300" > Subir </button>
                                </>
                            ) : (
                                <>
                                <span className="flex font-bold text-[#1F3361] text-sm p-1">Excel cargado <FileDetailIcon className=" p-1  "/> </span>
                                <button type="submit"  className=" p-2 rounded font-semibold cursor-pointer bg-gray-300 text-gray-900 max-w-max text-sm" onClick={() => confirmDelete(fileID)}> Elimina el Excel </button>

                                </>
                            )}
                        </form>          
                    <div className="flex w-full">
                        <form action="" className="bg-white p-3 w-full rounded-lg">
                        <div className="flex  items-center border-b border-gray-300 p-2 font-semibold">
                            <aside className="bg-[#FFD40A] text-black max-w-max  p-2 font-bold rounded-full">2</aside>
                            <h2 className="m-2"> Redacta el mensaje  </h2>
                            <DiscussionIcon />
                        </div>
                            <textarea  className="bg-gray-50 p-2 border-dashed border-2 border-gray-300 w-full min-w-full min-h-32 rounded mt-3"
                                name="" id="" placeholder="Redacta el mensaje aqui!">
                            </textarea>
                            <div>
                                <button className="border-black border flex p-2 rounded-lg m-3 font-semibold cursor-pointer hover:bg-[#FFD40A] hover:scale-105 transition-all duration-300 hover:cursor-pointer"> <SendAlt2Icon className=" p-1  "/> Enviar Mensaje </button>
                            </div>
                        </form>
                    </div>
                            
                    
                    <div className="">
                    <span className="block text-center p-3 font-bold text-gray-700"> Predeterminados </span> 
                    <div className="flex p-2 justify-evenly">
                        <button className="bg-white border border-gray-400 p-2 rounded cursor-pointer" onClick={() => setApprovedApplicant(true)} > Aprobados </button>  
                        <button className="bg-white border border-gray-400 p-2 rounded cursor-pointer" onClick={() => setApprovedApplicant(false)}> No aprobados </button>
                    </div>
                        <div>
                        {approvedApplicant ? ( 
                            <form onSubmit={handleSubmit(approvedHandleSumbit)} className="bg-white p-3 w-full rounded-lg">
                                <div className="flex  items-center border-b border-gray-300 p-2 font-semibold">
                                    <aside className="bg-[#1F3361] text-white max-w-max  p-2 font-bold rounded-full">3</aside>
                                    <h2 className="m-2"> Para aplicantes aprobados  </h2>
                                    <UserCheckIcon />
                                </div>
                                <input {...register("title")} type="hidden" name="title"   defaultValue={"Mensaje Aprobados"} />
                                <textarea {...register("description")}  className="bg-gray-50 p-2 border-dashed border-2 border-gray-300 w-full min-w-full min-h-32 rounded mt-3"
                                name="description" id="" placeholder="Redacta el mensaje aqui!">
                                </textarea>
                                <button className="bg-[#1F3361] text-white hover:text-black p-2 rounded-lg font-semibold cursor-pointer hover:bg-[#FFD40A] hover:scale-105 transition-all duration-300"> Guardar </button>
                            </form>
                            ) : (
                            <form onSubmit={handleSubmit(approvedHandleSumbit)}  className="bg-white p-3 w-full rounded-lg">
                                <div className="flex  items-center border-b border-gray-300 p-2 font-semibold">
                                    <aside className="bg-[#1F3361] text-white max-w-max  p-2 font-bold rounded-full">4</aside>
                                    <h2 className="m-2"> Para aplicantes No Aprobados  </h2>
                                    <UserXIcon />
                                </div>
                                <input {...register("title")} type="hidden" name="title"   defaultValue={"Mensaje No Aprobados"} placeholder="Titulo para el mensaje "/>
                                <textarea {...register("description", {required: "Por favor completa este campo"})} className="bg-gray-50 p-2 border-dashed border-2 border-gray-300 w-full  min-w-full min-h-32 rounded mt-3"
                                name={"description"} id="" placeholder="Redacta el mensaje aqui!">
                                </textarea>
                                <button className="bg-[#1F3361] text-white hover:text-black p-2 rounded-lg font-semibold cursor-pointer hover:bg-[#FFD40A] hover:scale-105 transition-all duration-300"> Guardar </button>
                            </form>
                            ) }
                        </div>                    
                    </div>
                </div>




                {/* Caja de las plantillas de mensajes */}
                <div className="max-w-96 max-h-[60rem] overflow-auto basis-1/3 p-2  ">
                    <div className="flex  items-center p-2 bg-white justify-between rounded-lg sticky top-0 z-10">
                    <h3 className="text-[#1F3361] font-semibold "> Plantillas </h3>
                        <button className="text-[#1F3361] bg-blue-50 flex p-2 rounded-full items-center  cursor-pointer text-xs " onClick={() => 
                            sethandleModal(true)
                            }> <PlusIcon className="text-[#1F3361] p-1"/>  Nuevo Mensaje 
                        </button>  
                    </div>
                    <MessageTemplate/>

                </div>
                





                {/* Modal crear plantilla mensaje*/}
                {handleModal && 
                <div className="w-full h-full bg-[#0000005e] z-20 fixed top-0 left-0 flex justify-center items-center">
                    <form onSubmit={handleSubmit(createMessageTemplate)} className="bg-white relative w-1/2 max-h-full flex flex-col p-3 rounded">
                        <XIcon className="absolute top-3 right-3 bg-gray-200 rounded-full p-1 cursor-pointer" onClick={() => {
                            sethandleModal(false);
                            reset({
                                title: "",
                                description: ""
                            });
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

        </div>

    )

}


