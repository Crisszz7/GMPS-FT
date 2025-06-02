import {Link, useNavigate} from 'react-router-dom';
import { useAdmin } from '../context/UserContext.jsx';
import { 
    SendAlt2Icon, 
    BlocksIcon, 
    DashboardIcon, 
    ArrowOutLeftSquareHalfIcon,
    WhatsappIcon, 
    UserSquareIcon 
} from '../icons/index.jsx';
import sinFondo from "../assets/imgs/sinFondo.png"
import { useState } from 'react';

export const NavbarComponent = () =>{
    const navigate = useNavigate()
    const {logout, user} = useAdmin()   

    const handelLogout = () => {
        logout()
    }

    const userLinks = [
        { id:1,  "path": "/dashboard-user", "icon" : <DashboardIcon />, "text" : "Dashboard"   },
        { id:2,  "path": "/applicants-user", "icon" : <UserSquareIcon />, "text" : "Aplicantes"  },
        { id:3, "path": "/messages-template-user", "icon" : <WhatsappIcon />, "text" : "WhatsApp" }
    ]

    const userAdminLinks = [
        { id:1,  "path": "/dashboard", "icon" : <DashboardIcon />,  },
        { id:2,  "path": "/messages", "icon" : <SendAlt2Icon />, }, 
        { id:3,  "path": "/sedes", "icon" : <BlocksIcon />,  }
    ]

    return (
        <>
            {/* Navbar container Administer */}
            <div className='w-auto h-dvh bg-white p-1 sticky top-0 border-r-2 border-gray-200  '>
                <div className=' w-full h-[95%] relative '>
                    <ul className=' text-2xl p-1 '>
                        {user.isLogged && (
                            <>
                            <img src={sinFondo} alt="" width={40} className='m-auto bg-[#1F3361] rounded-full '/>
                                {(user.role == "admin" ? userAdminLinks : userLinks).map((page) => (
                                    <li key={page.id}>
                                        <Link to={page.path} className={`flex p-2 shadow-sm shadow-blue-100 m-3 border-gray-500 rounded-md hover:scale-105 
                                            transition-all duration-300 hover:bg-[#1F3361] hover:text-white`}>
                                            {page.icon}
                                        </Link>
                                    </li>
                                ))}
                            </>
                        )}
                    </ul>
                    <button onClick={handelLogout} className=' shadow-sm w-full shadow-blue-200  absolute bottom-10 p-2 montserrat
                        rounded-md  hover:text-red-600 hover:cursor-pointer'>
                        <ArrowOutLeftSquareHalfIcon className='text-2xl m-auto' />
                    </button>
                </div>
            </div>
        </>
    )
}


export default NavbarComponent;