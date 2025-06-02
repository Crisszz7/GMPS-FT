import { use, useEffect, useState } from "react";
import toast from "react-hot-toast";
import { NavbarComponent } from "../components/NavbarComponent"
import login from '../assets/imgs/login.png';
import { CogIcon, InfoCircleIcon } from "../icons/index";

export function DashboardAdmin (){

    let user = JSON.parse(sessionStorage.getItem("user"))

    return(
        <div className="w-full h-full flex flex-row bg-[#f2f2f2] montserrat ">
            <NavbarComponent/>
            <div className="basis-full h-auto bg-[#f3f4f6] p-2">
                <div className="w-full h-84 ">
                <div   style={{
                        backgroundImage: `url(${login})`,
                        backgroundSize: 'cover',
                        objectFit: 'cover',
                        backgroundPosition: 'center',
                        backgroundRepeat: 'no-repeat',}} 
                    className="  w-11/12 h-48 m-auto rounded-sm relative flex justify-center items-center ">
                <div className="bg-white w-11/12  h-full rounded-sm absolute -bottom-20 flex items-center p-3 ">
                    <img src="../src/assets/imgs/Billy 3D[1].png" alt="logo-trigal" className="w-42 rounded-2xl object-cover " />
                    <div className="flex flex-col justify-around h-1/2 ml-3">
                        <h1 className="text-2xl font-bold">Bienvenido de nuevo {user.username}</h1>
                        <p className="text-sm text-gray-500"> Panel administrativo de GMPS </p>
                    </div>
                    {/* Icons options */}
                    <div className="flex  justify-around h-auto p-2 w-auto ml-3 absolute right-0 top-0 ">
                        <InfoCircleIcon className="text-2xl m-2" />
                        <CogIcon className="text-2xl m-2  rounded-full " />
                    </div>
                </div>
                </div>
                </div>
                                {/* Contenedor de la dashboard y datos */}
                <div className="">
                    <div className="w-11/12 h-32 rounded-sm m-auto p-2 ">
                        <h2 className="text-5xl font-bold text-[#1F3361] ml-4"> Dashboard </h2>

                    </div>
                </div>
            </div>
        </div>
    )
}

