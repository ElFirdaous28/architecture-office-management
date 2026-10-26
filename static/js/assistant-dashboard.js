
import Chart from "chart.js/auto";

const dataElement = document.getElementById("project-chart-data");
const canvas = document.getElementById("projectChart");

if (dataElement && canvas) {
    const projectData = JSON.parse(dataElement.textContent);

    new Chart(canvas, {
        type: "doughnut",
        data: {
            labels: projectData.labels,
            datasets: [{
                data: projectData.data,
                backgroundColor: ["#94A3B8", "#C86446", "#2B7A78"],
                borderWidth: 0,
                hoverOffset: 5,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            rotation: -90,
            circumference: 180,
            cutout: "70%",
            plugins: {
                legend: {
                    position: "bottom",
                },
            },
        },
    });
}
