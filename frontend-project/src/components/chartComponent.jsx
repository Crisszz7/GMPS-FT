import React, { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend,
  BarElement,
  LineElement,
  PointElement 
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';
import { djangoAPI } from '../api/axios.jsx';
import { parseISO, startOfWeek, format } from 'date-fns';
import { es } from 'date-fns/locale';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement 
);

const options = {
  responsive: true,
  plugins: {
    legend: {
      position: 'top',
      align: 'start',
    },
    title: {
      display: true,
      text: 'Aplicaciones por semana',
    },
  },
};



function parseColombianDate(dateStr) {
  const [datePart, timePart] = dateStr.split(' ');
  const [day, month, year] = datePart.split('/');
  const [hour, minute] = timePart.split(':');

  // ¡Recuerda que el mes empieza desde 0 (enero) en JS!
  return new Date(year, month - 1, day, hour, minute);
}

// Función para obtener el lunes de la semana correspondiente
function getMonday(dateString) {
  const date = parseColombianDate(dateString);
  return startOfWeek(date, { weekStartsOn: 1 }); // Lunes como inicio
}

function formatWeekLabel(mondayDate) {
  const start = format(mondayDate, "dd 'de' MMM", { locale: es });
  const sunday = new Date(mondayDate);
  sunday.setDate(sunday.getDate() + 6);
  const end = format(sunday, "dd 'de' MMM", { locale: es });

  return `Semana del ${start} al ${end}`;
}


export function MyChart() {
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    const getApplicantsData = async () => {
      try {
        const response = await djangoAPI.get("users/whatsapp-users");
        const dataDelBackend = response.data;

        const conteoSemanal = new Map();

        dataDelBackend.forEach(({ date_request }) => {
          const monday = getMonday(date_request);
          const key = monday.toISOString(); // clave única por semana
          conteoSemanal.set(key, (conteoSemanal.get(key) || 0) + 1);
        });

        // Ordenar por fecha
        const semanasOrdenadas = Array.from(conteoSemanal.keys()).sort();

        const labels = semanasOrdenadas.map(key =>
          formatWeekLabel(new Date(key))
        );
        const counts = semanasOrdenadas.map(key => conteoSemanal.get(key));

        const data = {
          labels,
          datasets: [
            {
              label: 'Aplicaciones por semana',
              data: counts,
              borderColor: '#1F3361',
              backgroundColor: '#1F3361',
            },
          ],
        };

        setChartData(data);
      } catch (error) {
        console.error("Hubo un error:", error);
      }
    };

    getApplicantsData();
  }, []);

  return chartData ? <Line options={options} data={chartData} /> : <p>Cargando...</p>;
}
