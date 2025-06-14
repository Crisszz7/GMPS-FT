import { djangoAPI } from "../api/axios.jsx";
import { useForm } from "react-hook-form";
import { useNavigate } from 'react-router-dom';
import { toast }from 'react-hot-toast';
import { use, useEffect, useState } from "react";
import { useAdmin} from "../context/UserContext.jsx"
import  logo_trigal  from "../assets/imgs/logo_trigal.png";
import { KeyIcon, UserIcon } from "../icons/index.jsx";

export const Login = () => {

    const {  register, handleSubmit, formState : {errors} } = useForm();
    const [submit, setSubmit] = useState("Iniciar Sesión")
    const { setUser } = useAdmin()

    let navigate = useNavigate()

    const onSubmit = async (data) =>{  //Funcion asincrona para esperar la respuesta de API en django 
        setSubmit("Entrando....");
        try {
            const response = await djangoAPI.post("/users/login/",{
                username : data.username,
                password : data.password,
            },
         );

        sessionStorage.setItem("token", response.data.token)
        sessionStorage.setItem("user", JSON.stringify(response.data.user))

        const user = JSON.parse(sessionStorage.getItem("user"))

        console.log(user)

        setUser({
            username: user.username ,
            isLogged : true,
            role: (user.username == "admin" ? "admin" : "user"),
            sede: user.sede,
        })

        console.log(response)

        navigate(response.data.user.sede == "Trigal" ? "/dashboard" : "/dashboard-user")
        } catch (error) {
            console.error(error)
            toast.error("Credenciales invalidas.")
        }finally{
            setSubmit("Iniciar Sesión")
        }
    } 


    return(
        <div className=" w-full h-dvh flex flex-row relative">
            <div className="flex flex-row w-4/5 h-4/5 m-auto shadow-sm shadow-gray-500  ">
            <div className="bg-white basis-2/3 h-full border  border-gray-300 montserrat flex flex-col ">
                <div className="w-11/12 h-11/12 m-auto flex flex-col justify-center items-center">
                    <h1 className="text-6xl text-[#1F3361] m-3 "> <strong>GM</strong><span className="text-stroke text-white" >PS </span> </h1>
                    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col justify-center p-2 items-center w-10/12 h-auto ">
                        <label for="username" htmlFor="username" className=" w-full block p-3">
                        <span className="flex flex-row items-center gap-2">
                            <UserIcon />
                            Usuario *
                           </span>
                        </label>
                        <input 
                        {...register("username", {required:"El nombre de usuario es obligatorio *"})}  
                        type="text" 
                        name="username"  
                        placeholder="Nombre de usuario" 
                        className=" border-b-2 border-blue-950 p-3 rounded-xs w-full m-1 montserrat" />
                        {errors.username && <span className="text-red-500 w-full rounded-sm font-bold">{errors.username.message}</span> }
                        <label htmlFor="" className=" w-full block p-3">
                           <span className="flex flex-row items-center gap-2">
                            <KeyIcon />
                            Contraseña *
                           </span>
                        </label>
                        <input  {...register("password", {required:"La contraseña es obligatoria *"})} type="password"
                         name="password" placeholder="Contraseña" className="border-b-2 border-blue-950 p-3 rounded-xs w-full m-1 montserrat" />
                        {errors.password && <span className="text-red-500 rounded-sm font-bold w-full">{errors.password.message} </span>  }
                        <button type="submit" className="rounded bg-[#1f3361ef] text-white font-bold p-3 m-3 cursor-pointer hover:text-[#1F3361] hover:scale-105 hover:border-[0.1rem] hover:bg-white transition-all duration-300" >{submit}</button>
                    </form>
                </div>
            </div>
            <div className="basis-2/3 bg-login">
                <div className=" bg-[#1f336181] h-full w-full flex justify-center items-center" >
                    <div className="w-4/5 h-2/4 flex flex-col  justify-center items-center">
                        <img src={logo_trigal} alt="logo_trigal"  className=" object-cover w-full"/>
                        <div className="text-white text-center montserrat w-11/12 m-auto p-3 text-2xl">
                            <p>
                                CULTIVAMOS 
                                <strong> FLORES Y SUEÑOS</strong> CON RESPETO 
                                <strong> ENTREGANDO BELLEZA AL MUNDO</strong>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
            </div>

        </div>
    )
}


    // const handleChangue = (e) => { //funcion que resive (e) que es el obejto del evento (input)
    //     const { name, value } = e.target; // accede al name del input(name="") y value al valor(value="") 
    //     setCredentials((prev) => ({ //actualizar el estado de los inputs cuando el usuario escribe
    //       ...prev, //prev es el estado anterior del input, mantiene el valor intacto
    //       [name]: value, //actualizar el campo correspondiente (name="passsword")
    //     }));
    // }