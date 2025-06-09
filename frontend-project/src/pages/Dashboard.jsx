import { useState } from "react";
import {NavbarComponent} from "../components/NavbarComponent.jsx";
import {MyChart} from "../components/chartComponent.jsx"

export const Dashboard = () => {
    
    let user = JSON.parse(sessionStorage.getItem("user"))

    return (
        <div className="w-full h-full flex flex-row montserrat ">
            <NavbarComponent />
            <div  className="w-full flex-1 bg-[#f3f4f6]">
                <header className="p-4  w-full h-auto text-[#1F3361]">
                    <h1 className=" text-2xl font-bold border-b-2 p-2" > Sede {user.sede} </h1> 
                    <p> Flores El Trigal <strong> GMPS - {user.username}</strong></p>
                </header>
                <main className="p-4 w-1/2 bg-white rounded-2xl border border-gray-300 m-2" >
                    <h2 className="text-[#1F3361] font-bold text-4xl"> Dashboard </h2>
                    <MyChart />
                </main>
            </div>
        </div>
    )
}

