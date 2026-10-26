
import Chart from "chart.js/auto";

const dataElement = document.getElementById("task-chart-data");
const canvas = document.getElementById("taskChart");

if (dataElement && canvas) {
    const taskData = JSON.parse(dataElement.textContent);

    new Chart(canvas, {
        type: "doughnut",
        data: {
            labels: taskData.labels,
            datasets: [
                {
                    data: taskData.data,
                    backgroundColor: [
                        "#94A3B8", // To Do
                        "#C86446", // In Progress
                        "#2B7A78", // Completed
                    ],
                    borderWidth: 0,
                    hoverOffset: 5,
                },
            ],
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
                tooltip: {
                    callbacks: {
                        label(context) {
                            return ` ${context.label}: ${context.raw}`;
                        },
                    },
                },
            },
        },
    });
}
