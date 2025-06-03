import { useEffect } from "react";
import { NavbarComponent } from "../components/NavbarComponent";
import { djangoAPI } from "../api/axios.jsx";
import { useState } from "react";
import sedesImg from "../assets/imgs/sedesImg.jpg";
import { useAdmin } from "../context/UserContext.jsx";
import { InfoCircleIcon } from "../icons/index.jsx";
import { useForm } from "react-hook-form";
import { toast } from "react-hot-toast";

export const Sedes = () => {

    const {  register, handleSubmit, formState : {errors} } = useForm();
    const [users, setUsers] = useState([])
    const [sedes, setSedes] = useState([]) 
    
    const getSedes = async () => {
        try {
            const response = await djangoAPI.get("/users/place-trigal-users/")
            setSedes(response.data)
        } catch (error) {
            console.log(error)
        }
    }

    const getUsers = async () => {
        try {
            const response = await djangoAPI.get("/users/administer-users/")
            setUsers(response.data)
        } catch (error) {
            console.log(error)
        }
    }

    useEffect(() => {
        getSedes()
        getUsers()
    }, [])



    const onSubmit = async (data) => {
        try {
            const response = await djangoAPI.post("/users/administer-users/", {
                username: data.username,
                password: data.password,
                email: data.email,
                place_to_administer: data.place_to_administer
            })
            toast.success("Se registro el usuario")
        } catch (error) {
            console.error("Error al registrar sede:", error.response?.data || error.message);
            toast.error("Error al registrar el usuario")
        }
    }

    return (
        <div className="w-full h-full flex bg-[#f2f2f2] montserrat">
            <NavbarComponent />

            <div className="basis-full p-3">
            <h1 className="text-4xl font-bold mb-4 text-[#1F3361] p-2"> Sedes Trigal </h1>
                <div className="w-full p-4 flex gap-4 ">
                    {sedes.map(sede => (
                        <>
                        {sede.name_place_trigal == "Trigal" ? (
                            null
                        ) : 
                        <div key={sede.id} className="bg-white p-2 max-h-max hover:scale-105 transition-all duration-300">
                            <img src={sedesImg} alt="" className="object-cover w-full rounded-lg  "/>
                            <p className="font-bold "> {sede.name_place_trigal} </p>
                            <p> {users.map(user => user.place_to_administer == sede.id ? user.username : null)} </p>
                            <p> {users.map(user => user.place_to_administer == sede.id ? user.email : null)} </p>
                        </div>
                        }
                        </>
                        
                    ))}
                </div>
                <div>
                    <hr />
                     <p className="text-center"> Formulario de registro de sede </p>
                     <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col w-1/2 gap-2 bg-white p-2 m-auto"> 
                        <input className="p-2 border border-gray-400 rounded m-1"
                        {...register("username", {required: "El nombre de usuario es obligatorio *"})} 
                        type="text" name="username" placeholder="username" />
                        <span className="flex text-gray-600 text-sm italic p-2"> <InfoCircleIcon/> El nombre de usuario debe ir sin espacios</span>
                        {errors.username && <span className="text-red-500"> {errors.username.message} </span>}
                        <input className="p-2 border border-gray-400 rounded m-1"
                        {...register("password", {required: "La contraseña es obligatoria *"})} 
                        type="text" name="password" placeholder="password" />
                        {errors.password && <span className="text-red-500"> {errors.password.message} </span>}
                        <input className="p-2 border border-gray-400 rounded m-1"
                        {...register("email", {required: "El correo es obligatorio *"})} 
                        type="text" name="email" placeholder="email" />
                        {errors.email && <span className="text-red-500"> {errors.email.message} </span>}
                        <select className="p-2 border border-gray-400 rounded m-1"
                        {...register("place_to_administer", {required: "La sede es obligatoria *"})} 
                        name="place_to_administer" id="">
                            {sedes.map((sede, index) => (
                                <option key={index} value={sede.id}> {sede.name_place_trigal} </option>
                            ))}
                        </select>
                        {errors.place_to_administer && <span className="text-red-500"> {errors.place_to_administer.message} </span>}
                        <button type="submit" className="bg-[#1F3361] text-white font-bold w-1/2 rounded m-auto p-3 cursor-pointer"> registrar </button>
                     </form>
                </div>
            </div>

        </div>
    )
}   