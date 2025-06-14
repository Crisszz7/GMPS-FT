import axios from "axios";

export const djangoAPI = axios.create({
  baseURL: import.meta.env.VITE_REACT_APP_API_URL || "http://127.0.0.1:8000/api/",
  withCredentials: true
});

djangoAPI.interceptors.request.use(
  (peticion) => {
    const token = sessionStorage.getItem("token");
    if (token) {
      peticion.headers.Authorization = `Token ${token}`;
    }
    return peticion;
  },
  (error) => Promise.reject(error)
);



